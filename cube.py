# Example file showing a circle moving on screen
import pygame
import numpy as np
import math
import time

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
size = 50
globalOffset = 100
# offsets for drawing faces
uOffset = (size * 3 + globalOffset, size * 0 + globalOffset)
lOffset = (size * 0 + globalOffset, size * 3 + globalOffset)
fOffset = (size * 3 + globalOffset, size * 3 + globalOffset)
rOffset = (size * 6 + globalOffset, size * 3 + globalOffset)
bOffset = (size * 9 + globalOffset, size * 3 + globalOffset)
dOffset = (size * 3 + globalOffset, size * 6 + globalOffset)
# colors
blue    = (0, 0, 255)
green   = (0, 255, 0)
red     = (255, 0, 0)
white   = (255, 255, 255)
orange  = (255,165,0)
yellow  = (255,215,0)

# ------------------------------------------ fcube logic -----------------------------------
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

def getFacesFromIndex(indexs):
    string = ""
    for index in indexs:
        string += getFaceFromIndex(index)
    return string
def getFaceFromIndex(index):
    if   index >= 45: return "D"
    elif index >= 36: return "B"
    elif index >= 27: return "R"
    elif index >= 18: return "F"
    elif index >= 9:  return "L"
    elif index >= 0:  return "U"

# take a string to display the state of the cube
def drawState (state):
    xOffset = 0
    yOffset = 0
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
        xOffset = (i % 3) * size
        if (i % 3 == 0) and (i > 0): yOffset += size
        if i % 9 == 0: yOffset = 0
        pygame.draw.rect(screen, color,  (offset[0] + xOffset, offset[1] + yOffset, size, size), 0)
        pygame.draw.rect(screen, "black",  (offset[0] + xOffset, offset[1] + yOffset, size, size), 2) 

# take a list of ints and returns a list containings pairs of (source, destination)
def permFromCycle (stickers):
    perm = [] # src - dst
    for i in range(len(stickers)):
        if i + 1 < len(stickers):
            perm.append([stickers[i], stickers[i + 1]])
        else :
            perm.append([stickers[i], stickers[0]])
    return perm

# take a list of permutation pairs and swap : requires preturned cube to compare to
# def swapStickers(cube, perm, newCube):
#     for pair in perm:
#         newCube[pair[1]] = cube[pair[0]]
#     return newCube

# take in a cube state and apply a list of permutations to it
# def applyMove (cube, move):
#     newCube = list(cube)
#     for perms in move:
#         perm = permFromCycle(perms)
#         print(perm)
#         newCube = swapStickers(cube, perm, newCube)
#         # for pair in perm:
#         #     newCube[pair[1]] = cube[pair[0]]
#     newCube = "".join(newCube)
#     return newCube

# take a list of permutation pairs and swap : list must contain every pair of permutations so it doesnt require memory
def swapStickers(cube, perm, newCube):
    for pair in perm:
        newCube[pair[1]] = cube[pair[0]]
    return newCube
# take in a cube state and apply a list of permutation pairs to it
def applyMove (cube, move):
    newCube = list(cube)
    newCube = swapStickers(cube, move, newCube)
    newCube = "".join(newCube)
    return newCube

def applyMoveByLetter(cube, letter):
    if   letter == "U": return applyMove(cube, uMove)
    elif letter == "D": return applyMove(cube, dMove)
    elif letter == "L": return applyMove(cube, lMove)
    elif letter == "R": return applyMove(cube, rMove)
    elif letter == "F": return applyMove(cube, fMove)
    elif letter == "B": return applyMove(cube, bMove)

    if   letter == "U'": return applyMove(cube, upMove)
    elif letter == "D'": return applyMove(cube, dpMove)
    elif letter == "L'": return applyMove(cube, lpMove)
    elif letter == "R'": return applyMove(cube, rpMove)
    elif letter == "F'": return applyMove(cube, fpMove)
    elif letter == "B'": return applyMove(cube, bpMove)

    if   letter == "U2": return applyMove(cube, u2Move)
    elif letter == "D2": return applyMove(cube, d2Move)
    elif letter == "L2": return applyMove(cube, l2Move)
    elif letter == "R2": return applyMove(cube, r2Move)
    elif letter == "F2": return applyMove(cube, f2Move)
    elif letter == "B2": return applyMove(cube, b2Move)

def applyFmoves(cube, moves):
    for move in moves:
        cube = applyMove(cube, move)
    return cube

def applyFmovesByLetter(cube, moves):
    if type(moves) is list:
        for move in moves:
            cube = applyMoveByLetter(cube, move)
        return cube
    elif type(moves) is str:
        moves = moves.split(" ")
        for move in moves:
            cube = applyMoveByLetter(cube, move)
        return cube

# --------------------------------------------- gcube logic --------------------------------------------
# calculate a vectors position after applying a rotation around an axis
def applyAxisAngle(vector, axis, angle_radians):
    angle_radians = math.radians(angle_radians)

    # Normalize the axis to ensure it's a unit vector
    axis = axis / np.linalg.norm(axis)

    # Rodrigues' rotation formula
    rotated_vector = (
        vector * np.cos(angle_radians)
        + np.cross(axis, vector) * np.sin(angle_radians)
        + axis * np.dot(axis, vector) * (1 - np.cos(angle_radians))
    )
    rotated_vector[x] = round(rotated_vector[x])
    rotated_vector[y] = round(rotated_vector[y])
    rotated_vector[z] = round(rotated_vector[z])
    return rotated_vector.astype(int)

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

# if a sticker participates in a move, rotate it by degrees around the faces axis
def applyGMove(cube, move):
    for sticker in cube:
        if move.predicate(sticker.pos):
            sticker.pos = applyAxisAngle(sticker.pos, move.axis, move.angle)

    

def applyGmoves(cube, moves):
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
# functions to return the fcube index of a gcube sticker
def getIndexPos(gcube, sticker):
    face = getFace(sticker)
    stickers = sortFace(gcube, face)
    for s in stickers:
        if s.pos[x] == sticker.pos[x] and s.pos[y] == sticker.pos[y] and s.pos[z] == sticker.pos[z]:
            index = stickers.index(s)
            return S(face, index) + 1
def getIndexDst(gcube, sticker):
    stickers = sortFace(gcube, "U") + sortFace(gcube, "L") + sortFace(gcube, "F") + sortFace(gcube, "R") + sortFace(gcube, "B") + sortFace(gcube, "D")
    for s in stickers:
        if s.pos[x] == sticker.dst[x] and s.pos[y] == sticker.dst[y] and s.pos[z] == sticker.dst[z]:
            face = getFace(s)
            stickers = sortFace(gcube, face)
            index = stickers.index(s)
            return S(face, index) + 1
        
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

# create a [src, dst] pair for every sticker involved in the move and put it in a list and output move to console
def convertGmove(gMove, gCube):
    move = []
    applyGMove(gCube, gMove)
    for sticker in gCube:
        if gMove.predicate(sticker.pos):
            move.append([getIndexDst(gCube, sticker), getIndexPos(gCube, sticker)])
    print(gMove.name.lower() + "Move = " + str(move))

# ------------------------------ define solved cubes and legal moves --------------------------
# a move defined as permutation sets
# uMove = [[ S("U",1), S("U",3), S("U",9), S("U",7) ],
#          [ S("U",2), S("U",6), S("U",8), S("U",4) ],
#          [ S("F",1), S("L",1), S("B",1), S("R",1) ],
#          [ S("F",2), S("L",2), S("B",2), S("R",2) ],
#          [ S("F",3), S("L",3), S("B",3), S("R",3) ] ]
# moves defined by permutation pairs
uMove = [[0, 2], [1, 5], [2, 8], [3, 1], [4, 4], [5, 7], [6, 0], [7, 3], [8, 6], [29, 20], [28, 19], [27, 18], [9, 36], [10, 37], [11, 38], [18, 9], [19, 10], [20, 11], [38, 29], [37, 28], [36, 27]]
dMove = [[51, 45], [52, 48], [53, 51], [48, 46], [49, 49], [50, 52], [45, 47], [46, 50], [47, 53], [35, 44], [34, 43], [33, 42], [15, 24], [16, 25], [17, 26], [24, 33], [25, 34], [26, 35], [44, 17], [43, 16], [42, 15]]
lMove = [[0, 18], [3, 21], [6, 24], [51, 38], [48, 41], [45, 44], [15, 9], [12, 10], [9, 11], [16, 12], [13, 13], [10, 14], [17, 15], [14, 16], [11, 17], [24, 51], [21, 48], [18, 45], [44, 0], [41, 3], [38, 6]]
rMove = [[2, 42], [5, 39], [8, 36], [53, 26], [50, 23], [47, 20], [35, 33], [32, 34], [29, 35], [34, 30], [31, 31], [28, 32], [33, 27], [30, 28], [27, 29], [26, 8], [23, 5], [20, 2], [42, 47], [39, 50], [36, 53]]
fMove = [[6, 27], [7, 30], [8, 33], [45, 11], [46, 14], [47, 17], [33, 45], [30, 46], [27, 47], [17, 6], [14, 7], [11, 8], [24, 18], [25, 21], [26, 24], [21, 19], [22, 22], [23, 25], [18, 20], [19, 23], [20, 26]]
bMove = [[0, 15], [1, 12], [2, 9], [51, 35], [52, 32], [53, 29], [35, 2], [32, 1], [29, 0], [15, 53], [12, 52], [9, 51], [44, 42], [43, 39], [42, 36], [41, 43], [40, 40], [39, 37], [38, 44], [37, 41], [36, 38]]
upMove = [[0, 6], [1, 3], [2, 0], [3, 7], [4, 4], [5, 1], [6, 8], [7, 5], [8, 2], [29, 38], [28, 37], [27, 36], [9, 18], [10, 19], [11, 20], [18, 27], [19, 28], [20, 29], [38, 11], [37, 10], [36, 9]]
dpMove = [[51, 53], [52, 50], [53, 47], [48, 52], [49, 49], [50, 46], [45, 51], [46, 48], [47, 45], [35, 26], [34, 25], [33, 24], [15, 42], [16, 43], [17, 44], [24, 15], [25, 16], [26, 17], [44, 35], [43, 34], [42, 33]]
lpMove = [[0, 44], [3, 41], [6, 38], [51, 24], [48, 21], [45, 18], [15, 17], [12, 16], [9, 15], [16, 14], [13, 13], [10, 12], [17, 11], [14, 10], [11, 9], [24, 6], [21, 3], [18, 0], [44, 45], [41, 48], [38, 51]]
rpMove = [[2, 20], [5, 23], [8, 26], [53, 36], [50, 39], [47, 42], [35, 29], [32, 28], [29, 27], [34, 32], [31, 31], [28, 30], [33, 35], [30, 34], [27, 33], [26, 53], [23, 50], [20, 47], [42, 2], [39, 5], [36, 8]]
fpMove = [[6, 17], [7, 14], [8, 11], [45, 33], [46, 30], [47, 27], [33, 8], [30, 7], [27, 6], [17, 47], [14, 46], [11, 45], [24, 26], [25, 23], [26, 20], [21, 25], [22, 22], [23, 19], [18, 24], [19, 21], [20, 18]]
bpMove = [[0, 29], [1, 32], [2, 35], [51, 9], [52, 12], [53, 15], [35, 51], [32, 52], [29, 53], [15, 0], [12, 1], [9, 2], [44, 38], [43, 41], [42, 44], [41, 37], [40, 40], [39, 43], [38, 36], [37, 39], [36, 42]]
u2Move = [[0, 8], [1, 7], [2, 6], [3, 5], [4, 4], [5, 3], [6, 2], [7, 1], [8, 0], [29, 11], [28, 10], [27, 9], [9, 27], [10, 28], [11, 29], [18, 36], [19, 37], [20, 38], [38, 20], [37, 19], [36, 18]]
d2Move = [[51, 47], [52, 46], [53, 45], [48, 50], [49, 49], [50, 48], [45, 53], [46, 52], [47, 51], [35, 17], [34, 16], [33, 15], [15, 33], [16, 34], [17, 35], [24, 42], [25, 43], [26, 44], [44, 26], [43, 25], [42, 24]]
l2Move = [[0, 45], [3, 48], [6, 51], [51, 6], [48, 3], [45, 0], [15, 11], [12, 14], [9, 17], [16, 10], [13, 13], [10, 16], [17, 9], [14, 12], [11, 15], [24, 38], [21, 41], [18, 44], [44, 18], [41, 21], [38, 24]]
r2Move = [[2, 47], [5, 50], [8, 53], [53, 8], [50, 5], [47, 2], [35, 27], [32, 30], [29, 33], [34, 28], [31, 31], [28, 34], [33, 29], [30, 32], [27, 35], [26, 36], [23, 39], [20, 42], [42, 20], [39, 23], [36, 26]]
f2Move = [[6, 47], [7, 46], [8, 45], [45, 8], [46, 7], [47, 6], [33, 11], [30, 14], [27, 17], [17, 27], [14, 30], [11, 33], [24, 20], [25, 19], [26, 18], [21, 23], [22, 22], [23, 21], [18, 26], [19, 25], [20, 24]]
b2Move = [[0, 53], [1, 52], [2, 51], [51, 2], [52, 1], [53, 0], [35, 9], [32, 12], [29, 15], [15, 29], [12, 32], [9, 35], [44, 36], [43, 37], [42, 38], [41, 39], [40, 40], [39, 41], [38, 42], [37, 43], [36, 44]]

u = gMove("U", np.array([0, 1, 0]),  270,  lambda pos: pos[y] > 0)
d = gMove("D", np.array([0, -1, 0]), 270,  lambda pos: pos[y] < 0)
r = gMove("R", np.array([1, 0, 0]),  270,  lambda pos: pos[x] > 0)
l = gMove("L", np.array([-1, 0, 0]), 270,  lambda pos: pos[x] < 0)
f = gMove("F", np.array([0, 0, 1]),  270,  lambda pos: pos[z] > 0)
b = gMove("B", np.array([0, 0, -1]), 270,  lambda pos: pos[z] < 0)
up = gMove("U'", np.array([0, 1, 0]),  90,  lambda pos: pos[y] > 0)
dp = gMove("D'", np.array([0, -1, 0]), 90,  lambda pos: pos[y] < 0)
rp = gMove("R'", np.array([1, 0, 0]),  90,  lambda pos: pos[x] > 0)
lp = gMove("L'", np.array([-1, 0, 0]), 90,  lambda pos: pos[x] < 0)
fp = gMove("F'", np.array([0, 0, 1]),  90,  lambda pos: pos[z] > 0)
bp = gMove("B'", np.array([0, 0, -1]), 90,  lambda pos: pos[z] < 0)
u2 = gMove("U2", np.array([0, 1, 0]),  180,  lambda pos: pos[y] > 0)
d2 = gMove("D2", np.array([0, -1, 0]), 180,  lambda pos: pos[y] < 0)
r2 = gMove("R2", np.array([1, 0, 0]),  180,  lambda pos: pos[x] > 0)
l2 = gMove("L2", np.array([-1, 0, 0]), 180,  lambda pos: pos[x] < 0)
f2 = gMove("F2", np.array([0, 0, 1]),  180,  lambda pos: pos[z] > 0)
b2 = gMove("B2", np.array([0, 0, -1]), 180,  lambda pos: pos[z] < 0)

solvedCube = "UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD"
solvedGCube = [
    Sticker(np.array([x, 3, y]), np.array([x, 3, y])) if f == 0 else
    Sticker(np.array([x, -3, y]), np.array([x, -3, y])) if f == 1 else
    Sticker(np.array([3, x, y]), np.array([3, x, y])) if f == 2 else
    Sticker(np.array([-3, x, y]), np.array([-3, x, y])) if f == 3 else
    Sticker(np.array([x, y, 3]), np.array([x, y, 3])) if f == 4 else
    Sticker(np.array([x, y, -3]), np.array([x, y, -3]))
    for f in range(6)
    for i in range(3)
    for j in range(3)
    for x, y in [((-2 + j * 2), (-2 + i * 2))]
]

# --------------------------------- solver -----------------------------------------------
stdMoves = ["U", "U'", "U2", "D", "D'", "D2", "L", "L'", "L2", "R", "R'", "R2", "F", "F'", "F2", "B", "B'", "B2"]
ifCube = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53]

class SimpleSolver:
    def __init__(self, isSolved, candidateMoves):
        self.isSolved = isSolved
        self.moves = candidateMoves

# first block solver
fbPieces = [ S("L", 4), S("L", 5), S("L", 6), S("L", 7), S("L", 8), S("L", 9), S("F", 4), S("F", 7), S("B", 6), S("B", 9), S("D", 1), S("D", 4), S("D", 7)]
def fbIsSolved(fcube):
    FBFACES = getFacesFromIndex(fbPieces)
    for i in range(len(fbPieces)):
        if (fcube[fbPieces[i]] != FBFACES[i]):
            return False
    return True
simplefbSolver = SimpleSolver(fbIsSolved, stdMoves)

# depth first search
def solvedfs(solver, cube, solution, depthRemaining):
    print(solution)
    if solver.isSolved(cube):
        return solution.strip()
    if (depthRemaining == 0):
        return None
    for move in solver.moves:
        result = solvedfs(solver, applyMoveByLetter(cube, move), solution + " " + str(move), depthRemaining - 1,)
        if result != None:
            return result
    return None

# iteratively deepening dfs
def solveiddfs(solver, cube, depthLimit):
    for depth in range(depthLimit):
        solution = solvedfs(solver, cube, "", depth)
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
                solvedCube = applyMove(solvedCube, uMove)
                # applyGMove(solvedGCube, u)
                # solvedCube = convertGcube(solvedGCube)
            if event.key == pygame.K_r:
                solvedCube = applyMove(solvedCube, rMove)
                # applyGMove(solvedGCube, r)
                # solvedCube = convertGcube(solvedGCube)
            if event.key == pygame.K_l:
                solvedCube = applyMove(solvedCube, lMove)
                # applyGMove(solvedGCube, l)
                # solvedCube = convertGcube(solvedGCube)
            if event.key == pygame.K_d:
                solvedCube = applyMove(solvedCube, dMove)
                # applyGMove(solvedGCube, d)
                # solvedCube = convertGcube(solvedGCube)
            if event.key == pygame.K_f:
                solvedCube = applyMove(solvedCube, fMove)
                # applyGMove(solvedGCube, f)
                # solvedCube = convertGcube(solvedGCube)
            if event.key == pygame.K_b:
                solvedCube = applyMove(solvedCube, bMove)
                # applyGMove(solvedGCube, b)
                # solvedCube = convertGcube(solvedGCube)

            if event.key == pygame.K_g:
                solvedCube = applyFmovesByLetter(solvedCube, "L B F D")
                print(fbIsSolved(solvedCube))                
                startTime = time.perf_counter()
                solution = solveiddfs(simplefbSolver, solvedCube, 4)
                endTime = time.perf_counter()
                print (solution)
                solvedCube = applyFmovesByLetter(solvedCube, solution)
                
                totalTime = endTime - startTime
                print(f"Solved in {totalTime:.0f} seconds")

            # test efficiency of model types
            #Facelet model: 
            # 100026 moves in 108 miliseconds 922237.76 Moves per sec
            # Geometric model: 
            # 100026 moves in 69620 miliseconds 1436.74 Moves per sec
            loops = 5555
            if event.key == pygame.K_t:
                print("----------------------------------")
                moveCount = loops * 18
                startTime = time.perf_counter()
                for i in range(loops): solvedCube = applyFmoves(solvedCube, [uMove, dMove, lMove, rMove, fMove, bMove, upMove, dpMove, lpMove, rpMove, fpMove, bpMove, u2Move, d2Move, l2Move, r2Move, f2Move, b2Move])
                endTime = time.perf_counter()

                totalTime = endTime - startTime
                rate = (moveCount / totalTime) / 1000000
                print("Facelet model: ")
                print(f"{moveCount:.0f} moves in {totalTime * 1000:.0f} miliseconds {rate:.2f} Moves (million) per sec")


                startTime = time.perf_counter()
                for i in range(loops): applyGmoves(solvedGCube, [u, d, l, r, f, b, up, dp, lp, rp, fp, bp, u2, d2, l2, r2, f2, b2])
                endTime = time.perf_counter()

                totalTime = endTime - startTime
                rate = (moveCount / totalTime) / 1000000
                print("Geometric model: ")
                print(f"{moveCount:.0f} moves in {totalTime * 1000:.0f} miliseconds {rate:.2f} Moves (million) per sec")
                solvedCube = convertGcube(solvedGCube)



    # fill the screen with a color to wipe away anything from last frame
    screen.fill((100,100,100))

    drawState(solvedCube)
    
    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()