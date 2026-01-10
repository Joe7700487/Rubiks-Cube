# Example file showing a circle moving on screen
import pygame
import numpy as np
import math

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
# UUURUUUFUUUFUUUF RRRBRRRBRRRBRRRB RRRDFFFDFFFDFFFD DDDBDDDBDDDBDDDL FFFFLLLLLLLLLLLL ULLLUBBBUBBBUBBB
# U face           R face           F face           D face           L face           B face
def S(face, idx):
    idx = idx - 1
    index = 0
    if face == "U": index = idx + 0
    elif face == "R" : index = idx + 16
    elif face == "F" : index = idx + 32
    elif face == "D" : index = idx + 48
    elif face == "L" : index = idx + 64
    elif face == "B" : index = idx + 80
    return (index)

# recieve a list of indicies and return a string of faces for each index
def getFacesFromIndex(indexs):
    string = ""
    for index in indexs:
        if   index >= 80: string += "B"
        elif index >= 64: string += "L"
        elif index >= 48: string += "D"
        elif index >= 32: string += "F"
        elif index >= 16:  string += "R"
        elif index >= 0:  string += "U"
    return string

# take a string to display the state of the cube
def drawState (state, globalxOffset, globalyOffset):
    offset = uOffset
    color = ()
    for i in range(len(state)):
        sticker = state[i]
        if   i > 79: offset = bOffset
        elif i > 63: offset = lOffset
        elif i > 47: offset = dOffset
        elif i > 31: offset = fOffset
        elif i > 15: offset = rOffset
        if   sticker == "U": color = white
        elif sticker == "R": color = red
        elif sticker == "F": color = green
        elif sticker == "D": color = yellow
        elif sticker == "L": color = orange
        elif sticker == "B": color = blue
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
fMoves = {  "U"  : [[0, 3], [1, 7], [2, 11], [3, 15], [4, 2], [5, 6], [6, 10], [7, 14], [8, 1], [9, 5], [10, 9], [11, 13], [12, 0], [13, 4], [14, 8], [15, 12], [19, 35], [18, 34], [17, 33], [16, 32], [64, 80], [65, 81], [66, 82], [67, 83], [32, 64], [33, 65], [34, 66], [35, 67], [83, 19], [82, 18], [81, 17], [80, 16]],
            "U'" : [[0, 12], [1, 8], [2, 4], [3, 0], [4, 13], [5, 9], [6, 5], [7, 1], [8, 14], [9, 10], [10, 6], [11, 2], [12, 15], [13, 11], [14, 7], [15, 3], [19, 83], [18, 82], [17, 81], [16, 80], [64, 32], [65, 33], [66, 34], [67, 35], [32, 16], [33, 17], [34, 18], [35, 19], [83, 67], [82, 66], [81, 65], [80, 64]],
            "U2" : [[0, 15], [1, 14], [2, 13], [3, 12], [4, 11], [5, 10], [6, 9], [7, 8], [8, 7], [9, 6], [10, 5], [11, 4], [12, 3], [13, 2], [14, 1], [15, 0], [19, 67], [18, 66], [17, 65], [16, 64], [64, 16], [65, 17], [66, 18], [67, 19], [32, 80], [33, 81], [34, 82], [35, 83], [83, 35], [82, 34], [81, 33], [80, 32]],
            "D"  : [[60, 48], [61, 52], [62, 56], [63, 60], [56, 49], [57, 53], [58, 57], [59, 61], [52, 50], [53, 54], [54, 58], [55, 62], [48, 51], [49, 55], [50, 59], [51, 63], [31, 95], [30, 94], [29, 93], [28, 92], [76, 44], [77, 45], [78, 46], [79, 47], [44, 28], [45, 29], [46, 30], [47, 31], [95, 79], [94, 78], [93, 77], [92, 76]],
            "D'" : [[60, 63], [61, 59], [62, 55], [63, 51], [56, 62], [57, 58], [58, 54], [59, 50], [52, 61], [53, 57], [54, 53], [55, 49], [48, 60], [49, 56], [50, 52], [51, 48], [31, 47], [30, 46], [29, 45], [28, 44], [76, 92], [77, 93], [78, 94], [79, 95], [44, 76], [45, 77], [46, 78], [47, 79], [95, 31], [94, 30], [93, 29], [92, 28]],
            "D2" : [[60, 51], [61, 50], [62, 49], [63, 48], [56, 55], [57, 54], [58, 53], [59, 52], [52, 59], [53, 58], [54, 57], [55, 56], [48, 63], [49, 62], [50, 61], [51, 60], [31, 79], [30, 78], [29, 77], [28, 76], [76, 28], [77, 29], [78, 30], [79, 31], [44, 92], [45, 93], [46, 94], [47, 95], [95, 47], [94, 46], [93, 45], [92, 44]],
            "L"  : [[0, 32], [4, 36], [8, 40], [12, 44], [60, 83], [56, 87], [52, 91], [48, 95], [76, 64], [72, 65], [68, 66], [64, 67], [77, 68], [73, 69], [69, 70], [65, 71], [78, 72], [74, 73], [70, 74], [66, 75], [79, 76], [75, 77], [71, 78], [67, 79], [44, 60], [40, 56], [36, 52], [32, 48], [95, 0], [91, 4], [87, 8], [83, 12]],
            "L'" : [[0, 95], [4, 91], [8, 87], [12, 83], [60, 44], [56, 40], [52, 36], [48, 32], [76, 79], [72, 78], [68, 77], [64, 76], [77, 75], [73, 74], [69, 73], [65, 72], [78, 71], [74, 70], [70, 69], [66, 68], [79, 67], [75, 66], [71, 65], [67, 64], [44, 12], [40, 8], [36, 4], [32, 0], [95, 48], [91, 52], [87, 56], [83, 60]],
            "L2" : [[0, 48], [4, 52], [8, 56], [12, 60], [60, 12], [56, 8], [52, 4], [48, 0], [76, 67], [72, 71], [68, 75], [64, 79], [77, 66], [73, 70], [69, 74], [65, 78], [78, 65], [74, 69], [70, 73], [66, 77], [79, 64], [75, 68], [71, 72], [67, 76], [44, 83], [40, 87], [36, 91], [32, 95], [95, 32], [91, 36], [87, 40], [83, 44]],
            "R"  : [[3, 92], [7, 88], [11, 84], [15, 80], [63, 47], [59, 43], [55, 39], [51, 35], [31, 28], [27, 29], [23, 30], [19, 31], [30, 24], [26, 25], [22, 26], [18, 27], [29, 20], [25, 21], [21, 22], [17, 23], [28, 16], [24, 17], [20, 18], [16, 19], [47, 15], [43, 11], [39, 7], [35, 3], [92, 51], [88, 55], [84, 59], [80, 63]],
            "R'" : [[3, 35], [7, 39], [11, 43], [15, 47], [63, 80], [59, 84], [55, 88], [51, 92], [31, 19], [27, 18], [23, 17], [19, 16], [30, 23], [26, 22], [22, 21], [18, 20], [29, 27], [25, 26], [21, 25], [17, 24], [28, 31], [24, 30], [20, 29], [16, 28], [47, 63], [43, 59], [39, 55], [35, 51], [92, 3], [88, 7], [84, 11], [80, 15]],
            "R2" : [[3, 51], [7, 55], [11, 59], [15, 63], [63, 15], [59, 11], [55, 7], [51, 3], [31, 16], [27, 20], [23, 24], [19, 28], [30, 17], [26, 21], [22, 25], [18, 29], [29, 18], [25, 22], [21, 26], [17, 30], [28, 19], [24, 23], [20, 27], [16, 31], [47, 80], [43, 84], [39, 88], [35, 92], [92, 35], [88, 39], [84, 43], [80, 47]],
            "F"  : [[12, 16], [13, 20], [14, 24], [15, 28], [48, 67], [49, 71], [50, 75], [51, 79], [28, 48], [24, 49], [20, 50], [16, 51], [79, 12], [75, 13], [71, 14], [67, 15], [44, 32], [45, 36], [46, 40], [47, 44], [40, 33], [41, 37], [42, 41], [43, 45], [36, 34], [37, 38], [38, 42], [39, 46], [32, 35], [33, 39], [34, 43], [35, 47]],
            "F'" : [[12, 79], [13, 75], [14, 71], [15, 67], [48, 28], [49, 24], [50, 20], [51, 16], [28, 15], [24, 14], [20, 13], [16, 12], [79, 51], [75, 50], [71, 49], [67, 48], [44, 47], [45, 43], [46, 39], [47, 35], [40, 46], [41, 42], [42, 38], [43, 34], [36, 45], [37, 41], [38, 37], [39, 33], [32, 44], [33, 40], [34, 36], [35, 32]],
            "F2" : [[12, 51], [13, 50], [14, 49], [15, 48], [48, 15], [49, 14], [50, 13], [51, 12], [28, 67], [24, 71], [20, 75], [16, 79], [79, 16], [75, 20], [71, 24], [67, 28], [44, 35], [45, 34], [46, 33], [47, 32], [40, 39], [41, 38], [42, 37], [43, 36], [36, 43], [37, 42], [38, 41], [39, 40], [32, 47], [33, 46], [34, 45], [35, 44]],
            "B"  : [[0, 76], [1, 72], [2, 68], [3, 64], [60, 31], [61, 27], [62, 23], [63, 19], [31, 3], [27, 2], [23, 1], [19, 0], [76, 63], [72, 62], [68, 61], [64, 60], [95, 92], [94, 88], [93, 84], [92, 80], [91, 93], [90, 89], [89, 85], [88, 81], [87, 94], [86, 90], [85, 86], [84, 82], [83, 95], [82, 91], [81, 87], [80, 83]],
            "B'" : [[0, 19], [1, 23], [2, 27], [3, 31], [60, 64], [61, 68], [62, 72], [63, 76], [31, 60], [27, 61], [23, 62], [19, 63], [76, 0], [72, 1], [68, 2], [64, 3], [95, 83], [94, 87], [93, 91], [92, 95], [91, 82], [90, 86], [89, 90], [88, 94], [87, 81], [86, 85], [85, 89], [84, 93], [83, 80], [82, 84], [81, 88], [80, 92]],
            "B2" : [[0, 63], [1, 62], [2, 61], [3, 60], [60, 3], [61, 2], [62, 1], [63, 0], [31, 64], [27, 68], [23, 72], [19, 76], [76, 19], [72, 23], [68, 27], [64, 31], [95, 80], [94, 81], [93, 82], [92, 83], [91, 84], [90, 85], [89, 86], [88, 87], [87, 88], [86, 89], [85, 90], [84, 91], [83, 92], [82, 93], [81, 94], [80, 95]],
            "Uw" : [[0, 3], [1, 7], [2, 11], [3, 15], [4, 2], [5, 6], [6, 10], [7, 14], [8, 1], [9, 5], [10, 9], [11, 13], [12, 0], [13, 4], [14, 8], [15, 12], [23, 39], [19, 35], [22, 38], [18, 34], [21, 37], [17, 33], [20, 36], [16, 32], [68, 84], [64, 80], [69, 85], [65, 81], [70, 86], [66, 82], [71, 87], [67, 83], [36, 68], [37, 69], [38, 70], [39, 71], [32, 64], [33, 65], [34, 66], [35, 67], [87, 23], [86, 22], [85, 21], [84, 20], [83, 19], [82, 18], [81, 17], [80, 16]],
            "Uw'": [[0, 12], [1, 8], [2, 4], [3, 0], [4, 13], [5, 9], [6, 5], [7, 1], [8, 14], [9, 10], [10, 6], [11, 2], [12, 15], [13, 11], [14, 7], [15, 3], [23, 87], [19, 83], [22, 86], [18, 82], [21, 85], [17, 81], [20, 84], [16, 80], [68, 36], [64, 32], [69, 37], [65, 33], [70, 38], [66, 34], [71, 39], [67, 35], [36, 20], [37, 21], [38, 22], [39, 23], [32, 16], [33, 17], [34, 18], [35, 19], [87, 71], [86, 70], [85, 69], [84, 68], [83, 67], [82, 66], [81, 65], [80, 64]],
            "Uw2": [[0, 15], [1, 14], [2, 13], [3, 12], [4, 11], [5, 10], [6, 9], [7, 8], [8, 7], [9, 6], [10, 5], [11, 4], [12, 3], [13, 2], [14, 1], [15, 0], [23, 71], [19, 67], [22, 70], [18, 66], [21, 69], [17, 65], [20, 68], [16, 64], [68, 20], [64, 16], [69, 21], [65, 17], [70, 22], [66, 18], [71, 23], [67, 19], [36, 84], [37, 85], [38, 86], [39, 87], [32, 80], [33, 81], [34, 82], [35, 83], [87, 39], [86, 38], [85, 37], [84, 36], [83, 35], [82, 34], [81, 33], [80, 32]],
            "Rw" : [[2, 93], [3, 92], [6, 89], [7, 88], [10, 85], [11, 84], [14, 81], [15, 80], [62, 46], [63, 47], [58, 42], [59, 43], [54, 38], [55, 39], [50, 34], [51, 35], [31, 28], [27, 29], [23, 30], [19, 31], [30, 24], [26, 25], [22, 26], [18, 27], [29, 20], [25, 21], [21, 22], [17, 23], [28, 16], [24, 17], [20, 18], [16, 19], [46, 14], [47, 15], [42, 10], [43, 11], [38, 6], [39, 7], [34, 2], [35, 3], [93, 50], [92, 51], [89, 54], [88, 55], [85, 58], [84, 59], [81, 62], [80, 63]],
            "Rw'": [[2, 34], [3, 35], [6, 38], [7, 39], [10, 42], [11, 43], [14, 46], [15, 47], [62, 81], [63, 80], [58, 85], [59, 84], [54, 89], [55, 88], [50, 93], [51, 92], [31, 19], [27, 18], [23, 17], [19, 16], [30, 23], [26, 22], [22, 21], [18, 20], [29, 27], [25, 26], [21, 25], [17, 24], [28, 31], [24, 30], [20, 29], [16, 28], [46, 62], [47, 63], [42, 58], [43, 59], [38, 54], [39, 55], [34, 50], [35, 51], [93, 2], [92, 3], [89, 6], [88, 7], [85, 10], [84, 11], [81, 14], [80, 15]],
            "Rw2": [[2, 50], [3, 51], [6, 54], [7, 55], [10, 58], [11, 59], [14, 62], [15, 63], [62, 14], [63, 15], [58, 10], [59, 11], [54, 6], [55, 7], [50, 2], [51, 3], [31, 16], [27, 20], [23, 24], [19, 28], [30, 17], [26, 21], [22, 25], [18, 29], [29, 18], [25, 22], [21, 26], [17, 30], [28, 19], [24, 23], [20, 27], [16, 31], [46, 81], [47, 80], [42, 85], [43, 84], [38, 89], [39, 88], [34, 93], [35, 92], [93, 34], [92, 35], [89, 38], [88, 39], [85, 42], [84, 43], [81, 46], [80, 47]],
            "Fw" : [[8, 17], [9, 21], [10, 25], [11, 29], [12, 16], [13, 20], [14, 24], [15, 28], [52, 66], [53, 70], [54, 74], [55, 78], [48, 67], [49, 71], [50, 75], [51, 79], [29, 52], [25, 53], [21, 54], [17, 55], [28, 48], [24, 49], [20, 50], [16, 51], [78, 8], [74, 9], [70, 10], [66, 11], [79, 12], [75, 13], [71, 14], [67, 15], [44, 32], [45, 36], [46, 40], [47, 44], [40, 33], [41, 37], [42, 41], [43, 45], [36, 34], [37, 38], [38, 42], [39, 46], [32, 35], [33, 39], [34, 43], [35, 47]],
            "Fw'": [[8, 78], [9, 74], [10, 70], [11, 66], [12, 79], [13, 75], [14, 71], [15, 67], [52, 29], [53, 25], [54, 21], [55, 17], [48, 28], [49, 24], [50, 20], [51, 16], [29, 11], [25, 10], [21, 9], [17, 8], [28, 15], [24, 14], [20, 13], [16, 12], [78, 55], [74, 54], [70, 53], [66, 52], [79, 51], [75, 50], [71, 49], [67, 48], [44, 47], [45, 43], [46, 39], [47, 35], [40, 46], [41, 42], [42, 38], [43, 34], [36, 45], [37, 41], [38, 37], [39, 33], [32, 44], [33, 40], [34, 36], [35, 32]],
            "Fw2": [[8, 55], [9, 54], [10, 53], [11, 52], [12, 51], [13, 50], [14, 49], [15, 48], [52, 11], [53, 10], [54, 9], [55, 8], [48, 15], [49, 14], [50, 13], [51, 12], [29, 66], [25, 70], [21, 74], [17, 78], [28, 67], [24, 71], [20, 75], [16, 79], [78, 17], [74, 21], [70, 25], [66, 29], [79, 16], [75, 20], [71, 24], [67, 28], [44, 35], [45, 34], [46, 33], [47, 32], [40, 39], [41, 38], [42, 37], [43, 36], [36, 43], [37, 42], [38, 41], [39, 40], [32, 47], [33, 46], [34, 45], [35, 44]],}



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

solvedCube = list("UUURUUUFUUUFUUUFRRRBRRRBRRRBRRRBRRRDFFFDFFFDFFFDDDDBDDDBDDDBDDDLFFFFLLLLLLLLLLLLULLLUBBBUBBBUBBB")

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

# -------------------------------- program loop -------------------------------------------
stdMoves = ["U", "U'", "U2", "D", "D'", "D2", "L", "L'", "L2", "R", "R'", "R2", "F", "F'", "F2", "B", "B'", "B2",
            "Uw", "Uw'", "Uw2", "Rw", "Rw'", "Rw2", "Fw", "Fw'", "Fw2"]
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


    # fill the screen with a color to wipe away anything from last frame
    screen.fill((100,100,100))

    drawState(solvedCube, 100, 100)
    drawState(solvedCube, 100, 300)


    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()