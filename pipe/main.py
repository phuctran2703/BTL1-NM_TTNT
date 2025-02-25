# Databricks notebook source
import sys, pygame
import resource
import tracemalloc
import time
import json
from pipePuzzle import *
import os
import copy

os.environ['SDL_WINDOW_CENTERED'] = '1'  # Center all pygame windows

pygame.init()
size = width, height = 1200, 960

pygame.display.set_caption("PIPES PUZZLE")
icon = pygame.image.load("assets/icon.png")
pygame.display.set_icon(icon)
screen = pygame.display.set_mode(size)

# Default cell width for drawing the puzzle
CELL_WIDTH = 50  # This will be dynamically adjusted based on puzzle size

# Colors
BACKGROUND = (28, 37, 65)     # Deep navy blue background
PRIMARY = (86, 171, 147)      # Teal/mint green for pipes
SECONDARY = (120, 144, 156)   # Slate gray for secondary elements
ACCENT = (255, 140, 85)       # Coral orange for accents/highlights
TEXT_COLOR = (226, 232, 240)  # Light gray for text
BUTTON_HOVER = (108, 195, 171) # Lighter teal for hover states
GAME_AREA = (34, 44, 77)      # Slightly lighter than background for game area
ERROR_COLOR = (255, 99, 71)   # Tomato red for error messages

# Fonts
TITLE_FONT = pygame.font.SysFont('Corbel', 72)
MENU_FONT = pygame.font.SysFont('Corbel', 36)
INFO_FONT = pygame.font.SysFont('Corbel', 24)

# Menu states
MAIN_MENU = 0
ALGORITHM_MENU = 1
GAME_SCREEN = 2
PUZZLE_SIZE_MENU = 3

current_state = ALGORITHM_MENU
selected_algorithm = None

FILENAMES = [
    "2x1.json", "2x2.json", "3x3.json", "4x4.json", "5x5.json", 
    "7x7.json", "10x10.json","15x15.json","20x20.json", "25x25.json"
]

GRAPHS = [
    '1X2', '2X2', '3X3', '4X4', '5X5',
    '7X7', '10X10', '15X15', '20X20', '25X25'
]

# Stats
blind_stats = {'start_time': 0, 'end_time': 0, 'max_nodes': 0, 'loop': 0, 'mem_storage': [0, 0], 'status': ''}
heuristic_stats = {'start_time': 0, 'end_time': 0, 'pre_max_nodes': 0, 'pre_loop': 0, 
                  'max_nodes': 0, 'loop': 0, 'mem_storage': [0, 0], 'status': ''}

BLIND_SOLVE = pygame.font.SysFont('Corbel', 20) .render('Blind Solve' , True , (0, 0, 0))
HEURISTIC_SOLVE = pygame.font.SysFont('Corbel', 20) .render('Heuristic Solve' , True , (0, 0, 0))

def pipeImage(type, index, width):
    if type is Tpipe:
        image = pygame.image.load(f"assets/Tpipe{index}.png")
    elif type is Lpipe:
        image = pygame.image.load(f"assets/Lpipe{index}.png")
    elif type is Ipipe:
        image = pygame.image.load(f"assets/Ipipe{index}.png")
    else:
        image = pygame.image.load(f"assets/Epoint{index}.png")

    image = pygame.transform.scale(image, (width, width))
    
    # Apply teal color tint to the pipe images
    colored_surface = image.copy()
    colored_surface.fill(PRIMARY, special_flags=pygame.BLEND_RGBA_MULT)
    
    return colored_surface

def readGraph(fileName: str):
    mainGraph: list[list[Epoint | Tpipe | Lpipe | Ipipe]] = []
    
    with open(f"input/{fileName}", "r") as file:
        data = json.load(file)
    i = 0
    for _ in data:
        row = []
        j = 0
        for d in _:
            if d["type"] == "E":
                row += [Epoint(i, j, int(d["index"]))]
            elif d["type"] == "L":
                row += [Lpipe(i, j, int(d["index"]))]
            elif d["type"] == "T":
                row += [Tpipe(i, j, int(d["index"]))]
            elif d["type"] == "I":
                row += [Ipipe(i, j, int(d["index"]))]
            j += 1
        i += 1
        mainGraph += [row]
        
    return Graph(mainGraph)

def drawGraph(graph: Graph, BaseX, BaseY):
    baseY = BaseY
    
    for i in range(graph.row):
        baseX = BaseX
        for j in range(graph.col):
            t = type(graph.graph[i][j])
            index = graph.graph[i][j].index
            
            screen.blit(pipeImage(t, index, CELL_WIDTH), (baseX, baseY))
            baseX += CELL_WIDTH
        baseY += CELL_WIDTH

def drawDemoSolve(graph: Graph, transforms: list[Transform], BaseX, BaseY):
    baseY = BaseY
    
    for i in range(graph.row):
        baseX = BaseX
        for j in range(graph.col):
            t = type(graph.graph[i][j])
            index = graph.graph[i][j].index
            
            screen.blit(pipeImage(t, index, CELL_WIDTH), (baseX, baseY))
            baseX += CELL_WIDTH
        baseY += CELL_WIDTH
    
    baseY = BaseY
    baseX = BaseX
    
    for t in transforms:
        row = t.row
        col = t.col
        X = baseX + CELL_WIDTH*col
        Y = baseY + CELL_WIDTH*row
        for _ in range(t.times):
            t = type(graph.graph[row][col])
            
            graph.graph[row][col].leftRotate()
            index = graph.graph[row][col].index
            
            screen.blit(pipeImage(t, index, CELL_WIDTH), (X, Y))
            pygame.display.update()
            pygame.time.delay(300)

def draw_loading_screen(message):
    """Display a loading screen with the given message"""
    screen.fill(BACKGROUND)
    
    # Create loading text
    loading_text = TITLE_FONT.render(message, True, ACCENT)
    screen.blit(loading_text, ((width - loading_text.get_width()) // 2, height // 2 - 50))
    
    # Create a pulsing animation
    animation_time = (pygame.time.get_ticks() % 1000) / 1000.0  # Varies from 0 to 1
    dot_count = int(animation_time * 6) + 1  # 1 to 6 dots
    dots = "." * dot_count
    
    # Display dots
    dots_text = MENU_FONT.render(dots, True, TEXT_COLOR)
    screen.blit(dots_text, ((width - dots_text.get_width()) // 2, height // 2 + 20))
    
    pygame.display.flip()

def draw_game_result(stats, result_message, success=True):
    """Display algorithm results"""
    screen.fill(BACKGROUND)
    
    # Title
    title = TITLE_FONT.render(result_message, True, ACCENT if success else ERROR_COLOR)
    screen.blit(title, ((width - title.get_width()) // 2, 100))
    
    # Stats
    y_pos = 220
    line_height = 40
    
    stats_items = [
        f"Time taken: {stats['end_time'] - stats['start_time']:.2f} seconds",
        f"Iterations: {stats['loop']}",
        f"Max queue size: {stats['max_nodes']}",
        f"Peak memory usage: {stats['mem_storage'][1] / 1024 / 1024:.2f} MB"
    ]
    
    if 'status' in stats and stats['status']:
        stats_items.append(f"Status: {stats['status']}")
    
    for item in stats_items:
        stat_text = INFO_FONT.render(item, True, TEXT_COLOR)
        screen.blit(stat_text, ((width - stat_text.get_width()) // 2, y_pos))
        y_pos += line_height
    
    # Continue button
    continue_button = pygame.Rect((width - 200) // 2, y_pos + 40, 200, 60)
    draw_menu_button("Continue", continue_button)
    
    pygame.display.flip()
    
    # Wait for user to click continue
    waiting_for_click = True
    while waiting_for_click:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                if continue_button.collidepoint(pygame.mouse.get_pos()):
                    waiting_for_click = False

def solvedGraph(graph, type: str):
    solvedGraph: Graph = copy.deepcopy(graph)
    if type == 'blind':
        result = solvedGraph.blindSolve()
        if result is None:
            blind_stats['status'] = "Could not find solution (limits reached)"
            return None
        else:
            blind_stats['status'] = "Solution found"
            return result
    else:
        result = solvedGraph.heuristicSolve()
        if result is None:
            heuristic_stats['status'] = "Could not find solution (limits reached)"
            return None
        else:
            heuristic_stats['status'] = "Solution found"
            return result
    
def draw_menu_button(text, rect, hover=False):
    color = BUTTON_HOVER if hover else SECONDARY
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, ACCENT, rect, 2)  # Coral orange border
    text_surface = MENU_FONT.render(text, True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def draw_algorithm_menu():
    screen.fill(BACKGROUND)
    title = TITLE_FONT.render('Select Algorithm', True, ACCENT)  # Gold title
    screen.blit(title, ((width - title.get_width()) // 2, 100))
    
    buttons = [
        ('Blind Search (DFS)', pygame.Rect((width - 300) // 2, 300, 300, 60)),
        ('Heuristic Search (A*)', pygame.Rect((width - 300) // 2, 400, 300, 60)),
        ('Exit', pygame.Rect((width - 300) // 2, 500, 300, 60))
    ]
    
    mouse_pos = pygame.mouse.get_pos()
    for text, rect in buttons:
        hover = rect.collidepoint(mouse_pos)
        draw_menu_button(text, rect, hover)
    
    return buttons

def draw_puzzle_size_menu():
    screen.fill(BACKGROUND)
    title = TITLE_FONT.render('Select Puzzle Size', True, ACCENT)
    screen.blit(title, ((width - title.get_width()) // 2, 50))
    
    buttons = []
    button_width = 180  # Increased width for better spacing
    button_height = 50
    margin = 30  # Increased margin between buttons
    cols = 5
    
    # Create two rows of buttons
    sizes_row1 = ['1X2', '2X2', '3X3', '4X4', '5X5']
    sizes_row2 = ['7X7', '10X10', '15X15', '20X20', '25X25']
    
    # First row
    y = 200
    for i, size in enumerate(sizes_row1):
        x = (width - (button_width * cols + margin * (cols - 1))) // 2 + i * (button_width + margin)
        buttons.append((size, pygame.Rect(x, y, button_width, button_height)))
    
    # Second row
    y = 300  # More space between rows
    for i, size in enumerate(sizes_row2):
        x = (width - (button_width * cols + margin * (cols - 1))) // 2 + i * (button_width + margin)
        buttons.append((size, pygame.Rect(x, y, button_width, button_height)))
    
    # Back button at the bottom
    buttons.append(('Back', pygame.Rect((width - 150) // 2, height - 100, 150, 50)))
    
    # Draw a decorative box around the size buttons
    box_margin = 40
    box_rect = pygame.Rect(
        (width - (button_width * cols + margin * (cols - 1))) // 2 - box_margin,
        180,  # Slightly above first row
        (button_width * cols + margin * (cols - 1)) + box_margin * 2,
        200   # Height to encompass both rows
    )
    pygame.draw.rect(screen, SECONDARY, box_rect, 2)  # Draw border only
    
    # Draw buttons with hover effect
    mouse_pos = pygame.mouse.get_pos()
    for text, rect in buttons:
        hover = rect.collidepoint(mouse_pos)
        draw_menu_button(text, rect, hover)
    
    return buttons

def draw_game_screen():
    screen.fill(BACKGROUND)
    
    # Draw title
    title = TITLE_FONT.render(f"Puzzle {mainGraph.row}x{mainGraph.col}", True, ACCENT)
    screen.blit(title, ((width - title.get_width()) // 2, 50))
    
    # Calculate cell size based on puzzle dimensions
    global CELL_WIDTH
    max_puzzle_size = min(800, min(width, height) - 200)  # Leave margin
    CELL_WIDTH = min(100, max_puzzle_size // max(mainGraph.row, mainGraph.col))
    
    # Center position
    puzzle_width = CELL_WIDTH * mainGraph.col
    puzzle_height = CELL_WIDTH * mainGraph.row
    base_x = (width - puzzle_width) // 2
    base_y = (height - puzzle_height) // 2
    
    # Draw puzzle
    for i in range(mainGraph.row):
        for j in range(mainGraph.col):
            x = base_x + j * CELL_WIDTH
            y = base_y + i * CELL_WIDTH
            t = type(mainGraph.graph[i][j])
            index = mainGraph.graph[i][j].index
            screen.blit(pipeImage(t, index, CELL_WIDTH), (x, y))
    
    # Draw back button
    back_button = pygame.Rect(20, 20, 100, 40)
    draw_menu_button('Back', back_button)
    
    return back_button, base_x, base_y, CELL_WIDTH

def animate_solution(transforms, base_x, base_y, cell_size):
    """Animate the solution by showing each transformation step by step"""
    # Make a copy of the current graph to animate
    graph_copy = copy.deepcopy(mainGraph)
    
    for t in transforms:
        row, col = t.row, t.col
        x = base_x + col * cell_size
        y = base_y + row * cell_size
        
        for _ in range(t.times):
            # Redraw the entire screen to ensure it's up to date
            screen.fill(BACKGROUND)
            
            # Draw the title
            title = TITLE_FONT.render(f"Puzzle {graph_copy.row}x{graph_copy.col} - Solving", True, ACCENT)
            screen.blit(title, ((width - title.get_width()) // 2, 50))
            
            # Apply the transformation
            graph_copy.graph[row][col].leftRotate()
            
            # Draw the current state of the puzzle
            for i in range(graph_copy.row):
                for j in range(graph_copy.col):
                    pipe_x = base_x + j * cell_size
                    pipe_y = base_y + i * cell_size
                    pipe_type = type(graph_copy.graph[i][j])
                    pipe_index = graph_copy.graph[i][j].index
                    
                    # Highlight the current pipe being rotated
                    if i == row and j == col:
                        # Draw a highlight behind the pipe
                        highlight_rect = pygame.Rect(pipe_x-5, pipe_y-5, cell_size+10, cell_size+10)
                        pygame.draw.rect(screen, ACCENT, highlight_rect, 3)
                    
                    screen.blit(pipeImage(pipe_type, pipe_index, cell_size), (pipe_x, pipe_y))
            
            # Add a status message
            status = INFO_FONT.render(f"Rotating pipe at ({row+1},{col+1})", True, TEXT_COLOR)
            screen.blit(status, ((width - status.get_width()) // 2, base_y + graph_copy.row * cell_size + 30))
            
            pygame.display.flip()
            pygame.time.delay(200)  # Slightly faster animation for better UX

mainGraph = readGraph(FILENAMES[0])

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if current_state == GAME_SCREEN:
                current_state = ALGORITHM_MENU
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = pygame.mouse.get_pos()
            
            if current_state == MAIN_MENU:
                buttons = draw_main_menu()
                for text, rect in buttons:
                    if rect.collidepoint(mouse_pos):
                        if text == 'Play Game':
                            current_state = PUZZLE_SIZE_MENU
                        elif text == 'Solve with Algorithms':
                            current_state = ALGORITHM_MENU
                        elif text == 'Exit':
                            sys.exit()
            
            elif current_state == ALGORITHM_MENU:
                buttons = draw_algorithm_menu()
                for text, rect in buttons:
                    if rect.collidepoint(mouse_pos):
                        if text == 'Exit':
                            sys.exit()
                        elif text == 'Blind Search (DFS)':
                            selected_algorithm = 'blind'
                            current_state = PUZZLE_SIZE_MENU
                        elif text == 'Heuristic Search (A*)':
                            selected_algorithm = 'heuristic'
                            current_state = PUZZLE_SIZE_MENU
            
            elif current_state == PUZZLE_SIZE_MENU:
                buttons = draw_puzzle_size_menu()
                for text, rect in buttons:
                    if rect.collidepoint(mouse_pos):
                        if text == 'Back':
                            current_state = ALGORITHM_MENU if selected_algorithm else MAIN_MENU
                        else:
                            idx = GRAPHS.index(text)
                            mainGraph = readGraph(FILENAMES[idx])
                            current_state = GAME_SCREEN
                            
                            if selected_algorithm:
                                back_button, base_x, base_y, cell_size = draw_game_screen()
                                pygame.display.flip()
                                
                                if selected_algorithm == 'blind':
                                    draw_loading_screen("Running Blind Search")
                                    blind_stats['start_time'] = time.time()
                                    tracemalloc.start()
                                    
                                    result = solvedGraph(mainGraph, "blind")
                                    
                                    blind_stats['mem_storage'] = tracemalloc.get_traced_memory()
                                    tracemalloc.stop()
                                    blind_stats['end_time'] = time.time()
                                    
                                    if result:
                                        transforms, blind_stats['max_nodes'], blind_stats['loop'] = result
                                        animate_solution(transforms, base_x, base_y, cell_size)
                                        draw_game_result(blind_stats, "Blind Search Complete", True)
                                    else:
                                        draw_game_result(blind_stats, "Blind Search Failed", False)
                                        
                                else:
                                    draw_loading_screen("Running Heuristic Search")
                                    heuristic_stats['start_time'] = time.time()
                                    tracemalloc.start()
                                    
                                    result = solvedGraph(mainGraph, "heuristic")
                                    
                                    heuristic_stats['mem_storage'] = tracemalloc.get_traced_memory()
                                    tracemalloc.stop()
                                    heuristic_stats['end_time'] = time.time()
                                    
                                    if result:
                                        transforms, heuristic_stats['pre_max_nodes'], heuristic_stats['max_nodes'], heuristic_stats['pre_loop'], heuristic_stats['loop'] = result
                                        animate_solution(transforms, base_x, base_y, cell_size)
                                        draw_game_result(heuristic_stats, "Heuristic Search Complete", True)
                                    else:
                                        draw_game_result(heuristic_stats, "Heuristic Search Failed", False)
                                        
                                current_state = ALGORITHM_MENU
            
            elif current_state == GAME_SCREEN:
                back_button, base_x, base_y, cell_size = draw_game_screen()
                
                if back_button.collidepoint(mouse_pos):
                    current_state = ALGORITHM_MENU
                else:
                    # Handle puzzle piece rotation
                    puzzle_width = cell_size * mainGraph.col
                    puzzle_height = cell_size * mainGraph.row
                    if (base_x <= mouse_pos[0] <= base_x + puzzle_width and 
                        base_y <= mouse_pos[1] <= base_y + puzzle_height):
                        col = (mouse_pos[0] - base_x) // cell_size
                        row = (mouse_pos[1] - base_y) // cell_size
                        if event.button == 1:  # Left click
                            mainGraph.graph[row][col].leftRotate()
                        else:  # Right click
                            mainGraph.graph[row][col].rightRotate()
    
    if current_state == ALGORITHM_MENU:
        draw_algorithm_menu()
    elif current_state == PUZZLE_SIZE_MENU:
        draw_puzzle_size_menu()
    elif current_state == GAME_SCREEN:
        draw_game_screen()
    
    pygame.display.update()