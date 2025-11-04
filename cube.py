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

solvedCube = "UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD"

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

uMove = [[ S("U",1), S("U",3), S("U",9), S("U",7) ],
         [ S("U",2), S("U",6), S("U",8), S("U",4) ],
         [ S("F",1), S("L",1), S("B",1), S("R",1) ],
         [ S("F",2), S("L",2), S("B",2), S("R",2) ],
         [ S("F",3), S("L",3), S("B",3), S("R",3) ] ]

# take in a cube state and apply a list of permutations to it
def applyMove (cube, move):
    newCube = list(cube)
    for perms in move:
        perm = permFromCycle(perms)
        for pair in perm:
            newCube[pair[1]] = cube[pair[0]]
    newCube = "".join(newCube)
    return newCube

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

def applyGMove(cube, move):
    for sticker in cube:
        if move.predicate(sticker.pos):
            sticker.pos = applyAxisAngle(sticker.pos, move.axis, move.angle)


def getFace(sticker):
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
    
guMove = gMove("U", np.array([0, 1, 0]), 270,  lambda pos: pos[y] > 0)
gdMove = gMove("D", np.array([0, -1, 0]), 270,  lambda pos: pos[y] < 0)
grMove = gMove("R", np.array([1, 0, 0]), 270,  lambda pos: pos[x] > 0)
glMove = gMove("L", np.array([-1, 0, 0]), 270,  lambda pos: pos[x] < 0)
gfMove = gMove("F", np.array([0, 0, 1]), 270,  lambda pos: pos[z] > 0)
gbMove = gMove("B", np.array([0, 0, -1]), 270,  lambda pos: pos[z] < 0)

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

def convertGcube(gcube):
    sCube = ""

    # Up (y = +3): view from above, z decreases downward, x increases rightward
    uFace = sorted([s for s in gcube if s.pos[y] == 3],
                   key=lambda s: (s.pos[z], s.pos[x]))
    # Down (y = -3): viewed from below, z increases downward, x increases rightward
    dFace = sorted([s for s in gcube if s.pos[y] == -3],
                   key=lambda s: (-s.pos[z], s.pos[x]))

    # Left (x = -3): viewed from left, y decreases downward, z increases rightward
    lFace = sorted([s for s in gcube if s.pos[x] == -3],
                   key=lambda s: (-s.pos[y], s.pos[z]))
    # Right (x = +3): viewed from right, y decreases downward, z decreases rightward
    rFace = sorted([s for s in gcube if s.pos[x] == 3],
                   key=lambda s: (-s.pos[y], -s.pos[z]))

    # Front (z = +3): viewed from front, y decreases downward, x increases rightward
    fFace = sorted([s for s in gcube if s.pos[z] == 3],
                   key=lambda s: (-s.pos[y], s.pos[x]))
    # Back (z = -3): viewed from back, y decreases downward, x decreases rightward
    bFace = sorted([s for s in gcube if s.pos[z] == -3],
                   key=lambda s: (-s.pos[y], -s.pos[x]))


    # Build ULFRBD order
    for face in [uFace, lFace, fFace, rFace, bFace, dFace]:
        for sticker in face:
            sCube += getFace(sticker)
    return sCube


while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_u:
                # solvedCube = applyMove(solvedCube, uMove)
                applyGMove(solvedGCube, guMove)
                solvedCube = convertGcube(solvedGCube)
            if event.key == pygame.K_r:
                applyGMove(solvedGCube, grMove)
                solvedCube = convertGcube(solvedGCube)
            if event.key == pygame.K_l:
                applyGMove(solvedGCube, glMove)
                solvedCube = convertGcube(solvedGCube)
            if event.key == pygame.K_d:
                applyGMove(solvedGCube, gdMove)
                solvedCube = convertGcube(solvedGCube)
            if event.key == pygame.K_f:
                applyGMove(solvedGCube, gfMove)
                solvedCube = convertGcube(solvedGCube)
            if event.key == pygame.K_b:
                applyGMove(solvedGCube, gbMove)
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