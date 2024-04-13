#Pygame 3d projection test
from numba import njit
import pygame as pg
import numpy as np
import math, random

d = 4

def getColor(r, g, b):
    return (r//3, g//3, b//3)

def translate(pos):
    tx, ty, tz = pos
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [tx, ty, tz, 1]
    ])


def rotate_x(a):
    return np.array([
        [1, 0, 0, 0],
        [0, math.cos(a), math.sin(a), 0],
        [0, -math.sin(a), math.cos(a), 0],
        [0, 0, 0, 1]
    ])

def rotate_y(a):
    return np.array([
        [math.cos(a), 0, -math.sin(a), 0],
        [0, 1, 0, 0],
        [math.sin(a), 0, math.cos(a), 0],
        [0, 0, 0, 1]
    ])


def rotate_z(a):
    return np.array([
        [math.cos(a), math.sin(a), 0, 0],
        [-math.sin(a), math.cos(a), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

def scale(n):
    return np.array([
        [n, 0, 0, 0],
        [0, n, 0, 0],
        [0, 0, n, 0],
        [0, 0, 0, 1]
    ])

def getCube(d2):
    v = []
    g = []
    n = 2**d2
    for x in range(n):
        f = bin(x).split('0b')[1] if len(bin(x).split('0b')[1]) == d else '0'*(d2-len(bin(x).split('0b')[1])) + bin(x).split('0b')[1] + '0' * (d-d2)
        g.append(f)
    for f in g:
        x = []
        for char in f:
            x.append(int(char))
        v.append(x)
    return np.array(v)

def loadMesh(filename):
        vertex = []
        with open(filename) as f:
            for line in f:
                if line.startswith('v '):
                    vertex.append([float(i) for i in line.split()[1:]] + [1])
        return np.array(vertex)

WIN_RES = WIDTH, HEIGHT = 1200, 800
PROJ_SCALE = 200
OFFSET = PROJ_SCALE*2
MODE = 0
RUN = True
FPS = 0
DET = 10
VERTEX_RAD = PROJ_SCALE//(DET*10)
COLOUR = getColor(0, 255, 0)
print(COLOUR)

CAM = [1, 1]

WHITE = (255, 255, 255)
GRAY = (125, 125, 125)

pg.init()

screen = pg.display.set_mode(WIN_RES)
pg.display.set_caption("3D Projection")
#@njit(fastmath=True)
def arse(nums):
    return sum(nums)/len(nums)

@njit(fastmath=True)
def getPoint(v):
    x = v[0]*PROJ_SCALE+v[2]*PROJ_SCALE*0.25+v[3]*PROJ_SCALE*0.75
    y = v[1]*PROJ_SCALE+v[2]*PROJ_SCALE*0.25+v[3]*PROJ_SCALE*0.75
    return [x, y]

def length(v):
    x, y, z, w = v
    return math.sqrt(x**2 + y**2 + z**2)
def normalize(vert):
    x, y, z, w = vert
    return np.array([
        x/length(vert),
        y/length(vert),
        z/length(vert)
        ])

def perpendicular(vert):
    return np.array([
        length([vert[0],vert[1],vert[2],0])*math.cos(0+math.pi/2),
        length([vert[0],vert[1],vert[2],0])*math.sin(90+math.pi/2),
        length([vert[0],vert[1],vert[2],0])*math.sin(-45+math.pi/2)
        ])


def drawMesh(mesh, ev):
    #edge = [mesh[0], mesh[-1], mesh[-2]]
    for i in range(len(mesh)):
        v = mesh[i]
        v1 = mesh[i-1]
        v2 = mesh[i-2]
        v3 = mesh[i-3]
        #dx = arse([v[0], v1[0], v2[0]]) - arse([edge[0][0], edge[1][0], edge[2][0]]) if arse([v[0], v1[0], v2[0]]) > arse([edge[0][0], edge[1][0], edge[2][0]]) else arse([edge[0][0], edge[1][0], edge[2][0]]) - arse([v[0], v1[0], v2[0]])
        #dy = arse([v[1], v1[1], v2[1]]) - arse([edge[0][1], edge[1][1], edge[2][1]]) if arse([v[1], v1[1], v2[1]]) > arse([edge[0][1], edge[1][1], edge[2][1]]) else arse([edge[0][1], edge[1][1], edge[2][1]]) - arse([v[1], v1[1], v2[1]])
        ox, oy = OFFSET*CAM[0], OFFSET*CAM[1]
        x, y = getPoint(v)

        cx, cy, cz = arse([v[0], v1[0], v2[0]]), arse([v[1], v1[1], v2[1]]), arse([v[2], v1[2], v2[2]]) 
        #if x+OFFSET/2 > 0 and x+OFFSET/2 < WIDTH and -y+OFFSET > 0 and -y+OFFSET < HEIGHT:
        if ev:
            colour = [abs(1+v[2])*COLOUR[0], abs(1+v[2])*COLOUR[1], abs(1+v[2])*COLOUR[2]]
            pg.draw.circle(screen, colour, (x+ox/2, -y+oy), abs(1+v[2])*VERTEX_RAD)
        if not ev and perpendicular(normalize([cx, cy, cz, 0])).all(): #and dx < 5 and dy < 5 and arse([v[2], v1[2], v2[2]]) > arse([edge[0][2], edge[1][2], edge[2][2]]):
            x1, y1 = getPoint(v1)
            x2, y2 = getPoint(v2)
            x3, y3 = getPoint(v3)
            colour = [abs(1+v[2])*COLOUR[0], abs(1+v[2])*COLOUR[1], abs(1+v[2])*COLOUR[2]]
            pg.draw.polygon(screen, colour, [[x+ox/2, -y+oy], [x1+ox/2, -y1+oy], [x2+ox/2, -y2+oy], [x3+ox/2, -y3+oy]])
        #edge = [v, v1, v2]
clock = pg.time.Clock()

font = pg.font.SysFont('Arial Black', 15)

cube = loadMesh("test.obj") @ scale(0.5)
print(len(cube))

dt = 0
while RUN:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            RUN = False
    screen.fill((0, 0, 0))
    cube = cube @ rotate_y(dt/250)
    drawMesh(cube, MODE)
    text = font.render(f'FPS:{int(clock.get_fps())}', False, WHITE)
    screen.blit(text, (0, 0))
    pg.display.flip()
    dt = clock.tick(FPS)
pg.quit()
quit()
