from abc import ABC, abstractmethod 
import copy
import heapq
import pygame

pygame.init()

#left, top, right, bottom
#True is connectable
#False is not connectable
TPIPE_BASE_STATES = [
    [False, True, True, True],      # |-
    [True, True, True, False],      # _|_
    [True, True, False, True],      # -|
    [True, False, True, True]       # the rest
]
IPIPE_BASE_STATES = [
    [False, True, False, True],     # |
    [True, False, True, False]      # __
]
LPIPE_BASE_STATES = [
    [False, True, True, False],     # L
    [True, True, False, False],     # _|
    [True, False, False, True],     # ┐
    [False, False, True, True]      # the rest
]
EPOINT_BASE_STATES = [
    [True, False, False, False],    # -o
    [False, False, False, True],    # the rest
    [False, False, True, False],    # o-
    [False, True, False, False]     # o/
]

class Pipe(ABC):
    def __init__(self, row: int, col: int, baseState: list[list[bool]], index: int):
        self.row = row
        self.col = col
        self.locked = False
        self.visited = False
        self.index = index
        self.baseState = baseState
    
    def adjacent (self, graph, row, col):
        adj = []
        if col - 1 >= 0 and not graph[row][col - 1].visited and self.value()[0] and graph[row][col - 1].value()[2]:  adj += [(self.row, self.col - 1 )]
        if row - 1 >= 0 and not graph[row - 1][col].visited and self.value()[1] and graph[row - 1][col].value()[3]: adj += [(self.row - 1, self.col)]
        if col + 1 < len(graph[0]) and not graph[row][col + 1].visited and self.value()[2] and graph[row][col + 1].value()[0]: adj += [(self.row, self.col + 1 )]
        if row + 1 < len(graph) and not graph[row + 1][col].visited and self.value()[3] and graph[row + 1][col].value()[1]: adj += [(self.row + 1, self.col)]

        return adj       
        
    @abstractmethod
    def leftRotate(self): pass
    
    @abstractmethod    
    def rightRotate(self): pass

    def value(self): 
        return self.baseState[self.index]

class Tpipe(Pipe):
    def __init__(self, row, col, index):
        super().__init__(row, col, TPIPE_BASE_STATES, index)
    
    def leftRotate(self):
        self.index = (self.index + 1) % 4
        
    def rightRotate(self):
        self.index = (self.index + 3) % 4
        
class Ipipe(Pipe):
    def __init__(self, row, col, index):
        super().__init__(row, col, IPIPE_BASE_STATES, index)
        
    def leftRotate(self):
        self.index = 0 if self.index == 1 else  1
        
    def rightRotate(self):
        self.leftRotate()
        
class Lpipe(Pipe):
    def __init__(self, row, col, index):
        super().__init__(row, col, LPIPE_BASE_STATES, index)
    
    def leftRotate(self):
        self.index = (self.index + 1) % 4
        
    def rightRotate(self):
        self.index = (self.index + 3) % 4

class Epoint(Pipe):
    def __init__(self, row, col, index):
        super().__init__(row, col, EPOINT_BASE_STATES, index)
        
    def leftRotate(self):
        self.index = (self.index + 1) % 4
        
    def rightRotate(self):
        self.index = (self.index + 3) % 4

class Transform():
    def __init__(self, row, col, times):
        self.row: int = row
        self.col: int = col
        self.times: int = times
    
    def value(self):
        return self.row, self.col, self.times

class PriorityQueue:
    def __init__(self):
        self.queue = []
    
    def len(self):
        return len(self.queue)

    def isEmpty(self):
        return len(self.queue) == 0
    
    def minConnected(self):
        if self.queue == []: return -1
        return self.queue[0][0]

    def insert(self, connected, data):
        heapq.heappush(self.queue, (connected, id(data),  data))

    def delete(self):
        if not self.isEmpty():
            return heapq.heappop(self.queue)[1]
        else:
            raise IndexError("Queue is empty")

def lockAdjacent(graph: list[list[Epoint | Tpipe | Lpipe | Ipipe]], row: int, col: int) -> list[Transform]:
        lockTransforms = []
        t = type(graph[row][col])
        left = type(graph[row][col - 1]) if col - 1 >= 0 and graph[row][col].value()[0] and not graph[row][col - 1].locked else None
        top = type(graph[row - 1][col]) if row - 1 >= 0 and graph[row][col].value()[1] and not graph[row - 1][col].locked else None
        right = type(graph[row][col + 1]) if col + 1 < len(graph[0]) and graph[row][col].value()[2] and not graph[row][col + 1].locked else None
        bottom = type(graph[row + 1][col]) if row + 1 < len(graph) and graph[row][col].value()[3] and not graph[row + 1][col].locked else None
        
        if t is Tpipe:
            if left and left in [Epoint, Lpipe]:
                count = 0
                
                if left is Epoint:
                    while not graph[row][col - 1].value()[2]:
                        count += 1
                        graph[row][col - 1].leftRotate()
                    graph[row][col - 1].locked = True
                else:
                    while row == 0 and not (graph[row][col - 1].value()[2] and graph[row][col - 1].value()[3]):
                        count += 1
                        graph[row][col - 1].leftRotate()
                    
                    while row == len(graph) - 1 and not (graph[row][col - 1].value()[2] and graph[row][col - 1].value()[1]):
                        count += 1
                        graph[row][col - 1].leftRotate()
                    
                    if row == 0 or row == len(graph) - 1:
                        graph[row][col - 1].locked = True
                    
                if count != 0:
                    lockTransforms += [Transform(row, col - 1, count)]
        
            if right and right in [Epoint, Lpipe]:
                count = 0
                
                if right is Epoint:
                    while not graph[row][col + 1].value()[0]:
                        count += 1
                        graph[row][col + 1].leftRotate()
                    graph[row][col + 1].locked = True 
                else:
                    while row == 0 and not (graph[row][col + 1].value()[0] and graph[row][col + 1].value()[3]):
                        count += 1
                        graph[row][col + 1].leftRotate()
                    
                    while row == len(graph) - 1 and not (graph[row][col + 1].value()[0] and graph[row][col + 1].value()[1]):
                        count += 1
                        graph[row][col + 1].leftRotate()
                    
                    if row == 0 or row == len(graph) - 1:
                        graph[row][col - 1].locked = True
                
                if count != 0:
                    lockTransforms += [Transform(row, col + 1, count)]
            
            if top and top in [Epoint, Ipipe]:
                count = 0
                
                while not graph[row - 1][col].value()[3]:
                    count += 1
                    graph[row - 1][col].leftRotate()
                    
                graph[row - 1][col].locked = True
                if count != 0:
                    lockTransforms += [Transform(row - 1, col, count)]
                    
            
            if bottom and bottom in [Epoint, Ipipe]:
                count = 0
                
                while not graph[row + 1][col].value()[1]:
                    count += 1
                    graph[row + 1][col].leftRotate()
                    
                graph[row + 1][col].locked = True
                if count != 0:
                    lockTransforms += [Transform(row + 1, col, count)]
                    
        if t in [Lpipe, Ipipe]:
            if left and left in [Epoint, Ipipe]:
                count = 0
                
                while not graph[row][col - 1].value()[2]:
                    count += 1
                    graph[row][col - 1].leftRotate()                    
                
                graph[row][col - 1].locked = True
                if count != 0:
                    lockTransforms += [Transform(row, col - 1, count)]
            
            if right and right in [Epoint, Ipipe]:
                count = 0
                
                while not graph[row][col + 1].value()[0]:
                    count += 1
                    graph[row][col + 1].leftRotate()
                    
                graph[row][col + 1].locked = True
                if count != 0:
                    lockTransforms += [Transform(row, col + 1, count)]
                    
            
            if top and top in [Epoint, Ipipe]:
                count = 0
                
                while not graph[row - 1][col].value()[3]:
                    count += 1
                    graph[row - 1][col].leftRotate()
                    
                graph[row - 1][col].locked = True
                if count != 0:
                    lockTransforms += [Transform(row - 1, col, count)]
                    
            
            if bottom and bottom in [Epoint, Ipipe]:
                count = 0
                
                while not graph[row + 1][col].value()[1]:
                    count += 1
                    graph[row + 1][col].leftRotate()
                    
                graph[row + 1][col].locked = True
                if count != 0:
                    lockTransforms += [Transform(row + 1, col, count)]
            
        if left and left is Lpipe:
            count = 0 
            while row == 0 and graph[row][col - 1].index != 3:
                count += 1
                graph[row][col - 1].leftRotate()
            
            while row == len(graph) - 1 and graph[row][col - 1].index != 0:
                count += 1
                graph[row][col - 1].leftRotate()
            
            if count != 0:
                lockTransforms += [Transform(row, col - 1, count)]
        
        if top and top is Lpipe:
            count = 0 
            while col == 0 and graph[row - 1][col].index != 3:
                count += 1
                graph[row - 1][col].leftRotate()
            
            while col == len(graph[0]) - 1 and graph[row - 1][col].index != 2:
                count += 1
                graph[row - 1][col].leftRotate()
            
            if count != 0:
                lockTransforms += [Transform(row - 1, col, count)]
                
                
        if right and right is Lpipe:
            count = 0 
            while row == 0 and graph[row][col + 1].index != 2:
                count += 1
                graph[row][col + 1].leftRotate()
            
            while row == len(graph) - 1 and graph[row][col + 1].index != 1:
                count += 1
                graph[row][col + 1].leftRotate()
            
            if count != 0:
                lockTransforms += [Transform(row, col + 1, count)]
                
        if bottom and bottom is Lpipe:
            count = 0 
            while col == 0 and graph[row + 1][col].index != 0:
                count += 1
                graph[row + 1][col].leftRotate()
            
            while col == len(graph[0]) - 1 and graph[row + 1][col].index != 1:
                count += 1
                graph[row + 1][col].leftRotate()
            
            if count != 0:
                lockTransforms += [Transform(row + 1, col, count)]
                
        return lockTransforms

def noHopeState(graph: list[list[Epoint | Tpipe | Lpipe | Ipipe]], row: int, col: int, preProcess: bool = False) -> bool:
    current = graph[row][col]
    left = graph[row][col - 1] if col - 1 >= 0 else None
    top = graph[row - 1][col] if row - 1 >= 0 else None
    right = graph[row][col + 1] if col + 1 < len(graph[0]) else None
    bottom = graph[row + 1][col] if row + 1 < len(graph) else None   
    
    if not left and current.value()[0]:
        return True 
    
    if not top and current.value()[1]:
        return True 
    
    if not right and current.value()[2]:
        return True 
    
    if not bottom and current.value()[3]:
        return True
    
    if left and (not preProcess or (preProcess and left.locked)) and left.value()[2] != current.value()[0]:
        return True

    if top and (not preProcess or (preProcess and top.locked)) and top.value()[3] != current.value()[1]:
        return True
    
    if right and right.locked and right.value()[0] != current.value()[2]:
        return True
    
    if bottom and bottom.locked and bottom.value()[1] != current.value()[3]:
        return True
    
    return False

def rightDicretion(graph: list[list[Epoint | Tpipe | Lpipe | Ipipe]], row: int, col: int, rightIndex: int, transforms: list[Transform], floodFill: list[(int, int)]):
    count = 0
    while graph[row][col].index != rightIndex:
        count += 1
        graph[row][col].leftRotate()
    graph[row][col].locked = True
    
    if count != 0:
        transforms += [Transform(row, col, count)]
        floodFill += [(row, col)]

    transforms += lockAdjacent(graph, row, col)

class Graph():
    def __init__(self, graph):
        # self.graph = [[self.create_random_pipe(i, j) for j in range(size)] for i in range(size)]
        self.graph: list[list[Epoint | Tpipe | Ipipe | Lpipe]] = graph
        self.row = len(graph)
        self.col = len(graph[0])

    def preProcessing(self) -> tuple[list[Transform], int, int]:
        # make edge have right direction
        maxElements = 0
        loop =  0
        preTransforms = []
        floodFill = []
        
        conners = [(0, 0), (0, self.col - 1), (self.row - 1, 0), (self.row - 1, self.col - 1)]
        for conner in conners:
            row: int = conner[0]
            col: int = conner[1]
            
            if type(self.graph[row][col]) is Lpipe:
                count = 0 
                while noHopeState(self.graph, row, col, True):
                    count += 1
                    self.graph[row][col].leftRotate()
                    
                self.graph[row][col].locked = True
                if count != 0:
                    preTransforms += [Transform(row, col, count)]
                    floodFill += [(row, col)]
                preTransforms += lockAdjacent(self.graph, row, col)
                
        for j in range(self.col):
            if type(self.graph[0][j]) is Tpipe:
                rightDicretion(self.graph, 0, j, 3, preTransforms, floodFill)
                
            if type(self.graph[0][j]) is Ipipe:
                rightDicretion(self.graph, 0, j, 1, preTransforms, floodFill)
                
            if type(self.graph[self.row - 1][j]) in [Tpipe, Ipipe]:
                rightDicretion(self.graph, self.row - 1, j, 1, preTransforms, floodFill)

        for i in range(1, self.row):
            if type(self.graph[i][0]) in [Tpipe, Ipipe]:
                rightDicretion(self.graph, i, 0, 0, preTransforms, floodFill)
                
            if type(self.graph[i][self.col - 1]) is Tpipe:
                rightDicretion(self.graph, i, self.col - 1, 2, preTransforms, floodFill)
                
            if type(self.graph[i][self.col - 1]) is Ipipe:
                rightDicretion(self.graph, i, self.col - 1, 0, preTransforms, floodFill)
        
        while floodFill:
            loop += 1
            maxElements = maxElements if maxElements > len(floodFill) else len(floodFill)
            
            front = floodFill.pop(0)
            row: int = front[0]
            col: int = front[1]

            if self.graph[row][col].visited:
                continue
            
            self.graph[row][col].visited = True
            steps: list[(int, int)] = [(0, -1), (-1, 0), (0, 1), (1, 0)]
            
            for _ in steps:            
                if not (0 <= col + _[1] < self.col  and 0 <= row + _[0] < self.row):
                    continue
                    
                if self.graph[row + _[0]][col + _[1]].locked:
                    floodFill += [( row + _[0], col + _[1])]
                    continue
                
                t = type(self.graph[row + _[0]][col + _[1]]) 
            
                count = 0
                if t is Ipipe:
                    for __ in range(2):
                        self.graph[row + _[0]][col + _[1]].leftRotate()
                        if not noHopeState(self.graph, row + _[0], col + _[1], True):
                            count += 1
                else:
                    for __ in range(4):
                        self.graph[row + _[0]][col + _[1]].leftRotate()
                        if not noHopeState(self.graph, row + _[0], col + _[1], True):
                            count += 1
            
                if count == 1:
                    count = 0
                    while noHopeState(self.graph, row + _[0], col + _[1], True):
                        count += 1
                        self.graph[row + _[0]][col + _[1]].leftRotate()
                    self.graph[row + _[0]][col + _[1]].locked = True
                    
                    if count != 0:
                        preTransforms += [Transform( row + _[0], col + _[1], count)]
                        floodFill += [( row + _[0], col + _[1])]

        for _ in self.graph:
            for __ in _:
                __.visited = False
        
        return preTransforms, maxElements, loop

    def connectedComponent(graph):
        connected = 0
        queue = []
        row = len(graph)
        col = len(graph[0])
        
        for i in range(row):
            for j in range(col):
                if graph[i][j].visited:
                    continue

                queue += [(i, j)]
                connected += 1
                
                while queue:
                    front = queue[0]
                    graph[front[0]][front[1]].visited = True
                    queue += graph[front[0]][front[1]].adjacent(graph, front[0], front[1])
                    queue.pop(0)
                    
        for i in range(row):
            for j in range(col):
                graph[i][j].visited = False
                
        return connected

    def blindSolve(self) -> tuple[list[Transform], int, int] | None:
        queue: list[list[Transform]] = []
    
        maxElement = 0
        loop = 0
        
        for i in range(self.row):
            for j in range(self.col):
                if self.graph[i][j].locked: continue
                
                numberOfState = len(queue)  if queue != [] else 1
                maxElement = maxElement if maxElement > numberOfState else numberOfState
                
                for _ in range(numberOfState):
                    loop += 1
                    front = queue.pop(0) if queue != [] else []
                    temp = copy.deepcopy(self.graph)
                    for k in range(len(front)):
                        row = front[k].row
                        col = front[k].col
                        times = front[k].times
                        for _ in range(times):
                            temp[row][col].leftRotate()
                    if type(temp[i][j]) is Ipipe:
                        for _ in range(2):
                            entry = copy.deepcopy(front) + [Transform(i, j, (_ + 1) % 2)]
                            temp[i][j].leftRotate()
                            if Graph.connectedComponent(temp) == 1:
                                return entry, maxElement, loop
                            queue += [entry]
                    else:
                        for _ in range(4):
                            entry = copy.deepcopy(front) + [Transform(i, j, (_ + 1) % 4)]
                            temp[i][j].leftRotate()
                            if Graph.connectedComponent(temp) == 1:
                                return entry, maxElement, loop
                            queue += [entry]
        return None

    def heuristicSolve(self) -> tuple[list[Transform], int, int, int, int] | None:
        preTransforms, preMaxElement, preLoop = self.preProcessing()     
        
        # the less connected components the better
        connectedBase = Graph.connectedComponent(self.graph)
        if connectedBase == 1: return preTransforms, preMaxElement, 0, preLoop, 0
        
        maxElement = 0
        loop = 0
        priorityQueue = PriorityQueue()
        # element of queue is tuple (connected: int, id: int, {"visited": False, "transforms": []})
        allVisited = pow(4, self.row*self.col)
        
        while priorityQueue.minConnected() != 1 or allVisited:
            loop += 1
            maxElement = maxElement if maxElement > priorityQueue.len() else priorityQueue.len()
            
            allVisited -= 1
            if priorityQueue.minConnected() == -1:
                transfroms =[]
            else:
                while not priorityQueue.isEmpty():
                    if priorityQueue.queue[0][2]["visited"] == True:
                        priorityQueue.delete()
                        continue
                    transfroms = copy.deepcopy(priorityQueue.queue[0][2]["transforms"])
                    priorityQueue.queue[0][2]["visited"] = True
                    break
            
            temp = copy.deepcopy(self.graph)
            lockTranforms = []
            
            for _ in transfroms:
                row = _.row
                col = _.col
                times = _.times
                for __ in range(times):
                    temp[row][col].leftRotate()
            
            i = -1 if transfroms == [] else transfroms[-1].row
            j = self.col if transfroms == [] else transfroms[-1].col
            
            i = i + 1 if j + 1 >= self.col else i
            j = j + 1 if j + 1 < self.col else 0
            
            while i < self.row and temp[i][j].locked:
                lockTranforms += lockAdjacent(temp, i, j)
                j += 1
                if j == self.col:
                    j = 0
                    i += 1
            
            if i >= self.row:
                continue        
            
            if type(temp[i][j]) is Ipipe:
                for _ in range(2):
                    temp[i][j].leftRotate()
                    if noHopeState(temp, i, j):
                        continue
                    newConnected = Graph.connectedComponent(temp)
                    newTransfroms = transfroms + lockTranforms + [Transform(i, j, (_ + 1) % 2)]
                    priorityQueue.insert(newConnected, {"visited": False, "transforms": newTransfroms})
            else:
                for _ in range(4):
                    temp[i][j].leftRotate()
                    if noHopeState(temp, i, j):
                        continue
                    newConnected = Graph.connectedComponent(temp)
                    newTransfroms = transfroms + lockTranforms + [Transform(i, j, (_ + 1) % 4)]
                    priorityQueue.insert(newConnected, {"visited": False, "transforms": newTransfroms})

            if not priorityQueue.isEmpty() and priorityQueue.queue[0][0] == 1:
                result = preTransforms + priorityQueue.queue[0][2]["transforms"]
                return result, preMaxElement, maxElement, preLoop, loop
        
        return None
    
    def solve(self, transformSteps: list[Transform]):
        for _ in transformSteps:
            # print(_.row, _.col, _.times)
            row = _.row
            col = _.col
            times = _.times
            for _ in range(times):
                self.graph[row][col].leftRotate()
        return self.graph