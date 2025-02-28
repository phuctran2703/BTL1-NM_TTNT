from abc import ABC, abstractmethod 
import copy
import heapq
import time

# Base states for different pipe types
TPIPE_BASE_STATES = [
    [False, True, True, True],      # |-
    [True, True, True, False],      # _|_
    [True, True, False, True],      # -|
    [True, False, True, True]       # The rest
]
IPIPE_BASE_STATES = [
    [False, True, False, True],     # |
    [True, False, True, False]      # __
]
LPIPE_BASE_STATES = [
    [False, True, True, False],     # L
    [True, True, False, False],     # _|
    [True, False, False, True],     # ┐
    [False, False, True, True]      # The rest
]
EPOINT_BASE_STATES = [
    [True, False, False, False],    # -o
    [False, False, False, True],    # The rest
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
    
    def adjacent(self, graph, row, col):
        adj = []
        if col - 1 >= 0 and not graph[row][col - 1].visited and self.value()[0] and graph[row][col - 1].value()[2]:  
            adj += [(self.row, self.col - 1)]
        if row - 1 >= 0 and not graph[row - 1][col].visited and self.value()[1] and graph[row - 1][col].value()[3]: 
            adj += [(self.row - 1, self.col)]
        if col + 1 < len(graph[0]) and not graph[row][col + 1].visited and self.value()[2] and graph[row][col + 1].value()[0]: 
            adj += [(self.row, self.col + 1)]
        if row + 1 < len(graph) and not graph[row + 1][col].visited and self.value()[3] and graph[row + 1][col].value()[1]: 
            adj += [(self.row + 1, self.col)]
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
        self.index = 0 if self.index == 1 else 1
        
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
        heapq.heappush(self.queue, (connected, id(data), data))

    def delete(self):
        if not self.isEmpty():
            return heapq.heappop(self.queue)
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
                    
        return lockTransforms

def noHopeState(graph: list[list[Epoint | Tpipe | Lpipe | Ipipe]], row: int, col: int, preProcess: bool = False) -> bool:
    current = graph[row][col]
    left = graph[row][col - 1] if col - 1 >= 0 else None
    top = graph[row - 1][col] if row - 1 >= 0 else None
    right = graph[row][col + 1] if col + 1 < len(graph[0]) else None
    bottom = graph[row + 1][col] if row + 1 < len(graph) else None   
    
    if (not left and current.value()[0]) or \
       (not top and current.value()[1]) or \
       (not right and current.value()[2]) or \
       (not bottom and current.value()[3]) or \
       (left and (not preProcess or (preProcess and left.locked)) and left.value()[2] != current.value()[0]) or \
       (top and (not preProcess or (preProcess and top.locked)) and top.value()[3] != current.value()[1]) or \
       (right and right.locked and right.value()[0] != current.value()[2]) or \
       (bottom and bottom.locked and bottom.value()[1] != current.value()[3]):
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
        self.graph: list[list[Epoint | Tpipe | Ipipe | Lpipe]] = graph
        self.row = len(graph)
        self.col = len(graph[0])

    def preProcessing(self) -> tuple[list[Transform], int, int]:
        maxElements = 0
        loop = 0
        preTransforms = []
        floodFill = []
        
        # Process corners
        conners = [(0, 0), (0, self.col - 1), (self.row - 1, 0), (self.row - 1, self.col - 1)]
        for row, col in conners:
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
        
        # Process edges
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
        
        # Process flood fill
        while floodFill:
            loop += 1
            maxElements = max(maxElements, len(floodFill))
            
            row, col = floodFill.pop(0)
            if self.graph[row][col].visited:
                continue
            
            self.graph[row][col].visited = True
            steps = [(0, -1), (-1, 0), (0, 1), (1, 0)]
            
            for dx, dy in steps:            
                if not (0 <= col + dy < self.col and 0 <= row + dx < self.row):
                    continue
                    
                if self.graph[row + dx][col + dy].locked:
                    floodFill += [(row + dx, col + dy)]
                    continue
                
                t = type(self.graph[row + dx][col + dy]) 
                count = 0
                max_rotations = 2 if t is Ipipe else 4
                
                for _ in range(max_rotations):
                    self.graph[row + dx][col + dy].leftRotate()
                    if not noHopeState(self.graph, row + dx, col + dy, True):
                        count += 1
            
                if count == 1:
                    count = 0
                    while noHopeState(self.graph, row + dx, col + dy, True):
                        count += 1
                        self.graph[row + dx][col + dy].leftRotate()
                    self.graph[row + dx][col + dy].locked = True
                    
                    if count != 0:
                        preTransforms += [Transform(row + dx, col + dy, count)]
                        floodFill += [(row + dx, col + dy)]

        # Reset visited flags
        for row in self.graph:
            for cell in row:
                cell.visited = False
        
        return preTransforms, maxElements, loop

    @staticmethod
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

    def _get_state_hash(self, graph):
        return tuple(cell.index for row in graph for cell in row)

    def blindSolve(self) -> tuple[list[Transform], int, int] | None:
        priorityQueue = PriorityQueue()
        priorityQueue.insert(float('inf'), {"transforms": []})
        
        visited = set()
        maxElement = 0
        loop = 0
        best_connected = float('inf')
        best_transforms = None
        
        try:
            while not priorityQueue.isEmpty():
                loop += 1
                maxElement = max(maxElement, priorityQueue.len())
                
                current = priorityQueue.delete()
                transforms = current[2]["transforms"]
                
                temp = copy.deepcopy(self.graph)
                for t in transforms:
                    for _ in range(t.times):
                        temp[t.row][t.col].leftRotate()
                
                state_hash = self._get_state_hash(temp)
                if state_hash in visited:
                    continue
                    
                visited.add(state_hash)
                connected = Graph.connectedComponent(temp)
                
                if connected == 1:
                    return transforms, maxElement, loop
                
                if connected < best_connected:
                    best_connected = connected
                    best_transforms = transforms
                
                for i in range(self.row):
                    for j in range(self.col):
                        if temp[i][j].locked:
                            continue
                        
                        original_pipe = copy.deepcopy(temp[i][j])
                        max_rotations = 2 if type(temp[i][j]) is Ipipe else 4
                        
                        for rot in range(1, max_rotations):
                            temp_pipe = copy.deepcopy(original_pipe)
                            for _ in range(rot):
                                temp_pipe.leftRotate()
                            temp[i][j] = temp_pipe
                            
                            if noHopeState(temp, i, j):
                                continue
                                
                            new_connected = Graph.connectedComponent(temp)
                            new_transforms = transforms + [Transform(i, j, rot)]
                            priorityQueue.insert(new_connected, {"transforms": new_transforms})
                        
                        temp[i][j] = original_pipe
                        
        except Exception as e:
            print(f"Error in blindSolve: {e}")
            return None
        
        return best_transforms, maxElement, loop if best_transforms else None

    def heuristicSolve(self) -> tuple[list[Transform], int, int, int, int] | None:
        preTransforms, preMaxElement, preLoop = self.preProcessing()     
        
        connectedBase = Graph.connectedComponent(self.graph)
        if connectedBase == 1: 
            return preTransforms, preMaxElement, 0, preLoop, 0
        
        maxElement = 0
        loop = 0
        priorityQueue = PriorityQueue()
        allVisited = pow(4, self.row*self.col)
        
        while priorityQueue.minConnected() != 1 or allVisited:
            loop += 1
            maxElement = max(maxElement, priorityQueue.len())
            
            allVisited -= 1
            if priorityQueue.minConnected() == -1:
                transfroms = []
            else:
                while not priorityQueue.isEmpty():
                    if priorityQueue.queue[0][2]["visited"]:
                        priorityQueue.delete()
                        continue
                    transfroms = copy.deepcopy(priorityQueue.queue[0][2]["transforms"])
                    priorityQueue.queue[0][2]["visited"] = True
                    break
            
            temp = copy.deepcopy(self.graph)
            lockTranforms = []
            
            for t in transfroms:
                for _ in range(t.times):
                    temp[t.row][t.col].leftRotate()
            
            i = -1 if not transfroms else transfroms[-1].row
            j = self.col if not transfroms else transfroms[-1].col
            
            i = i + 1 if j + 1 >= self.col else i
            j = 0 if j + 1 >= self.col else j + 1
            
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