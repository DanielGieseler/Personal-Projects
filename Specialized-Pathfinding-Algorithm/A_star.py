from queue import PriorityQueue
import itertools
import cv2 as cv
from PIL import Image
import numpy as np
import time
import imageio
import os

class Node:
    def __init__(self, parent = None, G = 0, H = 0):
        self.parent = parent
        self.G = G
        self.H = H


def distance(a, b, mode):
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    if mode == 'manhattan':
        return dx + dy
    elif mode == 'euclidian':
        return (dx**2 + dy**2)**0.5
    elif mode == 'euclidian grid':
        return min(dx, dy) + abs(dx - dy)*1
    else:
        print('wrong mode')
        
NEIGHBORHOOD = {
    'von neumann' : [(0,1), (0,-1), (1,0), (-1,0)],
    'moore'       : [(0,1), (0,-1), (1,0), (-1,0), (1,1), (-1,-1), (1,-1), (-1,1)]
}
def neighborhood(pos, limit, mode):
    neighbors = []
    for dx, dy in NEIGHBORHOOD[mode]:
        x, y = pos[0] + dx, pos[1] + dy
        if (x,y) not in BARRIER and (0 <= x < limit[0] and 0 <= y < limit[1]):
            neighbors.append((x, y))
    return neighbors

PURPLE = [164,  73, 163]
BLUE = [204,  72,  63]
BLACK = [0,  0,  0]
LIGHT_PURPLE = [231, 191, 200]

def coordinate_matches(color):
    indices = np.where(np.all(MAP == color, axis=-1))
    return list(zip(indices[0], indices[1]))

RED = [0, 0, 255]
GREEN = [0, 255, 0]

def draw():
    global MAP
    global FRAMES
    for coord in GRID:
        MAP[coord] = RED
    for _, _, coord in openNodes.queue:
        MAP[coord] = GREEN
    FRAMES.append(cv.cvtColor(MAP.copy(), cv.COLOR_BGR2RGB))

def display_path(current):
    path = []
    while GRID[current].parent:
        path.append(current)
        current = GRID[current].parent
    path.append(current)
    print(f'complete path is {len(set(path))} nodes long')
    delta_s = 0
    start = path[-1]
    for coord in path[::-1]:
        delta_s += distance(start, coord, 'euclidian')
        MAP[coord] = LIGHT_PURPLE
        FRAMES.append(cv.cvtColor(MAP.copy(), cv.COLOR_BGR2RGB))
        start = coord
    print(f'             and {delta_s} discrete units long')

MODE_DISTANCE = 'euclidian'
MODE_NEIGHBORHOOD = 'moore'

PATH = r'E:\Git2Post\Novel Search Algo'
for map_name in ['A1', 'A2', 'A3', 'B1', 'B2', 'C1']:
    MAP_ORIGINAL = cv.imread(os.path.join(PATH, 'maps', map_name + '.png'))
    MAP = MAP_ORIGINAL.copy()
    start, end = coordinate_matches(BLUE)[0], coordinate_matches(PURPLE)[0]
    limit = MAP.shape[:2]
    BARRIER = set(coordinate_matches(BLACK))
    SIGN = -1
    W = 1
    GRID = {}
    openNodes = PriorityQueue()
    H = distance(start, end, MODE_DISTANCE)
    GRID[start] = Node(H = H)
    openNodes.put((H, H, start))
    delta_time = 0
    FRAMES = []  # List to store frames for GIF
    while not openNodes.empty():
        start_time = time.time()
        current = openNodes.get()[2]
        if current == end:
            delta_time += time.time() - start_time
            print(f'Runtime: {delta_time}')
            print(f'Nodes searched: {len(GRID)}')   
            #draw()
            display_path(current)
            break
        for neighbor in neighborhood(current, limit, MODE_NEIGHBORHOOD):
            G = GRID[current].G + distance(neighbor, current, MODE_DISTANCE)
            queueOpen = [item[2] for item in openNodes.queue]
            if neighbor not in GRID: # new node
                H = distance(neighbor, end, MODE_DISTANCE)
                GRID[neighbor] = Node(parent = current, G = G, H = H)
                openNodes.put(((G + W*H), SIGN*G, neighbor))
            elif neighbor in queueOpen:
                if G < GRID[neighbor].G:
                    GRID[neighbor].G = G
                    GRID[neighbor].parent = current
        draw()
        delta_time += time.time() - start_time

    kept_frames = FRAMES[:-1:4] + [FRAMES[-1]]
    for frame in kept_frames:
        frame[start] = LIGHT_PURPLE
        frame[end] = LIGHT_PURPLE
    imageio.mimsave(os.path.join(PATH, map_name + '.gif'), kept_frames, fps=50)
