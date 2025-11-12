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
uOffset = (size * 4, size * 0)
lOffset = (size * 0, size * 4)
fOffset = (size * 4, size * 4)
rOffset = (size * 8, size * 4)
bOffset = (size * 12, size * 4)
dOffset = (size * 4, size * 8)
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
    elif face == "L" : index = idx + 16
    elif face == "F" : index = idx + 32
    elif face == "R" : index = idx + 48
    elif face == "B" : index = idx + 64
    elif face == "D" : index = idx + 80
    return (index)

# recieve a list of indicies and return a string of faces for each index
def getFacesFromIndex(indexs):
    string = ""
    for index in indexs:
        if   index >= 80: string += "D"
        elif index >= 64: string += "B"
        elif index >= 48: string += "R"
        elif index >= 32: string += "F"
        elif index >= 16:  string += "L"
        elif index >= 0:  string += "U"
    return string

# take a string to display the state of the cube
def drawState (state, globalxOffset, globalyOffset):
    offset = uOffset
    color = ()
    for i in range(len(state)):
        sticker = state[i]
        if   i > 79: offset = dOffset
        elif i > 63: offset = bOffset
        elif i > 47: offset = rOffset
        elif i > 31: offset = fOffset
        elif i > 15: offset = lOffset
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
        xOffset = (i % 4) * size
        if (i % 4 == 0) and (i > 0): yOffset += size
        if i % 16 == 0: yOffset = 0
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

# apply a list of moves to an IF cube list
def applyFmoves(cube, moves):
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
    if face == "U": return sorted([s for s in gcube if s.pos[y] == 4],  key=lambda s: ( s.pos[z],  s.pos[x]))
    if face == "D": return sorted([s for s in gcube if s.pos[y] == -4], key=lambda s: (-s.pos[z],  s.pos[x]))
    if face == "L": return sorted([s for s in gcube if s.pos[x] == -4], key=lambda s: (-s.pos[y],  s.pos[z]))
    if face == "R": return sorted([s for s in gcube if s.pos[x] == 4],  key=lambda s: (-s.pos[y], -s.pos[z]))
    if face == "F": return sorted([s for s in gcube if s.pos[z] == 4],  key=lambda s: (-s.pos[y],  s.pos[x])) 
    if face == "B": return sorted([s for s in gcube if s.pos[z] == -4], key=lambda s: (-s.pos[y], -s.pos[x]))

# return the face of the stickers position
def getFace(sticker):
    if (sticker.pos[y] == 4):
        return "U"
    elif (sticker.pos[y] == -4):
        return "D"
    elif (sticker.pos[x] == 4):
        return "R"
    elif (sticker.pos[x] == -4):
        return "L"
    elif (sticker.pos[z] == 4):
        return "F"
    elif (sticker.pos[z] == -4):
        return "B"

# return the face of the stickers destination
def getColor(sticker):
    if (sticker.dst[y] == 4):
        return "U"
    elif (sticker.dst[y] == -4):
        return "D"
    elif (sticker.dst[x] == 4):
        return "R"
    elif (sticker.dst[x] == -4):
        return "L"
    elif (sticker.dst[z] == 4):
        return "F"
    elif (sticker.dst[z] == -4):
        return "B"

# ---------------------------------------- conversion functions -------------------------------------
# convert gcube to fcube
def convertGcube(gcube):
    sCube = []
    uFace = sortFace(gcube, "U")
    dFace = sortFace(gcube, "D")
    lFace = sortFace(gcube, "L")
    rFace = sortFace(gcube, "R")
    fFace = sortFace(gcube, "F") 
    bFace = sortFace(gcube, "B")

    # Build ULFRBD order
    for face in [uFace, lFace, fFace, rFace, bFace, dFace]:
        for sticker in face:
            sCube.append(getColor(sticker))
    return sCube

# ------------------------------ define solved cubes and legal moves --------------------------
# moves defined by permutation pairs
fMoves = {  "U":   [],
            "D":   [],
            "L":   [],
            "R":   [],
            "F":   [],
            "B":   [],
            "U'":  [],
            "D'":  [],
            "L'":  [],
            "R'":  [],
            "F'":  [],
            "B'":  [],
            "U2":  [],
            "D2":  [],
            "L2":  [],
            "R2":  [],
            "F2":  [],
            "B2":  [],
            "Uw":  [],
            "Dw":  [],
            "Lw":  [],
            "Rw":  [],
            "Fw":  [],
            "Bw":  [],
            "Uw'": [],
            "Dw'": [],
            "Lw'": [],
            "Rw'": [],
            "Fw'": [],
            "Bw'": [],
            "Uw2": [],
            "Dw2": [],
            "Lw2": [],
            "Rw2": [],
            "Fw2": [],
            "Bw2": [] }

gMoves = {  "U":  gMove("U", np.array([0, 2, 0]),  270,  lambda pos: pos[y] > 1),
            "D":  gMove("D", np.array([0, -2, 0]), 270,  lambda pos: pos[y] < -1),
            "R":  gMove("R", np.array([1, 0, 0]),  270,  lambda pos: pos[x] > 1),
            "L":  gMove("L", np.array([-1, 0, 0]), 270,  lambda pos: pos[x] < -1),
            "F":  gMove("F", np.array([0, 0, 1]),  270,  lambda pos: pos[z] > 1),
            "B":  gMove("B", np.array([0, 0, -1]), 270,  lambda pos: pos[z] < -1),
            "U'": gMove("U'", np.array([0, 1, 0]),  90,  lambda pos: pos[y] > 1),
            "D'": gMove("D'", np.array([0, -1, 0]), 90,  lambda pos: pos[y] < -1),
            "R'": gMove("R'", np.array([1, 0, 0]),  90,  lambda pos: pos[x] > 1),
            "L'": gMove("L'", np.array([-1, 0, 0]), 90,  lambda pos: pos[x] < -1),
            "F'": gMove("F'", np.array([0, 0, 1]),  90,  lambda pos: pos[z] > 1),
            "B'": gMove("B'", np.array([0, 0, -1]), 90,  lambda pos: pos[z] < -1),
            "U2": gMove("U2", np.array([0, 1, 0]),  180,  lambda pos: pos[y] > 1),
            "D2": gMove("D2", np.array([0, -1, 0]), 180,  lambda pos: pos[y] < -1),
            "R2": gMove("R2", np.array([1, 0, 0]),  180,  lambda pos: pos[x] > 1),
            "L2": gMove("L2", np.array([-1, 0, 0]), 180,  lambda pos: pos[x] < -1),
            "F2": gMove("F2", np.array([0, 0, 1]),  180,  lambda pos: pos[z] > 1),
            "B2": gMove("B2", np.array([0, 0, -1]), 180,  lambda pos: pos[z] < -1), 
            "Uw":  gMove("Uw", np.array([0, 1, 0]),  270,  lambda pos: pos[y] > 0),
            "Dw":  gMove("Dw", np.array([0, -1, 0]), 270,  lambda pos: pos[y] < 0),
            "Rw":  gMove("Rw", np.array([1, 0, 0]),  270,  lambda pos: pos[x] > 0),
            "Lw":  gMove("Lw", np.array([-1, 0, 0]), 270,  lambda pos: pos[x] < 0),
            "Fw":  gMove("Fw", np.array([0, 0, 1]),  270,  lambda pos: pos[z] > 0),
            "Bw":  gMove("Bw", np.array([0, 0, -1]), 270,  lambda pos: pos[z] < 0),
            "Uw'": gMove("Uw'", np.array([0, 1, 0]),  90,  lambda pos: pos[y] > 0),
            "Dw'": gMove("Dw'", np.array([0, -1, 0]), 90,  lambda pos: pos[y] < 0),
            "Rw'": gMove("Rw'", np.array([1, 0, 0]),  90,  lambda pos: pos[x] > 0),
            "Lw'": gMove("Lw'", np.array([-1, 0, 0]), 90,  lambda pos: pos[x] < 0),
            "Fw'": gMove("Fw'", np.array([0, 0, 1]),  90,  lambda pos: pos[z] > 0),
            "Bw'": gMove("Bw'", np.array([0, 0, -1]), 90,  lambda pos: pos[z] < 0),
            "Uw2": gMove("Uw2", np.array([0, 1, 0]),  180,  lambda pos: pos[y] > 0),
            "Dw2": gMove("Dw2", np.array([0, -1, 0]), 180,  lambda pos: pos[y] < 0),
            "Rw2": gMove("Rw2", np.array([1, 0, 0]),  180,  lambda pos: pos[x] > 0),
            "Lw2": gMove("Lw2", np.array([-1, 0, 0]), 180,  lambda pos: pos[x] < 0),
            "Fw2": gMove("Fw2", np.array([0, 0, 1]),  180,  lambda pos: pos[z] > 0),
            "Bw2": gMove("Bw2", np.array([0, 0, -1]), 180,  lambda pos: pos[z] < 0), }

solvedCube = list("UUUUUUUUUUUUUUUULLLLLLLLLLLLLLLLFFFFFFFFFFFFFFFFRRRRRRRRRRRRRRRRBBBBBBBBBBBBBBBBDDDDDDDDDDDDDDDD")

solvedGCube = [ Sticker(np.array([x, 4, y]), np.array([x, 4, y])) if f == 0 else
                Sticker(np.array([x, -4, y]), np.array([x, -4, y])) if f == 1 else
                Sticker(np.array([4, x, y]), np.array([4, x, y])) if f == 2 else
                Sticker(np.array([-4, x, y]), np.array([-4, x, y])) if f == 3 else
                Sticker(np.array([x, y, 4]), np.array([x, y, 4])) if f == 4 else
                Sticker(np.array([x, y, -4]), np.array([x, y, -4]))
                for f in range(6)
                for i in range(4)
                for j in range(4)
                for x, y in [((-3 + j * 2), (-3 + i * 2))] ]
# --------------------------------- solver -----------------------------------------------
stdMoves = ["U", "U'", "U2", "D", "D'", "D2", "L", "L'", "L2", "R", "R'", "R2", "F", "F'", "F2", "B", "B'", "B2"]
ifCube = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53]
cornerPeices = [0, 2, 6, 8, 45, 47, 51, 53, 9, 11, 15, 17, 27, 29, 33, 35, 36, 38, 42, 44, 18, 20, 24, 26]
edgePeices = [10, 12, 14, 16, 19, 21, 23, 25, 28, 30, 32, 34, 37, 39, 41, 43]

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

# solvers require a function to determine if a state is solved, permitted moves, pruning table, 
# depth of the pruningtable, and what peices the solver needs to look at
class SimpleSolver:
    def __init__(self, isSolved, candidateMoves, pruningTable, pruningDepth, pieces):
        self.isSolved = isSolved
        self.moves = candidateMoves
        self.pruningTable = pruningTable
        self.pruningDepth = pruningDepth
        self.pieces = pieces

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
# function to actually solve positions
# requires a solver object, a cube and search depth limit
# peices of the cube that dont change the state should be left gray(X) 
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
                applyGmoves(solvedGCube, "")
                solvedCube = convertGcube(solvedGCube)


    # fill the screen with a color to wipe away anything from last frame
    screen.fill((100,100,100))

    drawState(solvedCube, 100, 100)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()