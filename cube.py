# Example file showing a circle moving on screen
import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

#------------------------ Cube setup ---------------------------------
size = 50
globalOffset = 100
u = [0, 0, 1, 2, 3, 4, 5, 6, 7, 8]
l = [0, 9, 10, 11, 12, 13, 14, 15, 16, 17]
f = [0, 18, 19, 20, 21, 22, 23, 24, 25, 26]
r = [0, 27, 28, 29, 30, 31, 32, 33, 34, 35]
b = [0, 36, 37, 38, 39, 40, 41, 42, 43, 44]
d = [0, 45, 46, 47, 48, 49, 50, 51, 52, 53]
uOffset = (size * 3 + globalOffset, size * 0 + globalOffset)
lOffset = (size * 0 + globalOffset, size * 3 + globalOffset)
fOffset = (size * 3 + globalOffset, size * 3 + globalOffset)
rOffset = (size * 6 + globalOffset, size * 3 + globalOffset)
bOffset = (size * 9 + globalOffset, size * 3 + globalOffset)
dOffset = (size * 3 + globalOffset, size * 6 + globalOffset)
blue    = (0, 0, 255)
green   = (0, 255, 0)
red     = (255, 0, 0)
white   = (255, 255, 255)
orange  = (255,165,0)
yellow  = (255,215,0)

tperm = "R U R' U' R' F R2 U' R' U' R U R' F'"
solvedCube = "UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD"

#define turns as permutations of facelets 
def turnUcw (state): # clockwise
    newState = list(state)
    # u face corners
    newState[u[1]] = state[u[7]]
    newState[u[3]] = state[u[1]]
    newState[u[9]] = state[u[3]]
    newState[u[7]] = state[u[9]]
    # u face edges
    newState[u[2]] = state[u[4]]
    newState[u[6]] = state[u[2]]
    newState[u[8]] = state[u[6]]
    newState[u[4]] = state[u[8]]
    # sides
    newState[l[1]] = state[f[1]]
    newState[l[2]] = state[f[2]]
    newState[l[3]] = state[f[3]]
    newState[f[1]] = state[r[1]]
    newState[f[2]] = state[r[2]]
    newState[f[3]] = state[r[3]]
    newState[r[1]] = state[b[1]]
    newState[r[2]] = state[b[2]]
    newState[r[3]] = state[b[3]]
    newState[b[1]] = state[l[1]]
    newState[b[2]] = state[l[2]]
    newState[b[3]] = state[l[3]]
    newState = "".join(newState)
    return newState
def turnUccw (state):
    for i in range(3): state = turnUcw (state)
    return state
def turnDccw (state): # counterclockwise
    newState = list(state)
    # u face corners
    newState[d[1]] = state[d[7]]
    newState[d[3]] = state[d[1]]
    newState[d[9]] = state[d[3]]
    newState[d[7]] = state[d[9]]
    # u face edges
    newState[d[2]] = state[d[4]]
    newState[d[6]] = state[d[2]]
    newState[d[8]] = state[d[6]]
    newState[d[4]] = state[d[8]]
    # sides
    newState[l[7]] = state[f[7]]
    newState[l[8]] = state[f[8]]
    newState[l[9]] = state[f[9]]
    newState[f[7]] = state[r[7]]
    newState[f[8]] = state[r[8]]
    newState[f[9]] = state[r[9]]
    newState[r[7]] = state[b[7]]
    newState[r[8]] = state[b[8]]
    newState[r[9]] = state[b[9]]
    newState[b[7]] = state[l[7]]
    newState[b[8]] = state[l[8]]
    newState[b[9]] = state[l[9]]
    newState = "".join(newState)
    return newState
def turnDcw (state):
    for i in range(3): state = turnDccw (state)
    return state
def turnLcw (state): # clockwise
    newState = list(state)
    # u face corners
    newState[l[1]] = state[l[7]]
    newState[l[3]] = state[l[1]]
    newState[l[9]] = state[l[3]]
    newState[l[7]] = state[l[9]]
    # u face edges
    newState[l[2]] = state[l[4]]
    newState[l[6]] = state[l[2]]
    newState[l[8]] = state[l[6]]
    newState[l[4]] = state[l[8]]
    # sides
    newState[f[1]] = state[u[1]]
    newState[f[4]] = state[u[4]]
    newState[f[7]] = state[u[7]]
    newState[u[1]] = state[b[9]]
    newState[u[4]] = state[b[6]]
    newState[u[7]] = state[b[3]]
    newState[b[9]] = state[d[1]]
    newState[b[6]] = state[d[4]]
    newState[b[3]] = state[d[7]]
    newState[d[1]] = state[f[1]]
    newState[d[4]] = state[f[4]]
    newState[d[7]] = state[f[7]]
    newState = "".join(newState)
    return newState
def turnLccw (state):
    for i in range(3): state = turnLcw (state)
    return state
def turnRccw (state): # counterclockwise
    newState = list(state)
    # u face corners
    newState[r[1]] = state[r[3]]
    newState[r[3]] = state[r[9]]
    newState[r[9]] = state[r[7]]
    newState[r[7]] = state[r[1]]
    # u face edges
    newState[r[2]] = state[r[6]]
    newState[r[6]] = state[r[8]]
    newState[r[8]] = state[r[4]]
    newState[r[4]] = state[r[2]]
    # sides
    newState[f[3]] = state[u[3]]
    newState[f[6]] = state[u[6]]
    newState[f[9]] = state[u[9]]
    newState[u[3]] = state[b[7]]
    newState[u[6]] = state[b[4]]
    newState[u[9]] = state[b[1]]
    newState[b[7]] = state[d[3]]
    newState[b[4]] = state[d[6]]
    newState[b[1]] = state[d[9]]
    newState[d[3]] = state[f[3]]
    newState[d[6]] = state[f[6]]
    newState[d[9]] = state[f[9]]
    newState = "".join(newState)
    return newState
def turnRcw (state):
    for i in range(3): state = turnRccw (state)
    return state
def turnFcw (state): # clockwise
    newState = list(state)
    # u face corners
    newState[f[1]] = state[f[7]]
    newState[f[3]] = state[f[1]]
    newState[f[9]] = state[f[3]]
    newState[f[7]] = state[f[9]]
    # u face edges
    newState[f[2]] = state[f[4]]
    newState[f[6]] = state[f[2]]
    newState[f[8]] = state[f[6]]
    newState[f[4]] = state[f[8]]
    # sides
    newState[u[7]] = state[l[9]]
    newState[u[8]] = state[l[6]]
    newState[u[9]] = state[l[3]]
    newState[r[1]] = state[u[7]]
    newState[r[4]] = state[u[8]]
    newState[r[7]] = state[u[9]]
    newState[d[1]] = state[r[7]]
    newState[d[2]] = state[r[4]]
    newState[d[3]] = state[r[1]]
    newState[l[3]] = state[d[1]]
    newState[l[6]] = state[d[2]]
    newState[l[9]] = state[d[3]]
    newState = "".join(newState)
    return newState
def turnFccw (state):
    for i in range(3): state = turnFcw (state)
    return state
def turnBcw (state): # clockwise
    newState = list(state)
    # u face corners
    newState[b[1]] = state[b[7]]
    newState[b[3]] = state[b[1]]
    newState[b[9]] = state[b[3]]
    newState[b[7]] = state[b[9]]
    # u face edges
    newState[b[2]] = state[b[4]]
    newState[b[6]] = state[b[2]]
    newState[b[8]] = state[b[6]]
    newState[b[4]] = state[b[8]]
    # sides
    newState[u[1]] = state[r[3]]
    newState[u[2]] = state[r[6]]
    newState[u[3]] = state[r[9]]
    newState[l[1]] = state[u[3]]
    newState[l[4]] = state[u[2]]
    newState[l[7]] = state[u[1]]
    newState[d[7]] = state[l[1]]
    newState[d[8]] = state[l[4]]
    newState[d[9]] = state[l[7]]
    newState[r[3]] = state[d[9]]
    newState[r[6]] = state[d[8]]
    newState[r[9]] = state[d[7]]
    newState = "".join(newState)
    return newState
def turnBccw (state):
    for i in range(3): state = turnFcw (state)
    return state
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

def decodeNotation(state, moves):
    moveArray = moves.split(" ")
    for move in moveArray:
        if len(move) == 1:
            if move == "U":
                state = turnUcw(state)
            elif move == "D":
                state = turnDcw(state)
            elif move == "F":
                state = turnFcw(state)
            elif move == "B":
                state = turnBcw(state)
            elif move == "R":
                state = turnRcw(state)
            elif move == "L":
                state = turnLcw(state)
        elif len(move) == 2 and move[1] != "2":
            if move[0] == "U":
                state = turnUccw(state)
            elif move[0] == "D":
                state = turnDccw(state)
            elif move[0] == "F":
                state = turnFccw(state)
            elif move[0] == "B":
                state = turnBccw(state)
            elif move[0] == "R":
                state = turnRccw(state)
            elif move[0] == "L":
                state = turnLccw(state)
        else:
            if move[0] == "U":
                for i in range(2): state = turnUccw(state)
            elif move[0] == "D":
                for i in range(2): state = turnDccw(state)
            elif move[0] == "F":
                for i in range(2): state = turnFccw(state)
            elif move[0] == "B":
                for i in range(2): state = turnBccw(state)
            elif move[0] == "R":
                for i in range(2): state = turnRccw(state)
            elif move[0] == "L":
                for i in range(2): state = turnLccw(state)
             
    return state
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_u:
                    solvedCube = turnUcw(solvedCube)
            if event.key == pygame.K_d:
                    solvedCube = turnDcw(solvedCube)
            if event.key == pygame.K_l:
                    solvedCube = turnLcw(solvedCube)
            if event.key == pygame.K_r:
                    solvedCube = turnRcw(solvedCube)
            if event.key == pygame.K_f:
                    solvedCube = turnFcw(solvedCube)
            if event.key == pygame.K_b:
                    solvedCube = turnBcw(solvedCube)
            if event.key == pygame.K_t:
                    solvedCube = decodeNotation(solvedCube, tperm)

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