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

def predicate():
    pass

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

def applyGMove(move, sticker):
    pass

solvedGCube = []
for i in range(54):
    solvedGCube.append(Sticker((0, 0, 0), (0, 0, 0)))


while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_u:
                solvedCube = applyMove(solvedCube, uMove)
                


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