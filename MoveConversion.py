
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rubik-style move converter with wide pivot support.

Finalized rules:
- Inputs will NOT include moves beginning with '3' (e.g., no 3Uw/Rw/Bw in input).
- Wide pivots act even without a suffix: Lw, Dw, Fw are pivots.
- Pivots convert themselves:
    * L  -> 3Rw,  Lw -> Rw
    * D  -> 3Uw,  Dw -> Uw
    * F  -> 3Bw,  Fw -> Bw
  (suffix "'" or "2" is preserved).
- After converting the pivot, apply its mapping to ALL following moves.
- Process moves left-to-right on the converted sequence (newly created L/D/F will act later when reached).
- Base-face mappings DO NOT apply to 3w moves (3Uw/3Rw/3Bw). Only their special mappings apply.
- IMPORTANT: Special mappings for 3w moves DO NOT apply when the 3w move has a '2' suffix.
  (Prevents final 3Uw2 from being changed by a late L/D/F pivot.)

Mappings (unchanged):
- L : base U→B, B→D, D→F, F→U; special 3Uw→F, 3Bw→U
- F : base U→L, L→D, D→R, R→U; special 3Rw→D, 3Uw→R
- D : base F→L, L→B, B→R, R→F; special 3Bw→D, 3Uw→R

Double-turn pivots:
- L2: U↔D, F↔B;  special 3Uw→U
- F2: U↔D, R↔L;  special 3Rw→R
- D2: F↔B, R↔L;  special 3Bw→B

Suffixes:
- Preserve each move’s own suffix (' or 2) after all conversions and mappings.

CLI:
- Run with no arguments to execute tests.
- Run with a sequence string to convert it.
- Run with `--debug "<sequence>"` to see step-by-step transformations.
"""

from typing import List, Dict, Tuple

# --------------------------
# Move representation
# --------------------------

class Move:
    def __init__(self, layer=None, base: str = '', wide: bool = False, suffix: str = ''):
        self.layer = layer      # None or 3
        self.base = base        # U,D,L,R,F,B
        self.wide = wide        # True if 'w'
        self.suffix = suffix    # '', "'", '2'

    def __str__(self) -> str:
        return f"{'3' if self.layer==3 else ''}{self.base}{'w' if self.wide else ''}{self.suffix}"


def parse_move(token: str) -> Move:
    """
    Parse a token like: U, U', U2, Uw, Rw2, L, F', etc.
    Inputs will NOT include tokens beginning with '3', but we parse defensively.
    """
    layer = None
    idx = 0

    # Optional '3' prefix (not expected in input, but supported defensively)
    if token.startswith('3'):
        layer = 3
        idx += 1

    if idx >= len(token) or token[idx] not in 'UDLRFB':
        raise ValueError(f"Invalid move: {token}")
    base = token[idx]
    idx += 1

    # Optional 'w'
    wide = False
    if idx < len(token) and token[idx] == 'w':
        wide = True
        idx += 1

    # Optional suffix "'" or "2"
    suffix = ''
    if idx < len(token):
        if token[idx:] in ("'", "2"):
            suffix = token[idx:]
        else:
            raise ValueError(f"Invalid suffix in {token}")

    return Move(layer=layer, base=base, wide=wide, suffix=suffix)


def format_moves(moves: List[Move]) -> str:
    return ' '.join(str(m) for m in moves)


# --------------------------
# Mapping specs (unchanged)
# --------------------------

specs = {
    'L':  {'map': {'U': 'B', 'B': 'D', 'D': 'F', 'F': 'U'},
           'special': {(3, 'U', True): 'F', (3, 'B', True): 'U'}},
    'F':  {'map': {'U': 'L', 'L': 'D', 'D': 'R', 'R': 'U'},
           'special': {(3, 'R', True): 'D', (3, 'U', True): 'R'}},
    'D':  {'map': {'F': 'L', 'L': 'B', 'B': 'R', 'R': 'F'},
           'special': {(3, 'B', True): 'D', (3, 'U', True): 'R'}},
    'L2': {'map': {'U': 'D', 'D': 'U', 'F': 'B', 'B': 'F'},
           'special': {(3, 'U', True): 'U'}},
    'F2': {'map': {'U': 'D', 'D': 'U', 'R': 'L', 'L': 'R'},
           'special': {(3, 'R', True): 'R'}},
    'D2': {'map': {'F': 'B', 'B': 'F', 'R': 'L', 'L': 'R'},
           'special': {(3, 'B', True): 'B'}},
}


# --------------------------
# Pivot conversion
# --------------------------

def convert_pivot(m: Move) -> Move:
    """
    Convert the pivot itself (wide/plain aware). Wide pivots act even without suffix.
    L  -> 3Rw (plain), Lw -> Rw
    D  -> 3Uw (plain), Dw -> Uw
    F  -> 3Bw (plain), Fw -> Bw
    """
    if m.base == 'L':
        if m.wide:
            return Move(3, 'R', True, m.suffix) if m.layer == 3 else Move(None, 'R', True, m.suffix)
        return Move(3, 'R', True, m.suffix)
    if m.base == 'D':
        if m.wide:
            return Move(3, 'U', True, m.suffix) if m.layer == 3 else Move(None, 'U', True, m.suffix)
        return Move(3, 'U', True, m.suffix)
    if m.base == 'F':
        if m.wide:
            return Move(3, 'B', True, m.suffix) if m.layer == 3 else Move(None, 'B', True, m.suffix)
        return Move(3, 'B', True, m.suffix)
    return m


# --------------------------
# Mapping application
# --------------------------

def apply_mapping(m: Move, mapping: Dict[str, str], special: Dict[Tuple[int, str, bool], str], reverse: bool = False) -> Move:
    """
    Apply mapping to a single move.
    - For 3w moves (layer==3 and wide==True): apply ONLY special mappings; do not apply base map.
      BUT: do NOT apply special mappings when the 3w move has suffix '2' (to preserve 3Uw2, 3Rw2, 3Bw2).
    - For faces/wide (non-3w): apply base-face map.
    - For prime pivots (reverse=True): use inverse base-face map for faces; special reverse for face->3w where defined.
    - Preserve suffix.
    - Do NOT immediately convert plain L/D/F results; they will act later when encountered.
    """
    is_3w = (m.layer == 3 and m.wide)

    if not reverse:
        if is_3w:
            # Suppress specials on 3w double-turns
            if m.suffix == '2':
                return m
            key = (m.layer, m.base, m.wide)
            if key in special:
                # Special maps 3Uw/3Rw/3Bw to a base face; keep as plain face (suffix preserved)
                return Move(None, special[key], False, m.suffix)
            # No base map applied to 3w moves
            return m
        else:
            if m.base in mapping:
                return Move(m.layer, mapping[m.base], m.wide, m.suffix)
            return m
    else:
        # Reverse direction
        if is_3w:
            # No base inverse for 3w; no reverse specials defined from 3w
            return m
        else:
            inv_map = {v: k for k, v in mapping.items()}
            if m.base in inv_map:
                return Move(m.layer, inv_map[m.base], m.wide, m.suffix)
            # Reverse special: face -> 3w when defined
            rev_special = {v: k for k, v in special.items()}  # e.g., 'D' -> (3,'R',True)
            if m.base in rev_special:
                layer, base, wide = rev_special[m.base]
                return Move(layer, base, wide, m.suffix)
            return m


# --------------------------
# Main conversion
# --------------------------

def convert_sequence(seq: str) -> str:
    moves = [parse_move(tok) for tok in seq.split() if tok.strip()]
    i = 0
    while i < len(moves):
        m = moves[i]
        if m.base in ('L', 'D', 'F'):
            pivot_key = m.base + ('2' if m.suffix == '2' else '')
            if pivot_key in specs:
                # Convert pivot itself
                moves[i] = convert_pivot(m)

                # Determine mapping direction
                reverse = (m.suffix == "'") and (pivot_key in ('L', 'D', 'F'))

                # Apply mapping to all subsequent moves
                mapping = specs[pivot_key]['map']
                special = specs[pivot_key]['special']
                for j in range(i + 1, len(moves)):
                    moves[j] = apply_mapping(moves[j], mapping, special, reverse)
        i += 1
    return format_moves(moves)


# --------------------------
# Debug helper (optional)
# --------------------------

def convert_sequence_debug(seq: str) -> str:
    moves = [parse_move(t) for t in seq.split() if t.strip()]
    print('start:', ' '.join(str(m) for m in moves))
    i = 0
    while i < len(moves):
        m = moves[i]
        if m.base in ('L', 'D', 'F'):
            pivot_key = m.base + ('2' if m.suffix == '2' else '')
            if pivot_key in specs:
                print(f"pivot at {i}: {str(m)} ->", end=' ')
                moves[i] = convert_pivot(m)
                print(str(moves[i]))
                reverse = (m.suffix == "'") and (pivot_key in ('L', 'D', 'F'))
                mapping = specs[pivot_key]['map']
                special = specs[pivot_key]['special']
                for j in range(i + 1, len(moves)):
                    before = str(moves[j])
                    moves[j] = apply_mapping(moves[j], mapping, special, reverse)
                    after = str(moves[j])
                    if before != after:
                        print(f"  map {j}: {before} -> {after}")
        i += 1
    print('end:  ', ' '.join(str(m) for m in moves))
    return ' '.join(str(m) for m in moves)


# --------------------------
# Tests (inputs do NOT start with '3')
# --------------------------

def run_tests():
    """
    Deterministic tests + prints for inspection.
    Inputs DO NOT include any tokens beginning with '3'.
    """
    tests = [
        # Sequential pivots on converted string (your corrected example):
        ("L U B D F",              "3Rw B 3Uw 3Rw B"),

        # Wide pivots act even without suffix, and subsequent pivots are processed
        ("Dw F",                   "Uw 3Rw"),
        ("Lw U",                   "Rw B"),
        ("Fw R",                   "Bw U"),

        # Prime/2 variants for wide pivots
        ("Lw' U B",                "Rw' 3Bw 3Rw"),
        ("Lw2 U D",                "Rw2 3Uw U"),

        # Mixed example with wide/non-wide and suffixes
        ("U L F' Uw2 R",           "U 3Rw U' Bw2 R"),

        # Singular long case from your message (tail must remain 3Uw2)
        ("L2 D' R L2 U F' D F' R2 B' U2 F R2 F2 L2 B D2 B U2 D Uw2 Rw2 U2 Fw2 L' Fw2 D' B2 Fw2 R D' L' B U2 Fw Uw2 R' Uw F Uw Rw' U2 L2",
         "3Rw2 U' R 3Rw2 U 3Bw' 3Rw U' 3Bw2 U' 3Rw2 U B2 U2 3Bw2 U 3Rw2 3Uw 3Bw2 B Bw2 Rw2 B2 Uw2 3Rw' Bw2 U' 3Bw2 Bw2 3Rw 3Bw' 3Uw' B 3Rw2 Bw Rw2 U' Rw U Rw Uw' 3Bw2 3Uw2"),
    ]

    for inp, expected in tests:
        out = convert_sequence(inp)
        print(f"{inp} -> {out}")
        assert out == expected, f"Expected: {expected}, got: {out}"

    # Guard: ensure no 3Lw/3Dw/3Fw ever appear
    dangers = ("3Lw", "3Dw", "3Fw")
    for inp, _ in tests:
        out = convert_sequence(inp)
        for d in dangers:
            assert d not in out, f"Forbidden {d} in output for '{inp}': {out}"

    print("\nAll tests passed ✅")


# --------------------------
# CLI
# --------------------------

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        arg = ' '.join(sys.argv[1:])
        if arg.startswith("--debug "):
            seq = arg[len("--debug "):]
            convert_sequence_debug(seq)
        else:
            print(convert_sequence(arg))
    else:
        run_tests()
