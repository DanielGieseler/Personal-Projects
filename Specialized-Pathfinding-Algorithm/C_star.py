from queue import PriorityQueue
import cv2 as cv
import numpy as np
import time
import copy
import itertools
import imageio
import os

#from pyrsistent import b, v
#from sympy import E

##### TEST STUFF

def StraightLine_Test():
    start = (50, 50)
    shifts = list(itertools.product([45], range(-45, 46))) + list(itertools.product(range(44, -46, -1), [45]))
    shifts += list(itertools.product([-45], range(44, -46, -1))) + list(itertools.product(range(-44, 45), [-45]))
    ends = [(start[0] + s[0], start[1] + s[1]) for s in shifts]
    aa = np.ones((100,100), dtype = np.uint8)*255
    aa[start[1], start[0]] = 0
    for end in ends:
        aa[end[1], end[0]] = 0
    flag = True
    while flag:
        for end in ends:
            a = aa.copy()
            straight_line = StraightLine(start, end)
            line = [start]
            while line[-1] != end:
                line.append(straight_line.get_neighbor(line[-1]))
            for n in line[1:-1]:
                a[n[1], n[0]] = 110
            cv.namedWindow('map', cv.WINDOW_KEEPRATIO)
            cv.imshow('map', a)
            cv.resizeWindow('map', 700, 700)
            if cv.waitKey(100) & 0xFF == ord('q'):
                flag = False
                cv.destroyAllWindows()
                break

def get_indexes(array, value):
    indices = np.where(array == value)
    return set((int(e[0]), int(e[1])) for e in zip(indices[0], indices[1]))

def neighborhood_test():
    array = np.array([
        [2, 1, 0],
        [2, -1, 0],
        [2, 2, 0]
    ])
    LIMIT = [20, 20]
    BARRIER = get_indexes(array, 1)
    START, END = (1, 1), (10, 10)
    s = 0
    s.visited = get_indexes(array, 0)
    s.current = get_indexes(array, -1).pop()

    a = np.ones((3,3), dtype = np.uint8)*255
    a[START[1],START[0]] = 120
    for n, flag in s.neighborhood():
        a[n] = 0

    while True:
        cv.namedWindow('map', cv.WINDOW_KEEPRATIO)
        cv.imshow('map', a)
        cv.resizeWindow('map', 500, 500)
        if cv.waitKey(0) & 0xFF == ord('q'):
            cv.destroyAllWindows()
            break

    
###########################
#### IMAGE PROCESSING #####
###########################

PURPLE = [164,  73, 163]
LIGHT_PURPLE = [231, 191, 200]
BLUE = [204,  72,  63]
BLACK = [0,  0,  0]
RED = [0, 0, 255]
GREEN = [0, 255, 0]

def coordinate_matches(color):
    indices = np.where(np.all(MAP == color, axis = -1))
    return [(int(e[0]), int(e[1])) for e in zip(indices[0], indices[1])]

def draw():
    global MAP
    for coord in GRID:
        MAP[coord] = RED
    for _, s in QUEUE.queue:
        for coord in [e[0] for e in s.path]:
            MAP[coord] = BLUE
    for _, segment in QUEUE.queue:
        MAP[segment.current] = GREEN

        
def display_path(path):
    start = path[0]
    complete_path = [start]
    delta_s_continuous, delta_s_discrete = 0, 0
    for end in path[1:]:
        SL = StraightLine(start, end)
        neighbor = start
        delta_s_continuous += distance(start, end, continuous = True)
        start_d = start
        while neighbor != end:
            neighbor = SL.get_neighbor(neighbor)
            delta_s_discrete += distance(start_d, neighbor)
            complete_path.append(neighbor)
            start_d = neighbor
        start = end
    print(f'complete path is {len(complete_path)} nodes long')
    print(f'             and {delta_s_continuous} continuuos units long')
    print(f'             and {delta_s_discrete} discrete units long')
    for coord in complete_path:
        MAP[coord] = LIGHT_PURPLE
        FRAMES.append(cv.cvtColor(MAP.copy(), cv.COLOR_BGR2RGB))

###########################
###### MAIN FUNCTIONS #####
###########################

CONTINUOUS = 1
def distance(a, b, continuous = False):
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    if continuous or CONTINUOUS:
        return (dx**2 + dy**2)**0.5
    else:
        return min(dx, dy) + abs(dx - dy)*2**0.5

def sign(line, point):
    [La, Lb], P = line, point
    d = (P[0]-La[0])*(Lb[1]-La[1])-(P[1]-La[1])*(Lb[0]-La[0])
    return (d>0)-(d<0)  

# get the 2 adjacents neighbors of a given neighbor in a Moore neighborhood
def adjacents(point, neighbor):
    if point == neighbor:
        return []
    neighbor = (neighbor[0] - point[0], neighbor[1] - point[1])
    if 0 in neighbor:
        adjacents = [list(neighbor), list(neighbor)]
        for i, adj in zip([-1, 1], adjacents):
            adj[adj.index(0)] = i
    else:
        adjacents = [(0,neighbor[1]), (neighbor[0],0)]
    return [(point[0] + adj[0], point[1] + adj[1]) for adj in adjacents]

class StraightLine:
    def __init__(self, p0, p1):
        self.start, self.end = p0, p1
        self.current = p0
        vector = [e1 - e0 for e1,e0 in zip(p1,p0)]
        vectorAbs = [abs(e) for e in vector]
        vectorSign = [(e>0)-(e<0) for e in vector]
        self.neighbors = [vectorSign.copy()]
        if not (0 in vectorSign) and not (vectorAbs[0] == vectorAbs[1]): 
            vectorSign[vectorAbs.index(min(vectorAbs))] = 0
            self.neighbors.append(vectorSign)
        self.distance_to_line = lambda p: abs((p[0]-p0[0])*vector[1]-(p[1]-p0[1])*vector[0])

    def get_neighbor(self, point):
        neighbors = [(point[0]+n[0], point[1]+n[1]) for n in self.neighbors]
        min_neighbor = min(neighbors, key = self.distance_to_line)
        self.current = min_neighbor
        return min_neighbor

class Elastic:
    def __init__(self, start, end):
        # start point, stretched, distance, sign, previous
        self.path = [[start, False, 0, None, start], [end, True, None, None, None]]
        self.index = 0
        self.visited = set()
        self.straightLine = StraightLine(start, end)
        self.start, self.end = start, end
        self.current = start
        self.update(start, False)
    
    def __lt__(self, other):
        return False
    
    def update(self, current, at_obstacle):
        self.previous = self.current
        self.current = current
        self.at_obstacle = at_obstacle
        self.visited.add(current)
        self.F = sum([p[2] for p in self.path[:self.index+1]]) + distance(self.current, self.start) + distance(self.current, self.end) + distance(self.end, self.path[-1][0])
        if not at_obstacle:
            self.sign = None
            #self.F += -10000

    def neighborhood(self):
        p = self.current
        available, unvisited = set(), set()
        # moore neighborhood tha is: NOT VISITED + NOT BARRIER + INBOUND
        for dy, dx in [(0,1), (0,-1), (1,0), (-1,0), (1,1), (-1,-1), (1,-1), (-1,1)]:
            np = (p[0] + dy, p[1] + dx)
            if not np in BARRIER and (0 <= np[0] < LIMIT[0] and 0 <= np[1] < LIMIT[1]):
                available.add(np)
                if not np in self.visited:
                    unvisited.add(np)
        selected = []
        # GET WALLING NEIGHBORS
        for neighbor in unvisited:
            for adj in adjacents(p, neighbor):
                if adj in BARRIER:
                    selected.append((neighbor, True))
                    break
        # GET CLOSEsT NEIGHBOR
        if self.straightLine.current != self.current:
            self.straightLine = StraightLine(self.current, self.end)
        closest = self.straightLine.get_neighbor(self.current)
        anti_inertial = adjacents(p, self.previous) + [self.previous]
        if closest in available and not closest in anti_inertial and not closest in [s for s,_ in selected]:
            return [(closest, False)]
        # last check
        if not selected and not self.at_obstacle:
            visited = available.difference(unvisited)
            for v in visited:
                if not v in anti_inertial:
                    for adj in adjacents(p, v):
                        if adj in BARRIER:
                            selected.append((v, True))
                            break
        return selected

    def bend(self):
        self.path[self.index][3] = self.sign
        self.index += 1
        self.path.insert(self.index, [self.current, False, distance(self.current, self.start), self.sign, None])
        self.start = self.path[self.index][0]
    
    def unbend_back(self):
        del self.path[self.index]
        self.index += -1
        self.start = self.path[self.index][0]

    def unbend_front(self):
        del self.path[self.index+2]
        self.path[self.index+1][1] = False

    def next_index_false(self):
        flags = [(i, e[1]) for i, e in enumerate(self.path)]
        for i, flag in flags[self.index:] + flags[:self.index]:
            if not flag:
                new_elastic = Elastic(self.path[i][0], self.path[i+1][0])
                new_elastic.path = copy.deepcopy(self.path)
                new_elastic.index = i
                new_elastic.visited = copy.deepcopy(self.visited)
                new_elastic.previous = new_elastic.path[i][4]
                return new_elastic
        return None

###########################
########## MAIN ###########
###########################

# parse image
PATH = r'E:\Git2Post\Novel Search Algo'
map_name = ['A1', 'A2', 'A3', 'B1', 'B2', 'C1'][5]
MAP_ORIGINAL = cv.imread(os.path.join(PATH, 'maps', map_name + '.png'))
MAP = MAP_ORIGINAL.copy()
START, END = coordinate_matches(BLUE)[0], coordinate_matches(PURPLE)[0]
LIMIT = MAP.shape[:2]
BARRIER = set(coordinate_matches(BLACK))
SPEED = 1 
SIZE = 700
QUEUE = PriorityQueue()
QUEUE.put((distance(START, END), Elastic(START, END)))
GRID = set()
FRAMES = []

def main():
    delta_time = 0
    while not QUEUE.empty():
        start_time = time.time()
        s = QUEUE.get()[1]
        GRID.add(s.current)
        # Stop triggers
        if s.current == s.path[s.index+1][0]:
            s.path[s.index][1] = True
            s.path[s.index+1][4] = s.previous
            s.path[s.index+1][2] = distance(s.start, s.end)
            # unbend ahead
            while (len(s.path[s.index:]) > 3) and sign([s.path[s.index+3][0], s.path[s.index+1][0]], s.path[s.index+2][0]) != s.path[s.index+1][3]:
                l = [s.path[s.index+3][0], s.path[s.index+1][0], s.path[s.index+2][0], s.path[s.index+1][3]]
                lsign = sign([s.path[s.index+3][0], s.path[s.index+1][0]], s.path[s.index+2][0])
                s.unbend_front()
            new_elastic = s.next_index_false()
            if not new_elastic:
                delta_time += time.time() - start_time
                print(f'Runtime: {delta_time}')
                display_path([e[0] for e in s.path])
                break
            QUEUE.put((new_elastic.F, new_elastic))
        else:
            neighborhood = s.neighborhood()
            elastics = [s] + [copy.deepcopy(s) for _ in range(len(neighborhood)-1)]
            for [neighbor, flag], e in zip(neighborhood, elastics):
                # Elastic Mechanics
                if e.sign:
                    while (e.index > 0) and sign([e.current, e.path[e.index-1][0]], e.start) != e.path[e.index-1][3]:
                        e.unbend_back()
                    if sign([neighbor, e.start], e.current) == e.sign:
                        e.bend()
                elif flag:
                    e.sign = sign([e.current, e.start], neighbor)
                # register
                e.update(neighbor, flag)
                e.visited.update([n for n,_ in neighborhood])
                QUEUE.put((e.F, e))
        
        delta_time += time.time() - start_time
        # Visualization
        draw()
        FRAMES.append(cv.cvtColor(MAP.copy(), cv.COLOR_BGR2RGB))

    imageio.mimsave(os.path.join(PATH, map_name + '-E.gif'), FRAMES, fps = 50)
    #print(f'Nodes searched: {len(s.visited)}')


main()


        