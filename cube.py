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

solvedCube = "UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD"
turnedCube = "UUUUUUUUUFFFLLLLLLRRRFFFFFFBBBRRRRRRLLLBBBBBBDDDDDDDDD"

#define turns as permutations of facelets 
def turnU (state):
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

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_u:
                    solvedCube = turnU(solvedCube)

    # fill the screen with a color to wipe away anything from last frame
    screen.fill((100,100,100))


    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        running = False


    drawState(solvedCube)
    
    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()