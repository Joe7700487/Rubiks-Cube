# 4x4 solver
import pygame
import numpy as np
import math
import time
import f2cPruningTable
import l4cPruningTable

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
size = 15
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

def getIndexPos(gcube, sticker):
    face = getFace(sticker)
    stickers = sortFace(gcube, face)
    for s in stickers:
        if s.pos[x] == sticker.pos[x] and s.pos[y] == sticker.pos[y] and s.pos[z] == sticker.pos[z]:
            index = stickers.index(s)
            return S(face, index + 1)
def getIndexDst(gcube, sticker):
    stickers = sortFace(gcube, "U") + sortFace(gcube, "L") + sortFace(gcube, "F") + sortFace(gcube, "R") + sortFace(gcube, "B") + sortFace(gcube, "D")
    for s in stickers:
        if s.pos[x] == sticker.dst[x] and s.pos[y] == sticker.dst[y] and s.pos[z] == sticker.dst[z]:
            face = getFace(s)
            stickers = sortFace(gcube, face)
            index = stickers.index(s)
            return S(face, index + 1)

def convertGmove(gMove, gCube):
    move = []
    applyGMove(gCube, gMove.name)
    for sticker in gCube:
        if gMove.predicate(sticker.pos):
            move.append([getIndexDst(gCube, sticker), getIndexPos(gCube, sticker)])
    print("'" + gMove.name + "': " + str(move) + ",")

# ------------------------------ define solved cubes and legal moves --------------------------
# moves defined by permutation pairs
fMoves = {  "U": [[0, 3], [1, 7], [2, 11], [3, 15], [4, 2], [5, 6], [6, 10], [7, 14], [8, 1], [9, 5], [10, 9], [11, 13], [12, 0], [13, 4], [14, 8], [15, 12], [51, 35], [50, 34], [49, 33], [48, 32], [16, 64], [17, 65], [18, 66], [19, 67], [32, 16], [33, 17], [34, 18], [35, 19], [67, 51], [66, 50], [65, 49], [64, 48]],
            "U'": [[0, 12], [1, 8], [2, 4], [3, 0], [4, 13], [5, 9], [6, 5], [7, 1], [8, 14], [9, 10], [10, 6], [11, 2], [12, 15], [13, 11], [14, 7], [15, 3], [51, 67], [50, 66], [49, 65], [48, 64], [16, 32], [17, 33], [18, 34], [19, 35], [32, 48], [33, 49], [34, 50], [35, 51], [67, 19], [66, 18], [65, 17], [64, 16]],
            "U2": [[0, 15], [1, 14], [2, 13], [3, 12], [4, 11], [5, 10], [6, 9], [7, 8], [8, 7], [9, 6], [10, 5], [11, 4], [12, 3], [13, 2], [14, 1], [15, 0], [51, 19], [50, 18], [49, 17], [48, 16], [16, 48], [17, 49], [18, 50], [19, 51], [32, 64], [33, 65], [34, 66], [35, 67], [67, 35], [66, 34], [65, 33], [64, 32]],
            "D": [[92, 80], [93, 84], [94, 88], [95, 92], [88, 81], [89, 85], [90, 89], [91, 93], [84, 82], [85, 86], [86, 90], [87, 94], [80, 83], [81, 87], [82, 91], [83, 95], [63, 79], [62, 78], [61, 77], [60, 76], [28, 44], [29, 45], [30, 46], [31, 47], [44, 60], [45, 61], [46, 62], [47, 63], [79, 31], [78, 30], [77, 29], [76, 28]],
            "D'": [[92, 95], [93, 91], [94, 87], [95, 83], [88, 94], [89, 90], [90, 86], [91, 82], [84, 93], [85, 89], [86, 85], [87, 81], [80, 92], [81, 88], [82, 84], [83, 80], [63, 47], [62, 46], [61, 45], [60, 44], [28, 76], [29, 77], [30, 78], [31, 79], [44, 28], [45, 29], [46, 30], [47, 31], [79, 63], [78, 62], [77, 61], [76, 60]],
            "D2": [[92, 83], [93, 82], [94, 81], [95, 80], [88, 87], [89, 86], [90, 85], [91, 84], [84, 91], [85, 90], [86, 89], [87, 88], [80, 95], [81, 94], [82, 93], [83, 92], [63, 31], [62, 30], [61, 29], [60, 28], [28, 60], [29, 61], [30, 62], [31, 63], [44, 76], [45, 77], [46, 78], [47, 79], [79, 47], [78, 46], [77, 45], [76, 44]],
            "L": [[0, 32], [4, 36], [8, 40], [12, 44], [92, 67], [88, 71], [84, 75], [80, 79], [28, 16], [24, 17], [20, 18], [16, 19], [29, 20], [25, 21], [21, 22], [17, 23], [30, 24], [26, 25], [22, 26], [18, 27], [31, 28], [27, 29], [23, 30], [19, 31], [44, 92], [40, 88], [36, 84], [32, 80], [79, 0], [75, 4], [71, 8], [67, 12]],
            "L'": [[0, 79], [4, 75], [8, 71], [12, 67], [92, 44], [88, 40], [84, 36], [80, 32], [28, 31], [24, 30], [20, 29], [16, 28], [29, 27], [25, 26], [21, 25], [17, 24], [30, 23], [26, 22], [22, 21], [18, 20], [31, 19], [27, 18], [23, 17], [19, 16], [44, 12], [40, 8], [36, 4], [32, 0], [79, 80], [75, 84], [71, 88], [67, 92]],
            "L2": [[0, 80], [4, 84], [8, 88], [12, 92], [92, 12], [88, 8], [84, 4], [80, 0], [28, 19], [24, 23], [20, 27], [16, 31], [29, 18], [25, 22], [21, 26], [17, 30], [30, 17], [26, 21], [22, 25], [18, 29], [31, 16], [27, 20], [23, 24], [19, 28], [44, 67], [40, 71], [36, 75], [32, 79], [79, 32], [75, 36], [71, 40], [67, 44]],
            "R": [[3, 76], [7, 72], [11, 68], [15, 64], [95, 47], [91, 43], [87, 39], [83, 35], [63, 60], [59, 61], [55, 62], [51, 63], [62, 56], [58, 57], [54, 58], [50, 59], [61, 52], [57, 53], [53, 54], [49, 55], [60, 48], [56, 49], [52, 50], [48, 51], [47, 15], [43, 11], [39, 7], [35, 3], [76, 83], [72, 87], [68, 91], [64, 95]],
            "R'": [[3, 35], [7, 39], [11, 43], [15, 47], [95, 64], [91, 68], [87, 72], [83, 76], [63, 51], [59, 50], [55, 49], [51, 48], [62, 55], [58, 54], [54, 53], [50, 52], [61, 59], [57, 58], [53, 57], [49, 56], [60, 63], [56, 62], [52, 61], [48, 60], [47, 95], [43, 91], [39, 87], [35, 83], [76, 3], [72, 7], [68, 11], [64, 15]],
            "R2": [[3, 83], [7, 87], [11, 91], [15, 95], [95, 15], [91, 11], [87, 7], [83, 3], [63, 48], [59, 52], [55, 56], [51, 60], [62, 49], [58, 53], [54, 57], [50, 61], [61, 50], [57, 54], [53, 58], [49, 62], [60, 51], [56, 55], [52, 59], [48, 63], [47, 64], [43, 68], [39, 72], [35, 76], [76, 35], [72, 39], [68, 43], [64, 47]],
            "F": [[12, 48], [13, 52], [14, 56], [15, 60], [80, 19], [81, 23], [82, 27], [83, 31], [60, 80], [56, 81], [52, 82], [48, 83], [31, 12], [27, 13], [23, 14], [19, 15], [44, 32], [45, 36], [46, 40], [47, 44], [40, 33], [41, 37], [42, 41], [43, 45], [36, 34], [37, 38], [38, 42], [39, 46], [32, 35], [33, 39], [34, 43], [35, 47]],
            "F'": [[12, 31], [13, 27], [14, 23], [15, 19], [80, 60], [81, 56], [82, 52], [83, 48], [60, 15], [56, 14], [52, 13], [48, 12], [31, 83], [27, 82], [23, 81], [19, 80], [44, 47], [45, 43], [46, 39], [47, 35], [40, 46], [41, 42], [42, 38], [43, 34], [36, 45], [37, 41], [38, 37], [39, 33], [32, 44], [33, 40], [34, 36], [35, 32]],
            "F2": [[12, 83], [13, 82], [14, 81], [15, 80], [80, 15], [81, 14], [82, 13], [83, 12], [60, 19], [56, 23], [52, 27], [48, 31], [31, 48], [27, 52], [23, 56], [19, 60], [44, 35], [45, 34], [46, 33], [47, 32], [40, 39], [41, 38], [42, 37], [43, 36], [36, 43], [37, 42], [38, 41], [39, 40], [32, 47], [33, 46], [34, 45], [35, 44]],
            "B": [[0, 28], [1, 24], [2, 20], [3, 16], [92, 63], [93, 59], [94, 55], [95, 51], [63, 3], [59, 2], [55, 1], [51, 0], [28, 95], [24, 94], [20, 93], [16, 92], [79, 76], [78, 72], [77, 68], [76, 64], [75, 77], [74, 73], [73, 69], [72, 65], [71, 78], [70, 74], [69, 70], [68, 66], [67, 79], [66, 75], [65, 71], [64, 67]],
            "B'": [[0, 51], [1, 55], [2, 59], [3, 63], [92, 16], [93, 20], [94, 24], [95, 28], [63, 92], [59, 93], [55, 94], [51, 95], [28, 0], [24, 1], [20, 2], [16, 3], [79, 67], [78, 71], [77, 75], [76, 79], [75, 66], [74, 70], [73, 74], [72, 78], [71, 65], [70, 69], [69, 73], [68, 77], [67, 64], [66, 68], [65, 72], [64, 76]],
            "B2": [[0, 95], [1, 94], [2, 93], [3, 92], [92, 3], [93, 2], [94, 1], [95, 0], [63, 16], [59, 20], [55, 24], [51, 28], [28, 51], [24, 55], [20, 59], [16, 63], [79, 64], [78, 65], [77, 66], [76, 67], [75, 68], [74, 69], [73, 70], [72, 71], [71, 72], [70, 73], [69, 74], [68, 75], [67, 76], [66, 77], [65, 78], [64, 79]],
            "Uw": [[0, 3], [1, 7], [2, 11], [3, 15], [4, 2], [5, 6], [6, 10], [7, 14], [8, 1], [9, 5], [10, 9], [11, 13], [12, 0], [13, 4], [14, 8], [15, 12], [55, 39], [51, 35], [54, 38], [50, 34], [53, 37], [49, 33], [52, 36], [48, 32], [20, 68], [16, 64], [21, 69], [17, 65], [22, 70], [18, 66], [23, 71], [19, 67], [36, 20], [37, 21], [38, 22], [39, 23], [32, 16], [33, 17], [34, 18], [35, 19], [71, 55], [70, 54], [69, 53], [68, 52], [67, 51], [66, 50], [65, 49], [64, 48]],
            "Uw'": [[0, 12], [1, 8], [2, 4], [3, 0], [4, 13], [5, 9], [6, 5], [7, 1], [8, 14], [9, 10], [10, 6], [11, 2], [12, 15], [13, 11], [14, 7], [15, 3], [55, 71], [51, 67], [54, 70], [50, 66], [53, 69], [49, 65], [52, 68], [48, 64], [20, 36], [16, 32], [21, 37], [17, 33], [22, 38], [18, 34], [23, 39], [19, 35], [36, 52], [37, 53], [38, 54], [39, 55], [32, 48], [33, 49], [34, 50], [35, 51], [71, 23], [70, 22], [69, 21], [68, 20], [67, 19], [66, 18], [65, 17], [64, 16]],
            "Uw2": [[0, 15], [1, 14], [2, 13], [3, 12], [4, 11], [5, 10], [6, 9], [7, 8], [8, 7], [9, 6], [10, 5], [11, 4], [12, 3], [13, 2], [14, 1], [15, 0], [55, 23], [51, 19], [54, 22], [50, 18], [53, 21], [49, 17], [52, 20], [48, 16], [20, 52], [16, 48], [21, 53], [17, 49], [22, 54], [18, 50], [23, 55], [19, 51], [36, 68], [37, 69], [38, 70], [39, 71], [32, 64], [33, 65], [34, 66], [35, 67], [71, 39], [70, 38], [69, 37], [68, 36], [67, 35], [66, 34], [65, 33], [64, 32]],
            "Rw": [[2, 77], [3, 76], [6, 73], [7, 72], [10, 69], [11, 68], [14, 65], [15, 64], [94, 46], [95, 47], [90, 42], [91, 43], [86, 38], [87, 39], [82, 34], [83, 35], [63, 60], [59, 61], [55, 62], [51, 63], [62, 56], [58, 57], [54, 58], [50, 59], [61, 52], [57, 53], [53, 54], [49, 55], [60, 48], [56, 49], [52, 50], [48, 51], [46, 14], [47, 15], [42, 10], [43, 11], [38, 6], [39, 7], [34, 2], [35, 3], [77, 82], [76, 83], [73, 86], [72, 87], [69, 90], [68, 91], [65, 94], [64, 95]],
            "Rw'": [[2, 34], [3, 35], [6, 38], [7, 39], [10, 42], [11, 43], [14, 46], [15, 47], [94, 65], [95, 64], [90, 69], [91, 68], [86, 73], [87, 72], [82, 77], [83, 76], [63, 51], [59, 50], [55, 49], [51, 48], [62, 55], [58, 54], [54, 53], [50, 52], [61, 59], [57, 58], [53, 57], [49, 56], [60, 63], [56, 62], [52, 61], [48, 60], [46, 94], [47, 95], [42, 90], [43, 91], [38, 86], [39, 87], [34, 82], [35, 83], [77, 2], [76, 3], [73, 6], [72, 7], [69, 10], [68, 11], [65, 14], [64, 15]],
            "Rw2": [[2, 82], [3, 83], [6, 86], [7, 87], [10, 90], [11, 91], [14, 94], [15, 95], [94, 14], [95, 15], [90, 10], [91, 11], [86, 6], [87, 7], [82, 2], [83, 3], [63, 48], [59, 52], [55, 56], [51, 60], [62, 49], [58, 53], [54, 57], [50, 61], [61, 50], [57, 54], [53, 58], [49, 62], [60, 51], [56, 55], [52, 59], [48, 63], [46, 65], [47, 64], [42, 69], [43, 68], [38, 73], [39, 72], [34, 77], [35, 76], [77, 34], [76, 35], [73, 38], [72, 39], [69, 42], [68, 43], [65, 46], [64, 47]],
            "Fw": [[8, 49], [9, 53], [10, 57], [11, 61], [12, 48], [13, 52], [14, 56], [15, 60], [84, 18], [85, 22], [86, 26], [87, 30], [80, 19], [81, 23], [82, 27], [83, 31], [61, 84], [57, 85], [53, 86], [49, 87], [60, 80], [56, 81], [52, 82], [48, 83], [30, 8], [26, 9], [22, 10], [18, 11], [31, 12], [27, 13], [23, 14], [19, 15], [44, 32], [45, 36], [46, 40], [47, 44], [40, 33], [41, 37], [42, 41], [43, 45], [36, 34], [37, 38], [38, 42], [39, 46], [32, 35], [33, 39], [34, 43], [35, 47]],
            "Fw'": [[8, 30], [9, 26], [10, 22], [11, 18], [12, 31], [13, 27], [14, 23], [15, 19], [84, 61], [85, 57], [86, 53], [87, 49], [80, 60], [81, 56], [82, 52], [83, 48], [61, 11], [57, 10], [53, 9], [49, 8], [60, 15], [56, 14], [52, 13], [48, 12], [30, 87], [26, 86], [22, 85], [18, 84], [31, 83], [27, 82], [23, 81], [19, 80], [44, 47], [45, 43], [46, 39], [47, 35], [40, 46], [41, 42], [42, 38], [43, 34], [36, 45], [37, 41], [38, 37], [39, 33], [32, 44], [33, 40], [34, 36], [35, 32]],
            "Fw2": [[8, 87], [9, 86], [10, 85], [11, 84], [12, 83], [13, 82], [14, 81], [15, 80], [84, 11], [85, 10], [86, 9], [87, 8], [80, 15], [81, 14], [82, 13], [83, 12], [61, 18], [57, 22], [53, 26], [49, 30], [60, 19], [56, 23], [52, 27], [48, 31], [30, 49], [26, 53], [22, 57], [18, 61], [31, 48], [27, 52], [23, 56], [19, 60], [44, 35], [45, 34], [46, 33], [47, 32], [40, 39], [41, 38], [42, 37], [43, 36], [36, 43], [37, 42], [38, 41], [39, 40], [32, 47], [33, 46], [34, 45], [35, 44]],}

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
            "Rw":  gMove("Rw", np.array([1, 0, 0]),  270,  lambda pos: pos[x] > 0),
            "Fw":  gMove("Fw", np.array([0, 0, 1]),  270,  lambda pos: pos[z] > 0),
            "Uw'": gMove("Uw'", np.array([0, 1, 0]),  90,  lambda pos: pos[y] > 0),
            "Rw'": gMove("Rw'", np.array([1, 0, 0]),  90,  lambda pos: pos[x] > 0),
            "Fw'": gMove("Fw'", np.array([0, 0, 1]),  90,  lambda pos: pos[z] > 0),
            "Uw2": gMove("Uw2", np.array([0, 1, 0]),  180,  lambda pos: pos[y] > 0),
            "Rw2": gMove("Rw2", np.array([1, 0, 0]),  180,  lambda pos: pos[x] > 0),
            "Fw2": gMove("Fw2", np.array([0, 0, 1]),  180,  lambda pos: pos[z] > 0) }

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
stdMoves = ["U", "U'", "U2", "D", "D'", "D2", "L", "L'", "L2", "R", "R'", "R2", "F", "F'", "F2", "B", "B'", "B2",
            "Uw", "Uw'", "Uw2", "Rw", "Rw'", "Rw2", "Fw", "Fw'", "Fw2"]
ifCube = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 
          16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 
          32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 
          48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 
          64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 
          80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95]
centers = [5, 6, 9, 10, 
           21, 22, 25, 26, 
           37, 38, 41, 42, 
           53, 54, 57, 58, 
           69, 70, 73, 74, 
           85, 86, 89, 90]


def genPruningTable(solvedStates, depth, moveset, name):
    pruningTable = {}
    previousFrontier = solvedStates

    for state in solvedStates:
        pruningTable["".join(state)] = 0

    for i in range(1, depth + 1):
        frontier = []
        for state in previousFrontier:
            for move in moveset:
                newState = "".join(applyFmoves(list(state), move))
                if(newState not in pruningTable):
                    pruningTable[newState] = i
                    frontier.append(newState)
        previousFrontier = frontier

    with open(name + ".py", "w") as file:
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
        self.pruningDepth = pruningDepth # max depth of the pruning table
        self.pieces = pieces

# first 2 centers opposite
first2centers = [5, 6, 9, 10, 85, 86, 89, 90]
def centersIsSolved (mask, pieces):
    if mask == ['X', 'X', 'X', 'X', 'X', 'U', 'U', 'X', 'X', 'U', 'U', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'U', 'U', 'X', 'X', 'U', 'U', 'X', 'X', 'X', 'X', 'X']:
        return True
    else: return False
f2cMask = list("U" if i in first2centers else "X" for i in ifCube)
# genPruningTable([f2cMask], 7, stdMoves, "f2cPruningTable")
f2cSolver = SimpleSolver(centersIsSolved, stdMoves, f2cPruningTable.table, 6, centers)

# last 4 centers opposite
l4cMoves = ["U", "U'", "U2", "D", "D'", "D2", "L", "L'", "L2", "R", "R'", "R2", "F", "F'", "F2", "B", "B'", "B2",
            "Uw", "Uw'", "Uw2"]
last4centers = [ 21, 22, 25, 26, 37, 38, 41, 42, 53, 54, 57, 58, 69, 70, 73, 74, ]
def l4cIsSolved (mask, pieces):
    if mask == ['X', 'X', 'X', 'X', 'X', 'U', 'U', 'X', 'X', 'U', 'U', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'R', 'R', 'X', 'X', 'R', 'R', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'F', 'F', 'X', 'X', 'F', 'F', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'R', 'R', 'X', 'X', 'R', 'R', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'F', 'F', 'X', 'X', 'F', 'F', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'U', 'U', 'X', 'X', 'U', 'U', 'X', 'X', 'X', 'X', 'X']:
        return True
    else: return False
l4cMask = []
# for i in range(len(ifCube)):
#     if ifCube[i] in centers:
#         face = getFacesFromIndex([ifCube[i]])
#         if face == "L": face = "R"
#         if face == "B": face = "F"
#         if face == "D": face = "U"
#         l4cMask.append(face)
#     else:
#         l4cMask.append("X")
# genPruningTable([l4cMask], 15, l4cMoves, "l4cPruningTable")
l4cSolver = SimpleSolver(l4cIsSolved, l4cMoves, l4cPruningTable.table, 9, centers)

## IMPORTANT FUNCTIONS
def solvedfsWithPruning(solver, cube, solution, depthRemaining):
    if solver.isSolved(cube, solver.pieces):
        return solution.strip()

    # pruning
    lowerBound = solver.pruningTable.get("".join(cube))
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
solvedCubeAfter = solvedCube
f2cMaskAfter = f2cMask
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_u:
                # applyGmoves(solvedGCube, "U'")
                # solvedCube = convertGcube(solvedGCube)
                solvedCube = applyFmoves(solvedCube, "Uw")
            if event.key == pygame.K_s:
                scramble = "Fw2 Uw2 L U R' Uw2 U Rw2 R' D L' R F2 B' D' Fw' Rw2 Uw' Rw R' U F' Rw' Uw F2"
                scramble += " U Fw R2 Uw L Rw Fw"

                solvedCube = applyFmoves(solvedCube, scramble)
                ifCube = applyFmoves(ifCube, scramble)
                # f2cMask = ["U" if st in first2centers else "X" for st in ifCube]
                # solution = solveiddfs2(f2cSolver, f2cMask, 10)

                l4cMask = []
                for i in range(len(ifCube)):
                    if ifCube[i] in centers:
                        face = getFacesFromIndex([ifCube[i]])
                        if face == "L": face = "R"
                        if face == "B": face = "F"
                        if face == "D": face = "U"
                        l4cMask.append(face)
                    else:
                        l4cMask.append("X")
                solution = solveiddfs2(l4cSolver, l4cMask, 10)

                if solution != None:
                    if len(solution) > 0:
                        print(solution, len(solution.split(" ")))
                        solvedCubeAfter = applyFmoves(solvedCube, solution)
                        f2cMaskAfter = applyFmoves(f2cMask, solution)
                    else:
                        print("alreayd solved")
                else:
                    print("NOt found")
                

    # fill the screen with a color to wipe away anything from last frame
    screen.fill((100,100,100))

    drawState(solvedCube, 100, 100)
    drawState(f2cMask, 100, 300)
    drawState(solvedCubeAfter, 400, 100)
    drawState(f2cMaskAfter, 400, 300)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()