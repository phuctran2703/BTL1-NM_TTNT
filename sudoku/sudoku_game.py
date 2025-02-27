import pygame
from sudoku_initialization import *
from sudoku_solver import *

# Kích thước
CELL_SIZE = 60
WINDOW_SIZE = CELL_SIZE * BOARD_SIZE  

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 200, 0)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 100))  # Thêm không gian cho nút
        pygame.display.set_caption("Sudoku")
        self.font = pygame.font.Font(None, 40)
        self.running = True
        self.board = Board()
        self.selected_cell = None
        self.state = "start"  # "start", "playing", "end", "solving"
        self.win = False
        self.solver = SudokuSolver(self.board.board, self)

    def draw_button(self, text, x, y, width, height, color, action=None):
        """Vẽ nút bấm"""
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, color, rect)
        text_surface = self.font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
        return rect

    def draw_board(self):
        """Vẽ bảng Sudoku"""
        self.screen.fill(WHITE)
        
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                cell = self.board.board[x][y]
                rect = pygame.Rect(y * CELL_SIZE, x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, GRAY, rect, 1)

                if cell.value != 0:
                    color = BLACK if cell.fixed else BLUE
                    text_surface = self.font.render(str(cell.value), True, color)
                    self.screen.blit(text_surface, (y * CELL_SIZE + 20, x * CELL_SIZE + 15))

        for i in range(0, BOARD_SIZE+1, 3):
            pygame.draw.line(self.screen, BLACK, (0, i * CELL_SIZE), (WINDOW_SIZE, i * CELL_SIZE), 3)
            pygame.draw.line(self.screen, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, WINDOW_SIZE), 3)

        if self.selected_cell:
            x, y = self.selected_cell
            rect = pygame.Rect(y * CELL_SIZE, x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, BLUE, rect, 3)

        # Vẽ nút Submit
        self.submit_button = self.draw_button("Submit", (WINDOW_SIZE - 300) // 2, WINDOW_SIZE + 20, 300, 50, GREEN)

    def draw_start_screen(self):
        """Vẽ màn hình bắt đầu"""
        self.screen.fill(WHITE)
        text_surface = self.font.render("SUDOKU GAME", True, BLACK)
        text_rect = text_surface.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 3))
        self.screen.blit(text_surface, text_rect)
        self.start_button = self.draw_button("Start Game", (WINDOW_SIZE - 300) // 2, WINDOW_SIZE // 2, 300, 50, BLUE)
        self.dfs_button = self.draw_button("Solving by DFS", (WINDOW_SIZE - 300) // 2, WINDOW_SIZE // 2 + 70, 300, 50, BLUE)
        self.astar_button = self.draw_button("Solving by Astar", (WINDOW_SIZE - 300) // 2, WINDOW_SIZE // 2 + 140, 300, 50, BLUE)
        # self.greedy_button = self.draw_button("Solving by Greedy", (WINDOW_SIZE - 300) // 2, WINDOW_SIZE // 2 + 210, 300, 50, BLUE)
        self.greedy_button = self.draw_button("Solving by Greedy", (WINDOW_SIZE - 300) // 2, WINDOW_SIZE // 2 + 210, 0, 0, BLUE)

    def draw_end_screen(self):
        """Vẽ màn hình kết thúc"""
        self.screen.fill(WHITE)
        text = "YOU WIN!" if self.win else "YOU LOSE!"
        color = GREEN if self.win else RED
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 3))
        self.screen.blit(text_surface, text_rect)
        self.restart_button = self.draw_button("Restart", (WINDOW_SIZE - 300) // 2, WINDOW_SIZE // 2, 300, 50, BLUE)

    def handle_mouse_click(self, pos):
        """Xử lý sự kiện nhấn chuột"""
        if self.state == "start":
            if self.start_button.collidepoint(pos):
                self.state = "playing"
            elif self.dfs_button.collidepoint(pos):
                self.state = "solving_by_dfs"
                self.solver.solve_by_dfs()
            elif self.greedy_button.collidepoint(pos):
                self.state = "solving_by_greedy"
                self.solver.solve_by_greedy()
            elif self.astar_button.collidepoint(pos):
                self.state = "solving_by_astar"
                self.solver.solve_by_astar()
        elif self.state == "playing" or self.state == "solving_by_dfs" or self.state == "solving_by_greedy" or self.state == "solving_by_astar":
            if self.submit_button.collidepoint(pos):
                self.win = self.board.is_solved()
                self.state = "end"
            else:
                x, y = pos[1] // CELL_SIZE, pos[0] // CELL_SIZE
                self.selected_cell = (x, y)
        elif self.state == "end":
            if self.restart_button.collidepoint(pos):
                self.__init__()

    def handle_keypress(self, key):
        """Xử lý nhập số"""
        if self.state == "playing" and self.selected_cell:
            x, y = self.selected_cell
            cell = self.board.board[x][y]
            if not cell.fixed and key in range(pygame.K_1, pygame.K_9 + 1):
                cell.value = key - pygame.K_0

    def run(self):
        """Vòng lặp chính của trò chơi"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    self.handle_keypress(event.key)

            if self.state == "start":
                self.draw_start_screen()
            elif self.state == "playing":
                self.draw_board()
            elif self.state == "end":
                self.draw_end_screen()

            pygame.display.flip()

        pygame.quit()

# Chạy game
if __name__ == "__main__":
    game = Game()
    game.run()
