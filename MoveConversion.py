# vibe coded conversion script
# convert a set of moves such that no moves effect the DFL corner
# https://chatgpt.com/c/69605e09-b9cc-8326-891e-f7ca8e0f6b9f

# succesful prompt after many revisions:
# create a python script that will convert an input of moves
# the input will be a string of moves represented by letters separated by spaces
# R, U, F, L, D and B
# these letters could have a w suffix (ex. Rw)
# a letter with or without a w suffix could also have either a "'" or a 2
# Example of valid all R moves (R, R', R2, Rw, Rw', Rw2)

# These are the conversion rules

# When an L, F or D appears in the string, convert all following moves not including the current move in the string using the mappings below. Preserve any w, ', or 2 suffix in converted moves
# Mappings (unchanged):
# - L : base U→B, B→D, D→F, F→U;
# - F : base U→L, L→D, D→R, R→U;
# - D : base F→L, L→B, B→R, R→F;
# If the L, F, or D have a "'" suffix, do all mappings in reverse (U > B becomes B < U)

# If the current L, F or D move has a 2 suffix use these mappings
# Double-turn mappings:
# - L2: U↔D, F↔B;
# - F2: U↔D, R↔L;
# - D2: F↔B, R↔L;

# if the current L, F or D move contains a w suffix, convert it to R, B, and U respectively preserving any 2 or ' suffix

# Suffixes:
# - Preserve each move’s own suffix (w, ', 2) after all conversions and mappings.

# once you have gone through each move, convert these moves while preserving any suffix (L > 3Rw, D > 3Uw, F > 3Bw)

import re

# ---------- Parsing helpers ----------

MOVE_RE = re.compile(r"^(R|U|F|L|D|B)(w?)(2|'?)$")

def parse_move(move):
    m = MOVE_RE.match(move)
    if not m:
        raise ValueError(f"Invalid move: {move}")
    base, wide, suffix = m.groups()
    return base, wide, suffix

def build_move(base, wide, suffix):
    return f"{base}{wide}{suffix}"

# ---------- Mapping tables ----------

SINGLE_MAPS = {
    "L": {"U": "B", "B": "D", "D": "F", "F": "U"},
    "F": {"U": "L", "L": "D", "D": "R", "R": "U"},
    "D": {"F": "L", "L": "B", "B": "R", "R": "F"},
}

DOUBLE_MAPS = {
    "L": {"U": "D", "D": "U", "F": "B", "B": "F"},
    "F": {"U": "D", "D": "U", "R": "L", "L": "R"},
    "D": {"F": "B", "B": "F", "R": "L", "L": "R"},
}

FINAL_CONVERSION = {
    "L": "3Rw",
    "D": "3Uw",
    "F": "3Bw",
}

WIDE_CONVERSION = {
    "L": "R",
    "F": "B",
    "D": "U",
}

# ---------- Core logic ----------

def apply_mapping(base, mapping):
    return mapping.get(base, base)

def process_moves(move_string):
    moves = move_string.split()
    parsed = [parse_move(m) for m in moves]

    for i, (base, wide, suffix) in enumerate(parsed):
        if base not in ("L", "F", "D"):
            continue

        # Choose mapping
        if "2" in suffix:
            mapping = DOUBLE_MAPS[base]
        else:
            mapping = SINGLE_MAPS[base]

        # Reverse mapping if '
        if "'" in suffix:
            mapping = {v: k for k, v in mapping.items()}

        # Apply mapping to all following moves
        for j in range(i + 1, len(parsed)):
            b, w, s = parsed[j]
            parsed[j] = (apply_mapping(b, mapping), w, s)

        # Convert wide L/F/D to R/B/U
        if wide:
            base = WIDE_CONVERSION[base]
            parsed[i] = (base, wide, suffix)

    # Final conversion pass
    result = []
    for base, wide, suffix in parsed:
        if base in FINAL_CONVERSION:
            result.append(FINAL_CONVERSION[base] + wide + suffix)
        else:
            result.append(build_move(base, wide, suffix))

    return " ".join(result)

# ---------- Example usage ----------

if __name__ == "__main__":
    inp = "B Rw F B Fw Rw B L Uw' B R Fw2 Uw' B' L' Uw2 Rw2 F U2 R2 Fw2 R' F Rw2 Uw2 U' R2 B R2 D2 L2 D2 B2 D2 B2 D B2 R' D' L' D U' L U2"
    inp = process_moves(inp)
    inp = inp.split(" ")
    print(inp)
