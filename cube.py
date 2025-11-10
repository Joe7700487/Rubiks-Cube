# Example file showing a circle moving on screen
import pygame
import numpy as np
import math
import time
import g1PruningTable
import g2PruningTable
import g3SolvedStates
import g3PruningTable
import g4PruningTable

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

#------------------------ Cube setup ---------------------------------
x = 0
y = 1
z = 2
size = 25
# offsets for drawing faces
uOffset = (size * 3, size * 0)
lOffset = (size * 0, size * 3)
fOffset = (size * 3, size * 3)
rOffset = (size * 6, size * 3)
bOffset = (size * 9, size * 3)
dOffset = (size * 3, size * 6)
# colors
blue    = (0, 0, 255)
green   = (0, 255, 0)
red     = (255, 0, 0)
white   = (255, 255, 255)
orange  = (255,165,0)
yellow  = (255,215,0)
black  = (50,50,50)
offwhite  = (255,245,200)
purple  = (138,43,226)
pink  = (255,0,255)

# ------------------------------------------ fcube logic -----------------------------------

# return the fcube index from the index of a face
def S(face, idx):
    idx = idx - 1
    index = 0
    if face == "U": index = idx + 0
    elif face == "L" : index = idx + 9
    elif face == "F" : index = idx + 18
    elif face == "R" : index = idx + 27
    elif face == "B" : index = idx + 36
    elif face == "D" : index = idx + 45
    return (index)

# recieve a list of indicies and return a string of faces for each index
def getFacesFromIndex(indexs):
    string = ""
    for index in indexs:
        if   index >= 45: string += "D"
        elif index >= 36: string += "B"
        elif index >= 27: string += "R"
        elif index >= 18: string += "F"
        elif index >= 9:  string += "L"
        elif index >= 0:  string += "U"
    return string

# take a string to display the state of the cube
def drawState (state, globalxOffset, globalyOffset):
    offset = uOffset
    color = ()
    for i in range(len(state)):
        sticker = state[i]
        if   i > 44: offset = dOffset
        elif i > 35: offset = bOffset
        elif i > 26: offset = rOffset
        elif i > 17: offset = fOffset
        elif i > 8: offset = lOffset
        if   sticker == "U": color = white
        elif sticker == "L": color = orange
        elif sticker == "F": color = green
        elif sticker == "R": color = red
        elif sticker == "B": color = blue
        elif sticker == "D": color = yellow
        elif sticker == "X": color = black
        elif sticker == "o": color = offwhite
        elif sticker == "x": color = purple
        elif sticker == "y": color = pink
        xOffset = (i % 3) * size
        if (i % 3 == 0) and (i > 0): yOffset += size
        if i % 9 == 0: yOffset = 0
        pygame.draw.rect(screen, color,  (offset[0] + xOffset + globalxOffset, offset[1] + yOffset + globalyOffset, size, size), 0)
        pygame.draw.rect(screen, "black",  (offset[0] + xOffset + globalxOffset, offset[1] + yOffset + globalyOffset, size, size), 1) 

# take in an fcube string and apply a list of permutation pairs to it
def applyMove(cube_list, move):
    move = fMoves[move]
    # apply permutation directly on the list
    newCube = cube_list[:]  # shallow copy (keeps same type)
    for a, b in move:
        newCube[b] = cube_list[a]
    return newCube

# apply a list of moves in the form of a string in standard notation
def applyFmoves(cube, moves):
    moves = moves.split(" ")
    cube_list = list(cube)  # only convert once
    for move in moves:
        cube_list = applyMove(cube_list, move)
    return "".join(cube_list)  # convert back once
# apply a list of moves to an IF cube list
def applyIFmoves(cube, moves):
    moves = moves.split(" ")
    cube_list = cube
    for move in moves:
        cube_list = applyMove(cube_list, move)
    return cube_list

# --------------------------------------------- gcube logic --------------------------------------------
class Sticker:
    def __init__(self, pos, dst):
        self.pos = pos
        self.dst = dst

class gMove:
    def __init__(self, name, axis, angle, predicate):
        self.name = name
        self.axis = axis
        self.angle = angle
        self.predicate = predicate

# calculate a vectors position after applying a rotation around an axis
def applyAxisAngle(vector, axis, angle_radians):
    angle_radians = math.radians(angle_radians)
    axis = axis / np.linalg.norm(axis)
    rotated_vector = (
        vector * np.cos(angle_radians)
        + np.cross(axis, vector) * np.sin(angle_radians)
        + axis * np.dot(axis, vector) * (1 - np.cos(angle_radians))
    )
    rotated_vector[x] = round(rotated_vector[x])
    rotated_vector[y] = round(rotated_vector[y])
    rotated_vector[z] = round(rotated_vector[z])
    return rotated_vector.astype(int)

# if a sticker participates in a move, rotate it by degrees around the faces axis
def applyGMove(cube, move):
    for sticker in cube:
        if gMoves[move].predicate(sticker.pos):
            sticker.pos = applyAxisAngle(sticker.pos, gMoves[move].axis, gMoves[move].angle)

# apply a list of gmove to a cube
def applyGmoves(cube, moves):
    moves = moves.split(" ")
    for move in moves:
        applyGMove(cube, move)

# return a list of stickers on a face from left to right top to bottom
def sortFace(gcube, face):
    if face == "U": return sorted([s for s in gcube if s.pos[y] == 3],  key=lambda s: ( s.pos[z],  s.pos[x]))
    if face == "D": return sorted([s for s in gcube if s.pos[y] == -3], key=lambda s: (-s.pos[z],  s.pos[x]))
    if face == "L": return sorted([s for s in gcube if s.pos[x] == -3], key=lambda s: (-s.pos[y],  s.pos[z]))
    if face == "R": return sorted([s for s in gcube if s.pos[x] == 3],  key=lambda s: (-s.pos[y], -s.pos[z]))
    if face == "F": return sorted([s for s in gcube if s.pos[z] == 3],  key=lambda s: (-s.pos[y],  s.pos[x])) 
    if face == "B": return sorted([s for s in gcube if s.pos[z] == -3], key=lambda s: (-s.pos[y], -s.pos[x]))

# return the face of the stickers position
def getFace(sticker):
    if (sticker.pos[y] == 3):
        return "U"
    elif (sticker.pos[y] == -3):
        return "D"
    elif (sticker.pos[x] == 3):
        return "R"
    elif (sticker.pos[x] == -3):
        return "L"
    elif (sticker.pos[z] == 3):
        return "F"
    elif (sticker.pos[z] == -3):
        return "B"

# return the face of the stickers destination
def getColor(sticker):
    if (sticker.dst[y] == 3):
        return "U"
    elif (sticker.dst[y] == -3):
        return "D"
    elif (sticker.dst[x] == 3):
        return "R"
    elif (sticker.dst[x] == -3):
        return "L"
    elif (sticker.dst[z] == 3):
        return "F"
    elif (sticker.dst[z] == -3):
        return "B"

# ---------------------------------------- conversion functions -------------------------------------
# convert gcube to fcube
def convertGcube(gcube):
    sCube = ""
    uFace = sortFace(gcube, "U")
    dFace = sortFace(gcube, "D")
    lFace = sortFace(gcube, "L")
    rFace = sortFace(gcube, "R")
    fFace = sortFace(gcube, "F") 
    bFace = sortFace(gcube, "B")

    # Build ULFRBD order
    for face in [uFace, lFace, fFace, rFace, bFace, dFace]:
        for sticker in face:
            sCube += getColor(sticker)
    return sCube

# functions to return the fcube index of a gcube sticker  used to convert moves
# def getIndexPos(gcube, sticker):
#     face = getFace(sticker)
#     stickers = sortFace(gcube, face)
#     for s in stickers:
#         if s.pos[x] == sticker.pos[x] and s.pos[y] == sticker.pos[y] and s.pos[z] == sticker.pos[z]:
#             index = stickers.index(s)
#             return S(face, index) + 1
# def getIndexDst(gcube, sticker):
#     stickers = sortFace(gcube, "U") + sortFace(gcube, "L") + sortFace(gcube, "F") + sortFace(gcube, "R") + sortFace(gcube, "B") + sortFace(gcube, "D")
#     for s in stickers:
#         if s.pos[x] == sticker.dst[x] and s.pos[y] == sticker.dst[y] and s.pos[z] == sticker.dst[z]:
#             face = getFace(s)
#             stickers = sortFace(gcube, face)
#             index = stickers.index(s)
#             return S(face, index) + 1

# # create a [src, dst] pair for every sticker involved in the move and put it in a list and output move to console
# def convertGmove(gMove, gCube):
#     move = []
#     applyGMove(gCube, gMove)
#     for sticker in gCube:
#         if gMove.predicate(sticker.pos):
#             move.append([getIndexDst(gCube, sticker), getIndexPos(gCube, sticker)])
#     print(gMove.name.lower() + "Move = " + str(move))

# ------------------------------ define solved cubes and legal moves --------------------------
# moves defined by permutation pairs
fMoves = {  "U":  [[0, 2], [1, 5], [2, 8], [3, 1], [4, 4], [5, 7], [6, 0], [7, 3], [8, 6], [29, 20], [28, 19], [27, 18], [9, 36], [10, 37], [11, 38], [18, 9], [19, 10], [20, 11], [38, 29], [37, 28], [36, 27]],
            "D":  [[51, 45], [52, 48], [53, 51], [48, 46], [49, 49], [50, 52], [45, 47], [46, 50], [47, 53], [35, 44], [34, 43], [33, 42], [15, 24], [16, 25], [17, 26], [24, 33], [25, 34], [26, 35], [44, 17], [43, 16], [42, 15]],
            "L":  [[0, 18], [3, 21], [6, 24], [51, 38], [48, 41], [45, 44], [15, 9], [12, 10], [9, 11], [16, 12], [13, 13], [10, 14], [17, 15], [14, 16], [11, 17], [24, 51], [21, 48], [18, 45], [44, 0], [41, 3], [38, 6]],
            "R":  [[2, 42], [5, 39], [8, 36], [53, 26], [50, 23], [47, 20], [35, 33], [32, 34], [29, 35], [34, 30], [31, 31], [28, 32], [33, 27], [30, 28], [27, 29], [26, 8], [23, 5], [20, 2], [42, 47], [39, 50], [36, 53]],
            "F":  [[6, 27], [7, 30], [8, 33], [45, 11], [46, 14], [47, 17], [33, 45], [30, 46], [27, 47], [17, 6], [14, 7], [11, 8], [24, 18], [25, 21], [26, 24], [21, 19], [22, 22], [23, 25], [18, 20], [19, 23], [20, 26]],
            "B":  [[0, 15], [1, 12], [2, 9], [51, 35], [52, 32], [53, 29], [35, 2], [32, 1], [29, 0], [15, 53], [12, 52], [9, 51], [44, 42], [43, 39], [42, 36], [41, 43], [40, 40], [39, 37], [38, 44], [37, 41], [36, 38]],
            "U'": [[0, 6], [1, 3], [2, 0], [3, 7], [4, 4], [5, 1], [6, 8], [7, 5], [8, 2], [29, 38], [28, 37], [27, 36], [9, 18], [10, 19], [11, 20], [18, 27], [19, 28], [20, 29], [38, 11], [37, 10], [36, 9]],
            "D'": [[51, 53], [52, 50], [53, 47], [48, 52], [49, 49], [50, 46], [45, 51], [46, 48], [47, 45], [35, 26], [34, 25], [33, 24], [15, 42], [16, 43], [17, 44], [24, 15], [25, 16], [26, 17], [44, 35], [43, 34], [42, 33]],
            "L'": [[0, 44], [3, 41], [6, 38], [51, 24], [48, 21], [45, 18], [15, 17], [12, 16], [9, 15], [16, 14], [13, 13], [10, 12], [17, 11], [14, 10], [11, 9], [24, 6], [21, 3], [18, 0], [44, 45], [41, 48], [38, 51]],
            "R'": [[2, 20], [5, 23], [8, 26], [53, 36], [50, 39], [47, 42], [35, 29], [32, 28], [29, 27], [34, 32], [31, 31], [28, 30], [33, 35], [30, 34], [27, 33], [26, 53], [23, 50], [20, 47], [42, 2], [39, 5], [36, 8]],
            "F'": [[6, 17], [7, 14], [8, 11], [45, 33], [46, 30], [47, 27], [33, 8], [30, 7], [27, 6], [17, 47], [14, 46], [11, 45], [24, 26], [25, 23], [26, 20], [21, 25], [22, 22], [23, 19], [18, 24], [19, 21], [20, 18]],
            "B'": [[0, 29], [1, 32], [2, 35], [51, 9], [52, 12], [53, 15], [35, 51], [32, 52], [29, 53], [15, 0], [12, 1], [9, 2], [44, 38], [43, 41], [42, 44], [41, 37], [40, 40], [39, 43], [38, 36], [37, 39], [36, 42]],
            "U2": [[0, 8], [1, 7], [2, 6], [3, 5], [4, 4], [5, 3], [6, 2], [7, 1], [8, 0], [29, 11], [28, 10], [27, 9], [9, 27], [10, 28], [11, 29], [18, 36], [19, 37], [20, 38], [38, 20], [37, 19], [36, 18]],
            "D2": [[51, 47], [52, 46], [53, 45], [48, 50], [49, 49], [50, 48], [45, 53], [46, 52], [47, 51], [35, 17], [34, 16], [33, 15], [15, 33], [16, 34], [17, 35], [24, 42], [25, 43], [26, 44], [44, 26], [43, 25], [42, 24]],
            "L2": [[0, 45], [3, 48], [6, 51], [51, 6], [48, 3], [45, 0], [15, 11], [12, 14], [9, 17], [16, 10], [13, 13], [10, 16], [17, 9], [14, 12], [11, 15], [24, 38], [21, 41], [18, 44], [44, 18], [41, 21], [38, 24]],
            "R2": [[2, 47], [5, 50], [8, 53], [53, 8], [50, 5], [47, 2], [35, 27], [32, 30], [29, 33], [34, 28], [31, 31], [28, 34], [33, 29], [30, 32], [27, 35], [26, 36], [23, 39], [20, 42], [42, 20], [39, 23], [36, 26]],
            "F2": [[6, 47], [7, 46], [8, 45], [45, 8], [46, 7], [47, 6], [33, 11], [30, 14], [27, 17], [17, 27], [14, 30], [11, 33], [24, 20], [25, 19], [26, 18], [21, 23], [22, 22], [23, 21], [18, 26], [19, 25], [20, 24]],
            "B2": [[0, 53], [1, 52], [2, 51], [51, 2], [52, 1], [53, 0], [35, 9], [32, 12], [29, 15], [15, 29], [12, 32], [9, 35], [44, 36], [43, 37], [42, 38], [41, 39], [40, 40], [39, 41], [38, 42], [37, 43], [36, 44]] }

gMoves = { "U": gMove("U", np.array([0, 1, 0]),  270,  lambda pos: pos[y] > 0),
            "D": gMove("D", np.array([0, -1, 0]), 270,  lambda pos: pos[y] < 0),
            "R": gMove("R", np.array([1, 0, 0]),  270,  lambda pos: pos[x] > 0),
            "L": gMove("L", np.array([-1, 0, 0]), 270,  lambda pos: pos[x] < 0),
            "F": gMove("F", np.array([0, 0, 1]),  270,  lambda pos: pos[z] > 0),
            "B": gMove("B", np.array([0, 0, -1]), 270,  lambda pos: pos[z] < 0),
            "U'": gMove("U'", np.array([0, 1, 0]),  90,  lambda pos: pos[y] > 0),
            "D'": gMove("D'", np.array([0, -1, 0]), 90,  lambda pos: pos[y] < 0),
            "R'": gMove("R'", np.array([1, 0, 0]),  90,  lambda pos: pos[x] > 0),
            "L'": gMove("L'", np.array([-1, 0, 0]), 90,  lambda pos: pos[x] < 0),
            "F'": gMove("F'", np.array([0, 0, 1]),  90,  lambda pos: pos[z] > 0),
            "B'": gMove("B'", np.array([0, 0, -1]), 90,  lambda pos: pos[z] < 0),
            "U2": gMove("U2", np.array([0, 1, 0]),  180,  lambda pos: pos[y] > 0),
            "D2": gMove("D2", np.array([0, -1, 0]), 180,  lambda pos: pos[y] < 0),
            "R2": gMove("R2", np.array([1, 0, 0]),  180,  lambda pos: pos[x] > 0),
            "L2": gMove("L2", np.array([-1, 0, 0]), 180,  lambda pos: pos[x] < 0),
            "F2": gMove("F2", np.array([0, 0, 1]),  180,  lambda pos: pos[z] > 0),
            "B2": gMove("B2", np.array([0, 0, -1]), 180,  lambda pos: pos[z] < 0), }

solvedCube = "UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD"
solvedCubeAfter = "UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD"
solvedGCube = [ Sticker(np.array([x, 3, y]), np.array([x, 3, y])) if f == 0 else
                Sticker(np.array([x, -3, y]), np.array([x, -3, y])) if f == 1 else
                Sticker(np.array([3, x, y]), np.array([3, x, y])) if f == 2 else
                Sticker(np.array([-3, x, y]), np.array([-3, x, y])) if f == 3 else
                Sticker(np.array([x, y, 3]), np.array([x, y, 3])) if f == 4 else
                Sticker(np.array([x, y, -3]), np.array([x, y, -3]))
                for f in range(6)
                for i in range(3)
                for j in range(3)
                for x, y in [((-2 + j * 2), (-2 + i * 2))] ]

# --------------------------------- solver -----------------------------------------------
stdMoves = ["U", "U'", "U2", "D", "D'", "D2", "L", "L'", "L2", "R", "R'", "R2", "F", "F'", "F2", "B", "B'", "B2"]
ifCube = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53]
ifCubeAfter = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53]

def genPruningTable(solvedStates, depth, moveset):
    pruningTable = {}
    previousFrontier = solvedStates

    for state in solvedStates:
        pruningTable[state] = 0

    for i in range(1, depth + 1):
        frontier = []
        for state in previousFrontier:
            for move in moveset:
                newState = "".join(applyFmoves(state, move))
                if(newState not in pruningTable):
                    pruningTable[newState] = i
                    frontier.append(newState)
        previousFrontier = frontier

    with open("g4PruningTable.py", "w") as file:
        file.write("table = {")
        for key, value in pruningTable.items():
            file.write(f"'{key}':{value},\n")
        file.write("}")
    return pruningTable

class SimpleSolver:
    def __init__(self, isSolved, candidateMoves, pruningTable, pruningDepth, pieces):
        self.isSolved = isSolved
        self.moves = candidateMoves
        self.pruningTable = pruningTable
        self.pruningDepth = pruningDepth
        self.pieces = pieces


# g1 solver
def g1IsSolved(fcube, pieces):
    FBFACES = "oooooooooooo"
    for i in range(len(pieces)):
        if (fcube[pieces[i]] != FBFACES[i]):
            return False
    return True

g1Peices = [1, 3, 5, 7, 46, 48, 50, 52, 21, 23, 39, 41]
g1Mask = "".join("o" if i in g1Peices else "X" for i in ifCube)
g1MaskAfter = "".join("o" if i in g1Peices else "X" for i in ifCube)
g1MoveSet = stdMoves
# genPruningTable([g1Mask], 8, g1MoveSet)
g1Solver = SimpleSolver(g1IsSolved, g1MoveSet, g1PruningTable.table, 5, g1Peices)

# g2 solver
def g2IsSolved(fcube, pieces):
    FBFACES = "xxxxxxxxyyyyxxxxxxxx"
    for i in range(len(pieces)):
        if (fcube[pieces[i]] != FBFACES[i]):
            return False
    return True
g2CornerPeices = [0, 2, 6, 8, 45, 47, 51, 53]
g2udEdgePeices = [1, 3, 5, 7, 46, 48, 50, 52]
g2eEdgePeices = [21, 23, 39, 41]
g2Peices = sorted(g2CornerPeices + g2udEdgePeices + g2eEdgePeices)
g2Mask = "".join("x" if c in g2CornerPeices or c in g2udEdgePeices else "y" if c in g2eEdgePeices else "X" for c in ifCube)
g2MaskAfter = g2Mask
g2MoveSet = ["U", "U'", "U2", "D", "D'", "D2", "L", "L'", "L2", "R", "R'", "R2", "F2", "B2"]
# genPruningTable([g2Mask], 6, g2MoveSet)
g2Solver = SimpleSolver(g2IsSolved, g2MoveSet, g2PruningTable.table, 5, g2Peices)

# g3 solver
def g3IsSolved(fcube, pieces):
    states = list(g3SolvedStates.table.keys())
    if fcube in states:
        return True
    else:
        return False
g3MoveSet = ["U", "U'", "U2", "D", "D'", "D2", "L2", "R2", "F2", "B2"]
cornerPeices = [0, 2, 6, 8, 45, 47, 51, 53, 9, 11, 15, 17, 27, 29, 33, 35, 36, 38, 42, 44, 18, 20, 24, 26]
edgePeices = [10, 12, 14, 16, 19, 21, 23, 25, 28, 30, 32, 34, 37, 39, 41, 43]
g3Peices = sorted(cornerPeices + edgePeices)
cornerMask = "UXUXXXUXULXLXXXLXLFXFXXXFXFRXRXXXRXRBXBXXXBXBDXDXXXDXD"
g3Mask = ""
for i in range(len(ifCube)):
    if ifCube[i] in cornerPeices:
        g3Mask += getFacesFromIndex([ifCube[i]])
    elif ifCube[i] in edgePeices:
        face = getFacesFromIndex([ifCube[i]])
        if face == "L": face = "R"
        if face == "B": face = "F"
        g3Mask += face
    else:
        g3Mask += "X"
g3MaskAfter = g3Mask
# genPruningTable([g3Mask], 10, ["U2", "D2", "L2", "R2", "F2", "B2"])
# genPruningTable(list(g3SolvedStates.table.keys()), 5, g3MoveSet)
g3Solver = SimpleSolver(g3IsSolved, g3MoveSet, g3PruningTable.table, 5, g3Peices)


# g4 solver
def g4IsSolved(fcube, pieces):
    if fcube == "UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD" : return True
    else: return False
g4MoveSet = ["U2", "D2", "L2", "R2", "F2", "B2"]
g4Solver = SimpleSolver(g4IsSolved, g4MoveSet, g4PruningTable.table, 6, ifCube)

## IMPORTANT FUNCTIONS
def solvedfsWithPruning(solver, cube, solution, depthRemaining):
    if solver.isSolved(cube, solver.pieces):
        return solution.strip()

    # pruning
    lowerBound = solver.pruningTable.get(cube)
    if lowerBound == None:
        lowerBound = solver.pruningDepth + 1
    if lowerBound > depthRemaining:
        return None
    
    for move in solver.moves:
        if len(solution) and move[0] == solution[len(solution) - 1][0]:
            continue
        
        result = solvedfsWithPruning(solver, applyFmoves(cube, move), solution + " " + str(move), depthRemaining - 1,)
        if result != None:
            return result
    return None

# iteratively deepening dfs
def solveiddfs2(solver, maskedCube, depthLimit):
    for depth in range(depthLimit):
        solution = solvedfsWithPruning(solver, maskedCube, "", depth + 1)
        if (solution != None):
            return solution
    return None

# -------------------------------- program loop -------------------------------------------
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_u:
                solvedCube = applyFmoves(solvedCube, "U")
                # applyGMove(solvedGCube, "U")
                # solvedCube = convertGcube(solvedGCube)
            if event.key == pygame.K_r:
                solvedCube = applyFmoves(solvedCube, "R")
                # applyGMove(solvedGCube, "R")
                # solvedCube = convertGcube(solvedGCube)
            if event.key == pygame.K_l:
                solvedCube = applyFmoves(solvedCube, "L")
                # applyGMove(solvedGCube, "L")
                # solvedCube = convertGcube(solvedGCube)
            if event.key == pygame.K_d:
                solvedCube = applyFmoves(solvedCube, "D")
                # applyGMove(solvedGCube, "D")
                # solvedCube = convertGcube(solvedGCube)
            if event.key == pygame.K_f:
                solvedCube = applyFmoves(solvedCube, "F")
                # applyGMove(solvedGCube, "F")
                # solvedCube = convertGcube(solvedGCube)
            if event.key == pygame.K_b:
                solvedCube = applyFmoves(solvedCube, "B")
                # applyGMove(solvedGCube, gMoves["B"])
                # solvedCube = convertGcube(solvedGCube)

            # test solver
            if event.key == pygame.K_s:
                
                # scramble = "B L2 B' L2 B D' B' L' B L B D B2 L"
                # scramble = "D R U R' U' R U R' U' D U R U' R' U R U' R' D2"
                scramble = "F D2 F D2 F' L2 D2 B2 L2 B' D2 R D' R' U2 B D F D2 L2"
                solvedCube = applyFmoves(solvedCube, scramble)
                ifCube = applyIFmoves(ifCube, scramble)
                solvedCubeAfter = solvedCube

                startTime = time.perf_counter()

                solution = ""
                part1 = solveiddfs2(g1Solver, "".join("o" if i in g1Peices else "X" for i in ifCube), 10)
                solvedCubeAfter = applyFmoves(solvedCube, part1)
                ifCube = applyIFmoves(ifCube, part1)

                part2 = solveiddfs2(g2Solver, "".join("x" if c in g2CornerPeices or c in g2udEdgePeices else "y" if c in g2eEdgePeices else "X" for c in ifCube), 20)
                solvedCubeAfter = applyFmoves(solvedCubeAfter, part2)
                ifCube = applyIFmoves(ifCube, part2)
                
                g3Mask = ""
                for i in range(len(ifCube)):
                    if ifCube[i] in cornerPeices:
                        g3Mask += getFacesFromIndex([ifCube[i]])
                    elif ifCube[i] in edgePeices:
                        face = getFacesFromIndex([ifCube[i]])
                        if face == "L": face = "R"
                        if face == "B": face = "F"
                        g3Mask += face
                    else:
                        g3Mask += "X"
                part3 = solveiddfs2(g3Solver, g3Mask, 20)
                solvedCubeAfter = applyFmoves(solvedCubeAfter, part3)
                ifCube = applyIFmoves(ifCube, part3)

                part4 = solveiddfs2(g4Solver, solvedCubeAfter, 20)
                solvedCubeAfter = applyFmoves(solvedCubeAfter, part4)
                ifCube = applyIFmoves(ifCube, part4)
                solution = part1 + " " + part2 + " "  + part3 + " "  + part4
                endTime = time.perf_counter()

                if solution != None:
                    if len(solution) > 0:
                        solvedCubeAfter = applyFmoves(solvedCube, solution)
                        print(len(solution.split()))
                        print(solution)
                        totalTime = endTime - startTime
                        print(f"Solved in {totalTime:.2f} seconds")
                    else:
                        print("Already Solved")
                else:
                    print("out of range")

            # test efficiency of model types
            #Facelet model: 
            # 100026 moves in 108 miliseconds 922237.76 Moves per sec version 1
            # 100026 moves in 70 miliseconds 1427327.94 Moves per sec version 2
            # Geometric model: 
            # 100026 moves in 69620 miliseconds 1436.74 Moves per sec
            loops = 5557
            if event.key == pygame.K_t:
                print("----------------------------------")
                moveCount = loops * 18
                startTime = time.perf_counter()
                for i in range(loops): solvedCube = applyFmoves(solvedCube, "U D L R F B U' D' L' R' F' B' U2 D2 L2 R2 F2 B2")
                endTime = time.perf_counter()

                totalTime = endTime - startTime
                rate = (moveCount / totalTime)
                print("Facelet model: ")
                print(f"{moveCount:.0f} moves in {totalTime * 1000:.0f} miliseconds {rate:.2f} Moves per sec")

                # startTime = time.perf_counter()
                # for i in range(loops): applyGmoves(solvedGCube, "U D L R F B U' D' L' R' F' B' U2 D2 L2 R2 F2 B2")
                # endTime = time.perf_counter()

                # totalTime = endTime - startTime
                # rate = (moveCount / totalTime)
                # print("Geometric model: ")
                # print(f"{moveCount:.0f} moves in {totalTime * 1000:.0f} miliseconds {rate:.2f} Moves per sec")
                # solvedCube = convertGcube(solvedGCube)



    # fill the screen with a color to wipe away anything from last frame
    screen.fill((100,100,100))

    drawState(solvedCube, 100, 100)
    drawState(solvedCubeAfter, 100, 350)
    # drawState(g3Mask, 450, 100)
    # drawState(g3MaskAfter, 450, 350)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()