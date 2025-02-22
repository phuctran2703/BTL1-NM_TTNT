import pygame
import time
import tracemalloc
import heapq
from sudoku_initialization import *

class SudokuSolver:
    def __init__(self, board, game=None):
        self.board = board
        self.game = game  # Thêm tham chiếu đến game để cập nhật giao diện

    def show_values(self, board=None):
        """Hiển thị giá trị trên bảng Sudoku"""
        if board != None:
            for x in range(BOARD_SIZE):
                for y in range(BOARD_SIZE):
                    self.board[x][y].value = board[x][y].value

        if self.game != None:
            self.game.draw_board()
            pygame.display.flip()
            time.sleep(0.1)
    
    def is_valid(self, x, y, num):
        for i in range(BOARD_SIZE):
            if self.board[x][i].value == num or self.board[i][y].value == num:
                return False
        box_x, box_y = (x // 3) * 3, (y // 3) * 3
        for i in range(3):
            for j in range(3):
                if self.board[box_x + i][box_y + j].value == num:
                    return False
        return True
    
    def get_empty_cells(self):
        return [(x, y) for x in range(BOARD_SIZE) for y in range(BOARD_SIZE) if self.board[x][y].value == 0]

    def solve_by_dfs(self):
        empty_cells = self.get_empty_cells()
        
        def dfs(index):
            if index == len(empty_cells):
                return True
            x, y = empty_cells[index]
            for num in range(1, 10):
                if self.is_valid(x, y, num):
                    self.board[x][y].value = num
                    self.show_values()

                    if dfs(index + 1):
                        return True
                    
                    self.board[x][y].value = 0
                    self.show_values()
            return False
        
        dfs(0)

    def possible_values(self, x, y):
        """Trả về tập hợp số có thể đặt tại (x, y)"""
        if self.board[x][y].value != 0:
            return set()  # Nếu ô đã có giá trị thì không còn lựa chọn nào

        box_x, box_y = (x // 3) * 3, (y // 3) * 3
        used_values = {self.board[x][i].value for i in range(BOARD_SIZE)} | \
                    {self.board[i][y].value for i in range(BOARD_SIZE)} | \
                    {self.board[box_x + i][box_y + j].value for i in range(3) for j in range(3)}
        
        return {num for num in range(1, 10) if num not in used_values}

    def heuristic_num_value(self, x, y):
        """Trả về số lượng giá trị có thể điền vào ô (x, y)"""
        return len(self.possible_values(x, y))
    
    def heuristic_degree(self, x, y, num):
        """Trả về số lượng ô chưa điền bị ảnh hưởng nếu đặt num vào (x, y)"""
        count = 0

        # Ảnh hưởng đến hàng
        for i in range(BOARD_SIZE):
            if self.board[x][i].value == 0 and num in self.possible_values(x, i):
                count += 1

        # Ảnh hưởng đến cột
        for i in range(BOARD_SIZE):
            if self.board[i][y].value == 0 and num in self.possible_values(i, y):
                count += 1

        # Ảnh hưởng đến khối 3x3
        box_x, box_y = (x // 3) * 3, (y // 3) * 3
        for i in range(3):
            for j in range(3):
                cell_x, cell_y = box_x + i, box_y + j
                if self.board[cell_x][cell_y].value == 0 and num in self.possible_values(cell_x, cell_y):
                    count += 1

        return count

    def solve_by_greedy(self):
        """Giải Sudoku bằng greedy search"""
        empty_cells = [(x, y) for x in range(BOARD_SIZE) for y in range(BOARD_SIZE) if self.board[x][y].value == 0]
        if not empty_cells:
            return True  # Hoàn thành

        # Chọn ô có ít lựa chọn nhất (MRV - Minimum Remaining Values)
        x, y = min(empty_cells, key=lambda cell: self.heuristic_num_value(cell[0], cell[1]))

        # Lấy danh sách giá trị có thể điền, ưu tiên Degree Heuristic
        possible_values = sorted(self.possible_values(x, y), key=lambda val: self.heuristic_degree(x, y, val))

        for num in possible_values:
            if self.is_valid(x, y, num):
                self.board[x][y].value = num
                self.show_values()

                if self.solve_by_greedy():
                    return True

                # Nếu điền sai, quay lui
                self.board[x][y].value = 0
                self.show_values()

        return False
    
    def heuristic_cost(self, x, y, num):
        """Trả về số lượng ô chưa điền và số lượng giá trị có thể trong ô và số lượng ô bị điền sai"""
        if not self.is_valid(x, y, num):
            return float("inf")
        
        empty_cell_count = len(self.get_empty_cells())
        possible_values_count = self.heuristic_num_value(x, y)
        
        return empty_cell_count*10 + possible_values_count

    def copy_board(self):
        """Tạo một bản sao của bảng"""
        new_board = [[Cell(x, y, self.board[x][y].value) for y in range(BOARD_SIZE)] for x in range(BOARD_SIZE)]
        return new_board
    
    def generate_next_states(self):
        """Sinh các trạng thái kế tiếp và thêm vào hàng đợi"""
        empty_cells = self.get_empty_cells()
        if not empty_cells:
            return []
        
        queue = []
        for x, y in empty_cells:
            for num in self.possible_values(x, y):
                new_board = self.copy_board()                
                new_board[x][y].value = num
                cost = self.heuristic_cost(x, y, num)
                if cost != float("inf"):
                    heapq.heappush(queue, (cost, new_board))
        return queue

    def solve_by_astar(self):
        """Giải Sudoku bằng thuật toán A*"""
        queue = self.generate_next_states()
        
        if not queue:
            return False  # Không có giá trị hợp lệ để thử

        while queue:
            _, next_board = heapq.heappop(queue)
            self.show_values(next_board)

            if not self.get_empty_cells():
                return True  # Hoàn thành
            
            for state in self.generate_next_states():
                heapq.heappush(queue, state)
        return False


    
def compare_algorithms():
    board1 = Board()
    board2 = board1.copy()
    solver1 = SudokuSolver(board1.board)
    solver2 = SudokuSolver(board2.board)

    # Measure DFS memory usage
    tracemalloc.start()
    start_time = time.time()
    solver1.solve_by_dfs()
    dfs_time = time.time() - start_time
    dfs_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Measure Greedy memory usage
    tracemalloc.start()
    start_time = time.time()
    solver2.solve_by_astar()
    greedy_time = time.time() - start_time
    greedy_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"DFS Time: {dfs_time} seconds")
    print(f"DFS Memory: {dfs_memory[1] - dfs_memory[0]} bytes")
    print(f"A* Time: {greedy_time} seconds")
    print(f"A* Memory: {greedy_memory[1] - greedy_memory[0]} bytes")


if __name__ == "__main__":
    for i in range(10):
        print("Loop",i,":")
        compare_algorithms()
    