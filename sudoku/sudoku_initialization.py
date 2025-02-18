import random
import numpy as np

BOARD_SIZE = 9 # Kích thước của bảng sudoku

random.seed(0)
np.random.seed(0)

class Cell:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value
        self.fixed = True

class Board:
    def __init__(self):
        self.board = [[Cell(x, y, 0) for y in range(BOARD_SIZE)] for x in range(BOARD_SIZE)]
        self.generate_board()
        self.remove_numbers(40)
    
    def generate_board(self):
        """Tạo một bảng Sudoku hợp lệ"""
        base = np.array([[((i * 3 + i // 3 + j) % 9) + 1 for j in range(9)] for i in range(9)])  
        for i in range(0, 9, 3):
            np.random.shuffle(base[i:i+3, :])
        base = base.T
        for i in range(0, 9, 3):
            np.random.shuffle(base[i:i+3, :])
        base = base.T  

        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                self.board[x][y].value = base[x, y]

    def remove_numbers(self, num_to_remove=40):
        """Xóa số ngẫu nhiên để tạo Sudoku"""
        positions = [(x, y) for x in range(BOARD_SIZE) for y in range(BOARD_SIZE)]
        random.shuffle(positions)
        for i in range(num_to_remove):
            x, y = positions[i]
            self.board[x][y].value = 0
            self.board[x][y].fixed = False  # Những ô trống có thể chỉnh sửa

    def is_solved(self):
        """Kiểm tra xem Sudoku đã hoàn thành đúng chưa"""
        for row in range(BOARD_SIZE):
            if len(set(self.board[row][col].value for col in range(BOARD_SIZE))) != BOARD_SIZE:
                return False
        for col in range(BOARD_SIZE):
            if len(set(self.board[row][col].value for row in range(BOARD_SIZE))) != BOARD_SIZE:
                return False
        return True
    
    def copy(self):
        """Tạo một bản sao của bảng"""
        new_board = Board()
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                new_board.board[x][y].value = self.board[x][y].value
                new_board.board[x][y].fixed = self.board[x][y].fixed
        return new_board
    
    def show_values(self):
        """Hiển thị giá trị các ô"""
        for row in self.board:
            print([cell.value for cell in row])

if __name__ == "__main__":
    sudoku = Board()
    sudoku.show_values()