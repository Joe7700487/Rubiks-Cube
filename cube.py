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
        print(offset, color, i, i % 9, yOffset)
        pygame.draw.rect(screen, color,  (offset[0] + xOffset, offset[1] + yOffset, size, size), 0)
        pygame.draw.rect(screen, "black",  (offset[0] + xOffset, offset[1] + yOffset, size, size), 5)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    # drawState(solvedCube)
    drawState(turnedCube)
    
    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()