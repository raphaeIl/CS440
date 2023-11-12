import numpy as np
import random

from bots.bot1 import Bot1
from bots.bot2 import Bot2
from bots.bot3 import Bot3
from bots.bot4 import Bot4
from bots.bot5 import Bot5
from bots.bot6 import Bot6
from bots.bot7 import Bot7
from cell_state import CellState
from task_status import TaskStatus

class Ship:
    def __init__(self, D, detection_radius, bot_number, load_from_file = None):         
        self.ship_size = D 
        self.detection_radius = detection_radius
        self.ship_grid = np.zeros((D, D), np.int8)
        self.opened_cells = set([])

        if load_from_file == None:        
            self.init_layout()
        else:
            self.load_ship_layout(load_from_file, D, D)

        handle_multiple_leaks = bot_number >= 5

        self.bot_location, self.leak_location, self.leak_location2 = self.set_initial_states(handle_multiple_leaks)

        if bot_number == 1:
            self.bot = Bot1(self, self.bot_location, self.detection_radius)
        elif bot_number == 2:
            self.bot = Bot2(self, self.bot_location, self.detection_radius)
        elif bot_number == 3:
            self.bot = Bot3(self, self.bot_location, self.detection_radius)
        elif bot_number == 4:
            self.bot = Bot4(self, self.bot_location, self.detection_radius)
        elif bot_number == 5:
            self.bot = Bot5(self, self.bot_location, self.detection_radius)
        elif bot_number == 6:
            self.bot = Bot6(self, self.bot_location, self.detection_radius)
        elif bot_number == 7:
            self.bot = Bot7(self, self.bot_location, self.detection_radius)
        
        print("Running Simulation....")

    def start(self):
        self.bot.start()
        self.render()

    def update(self):
        bot_result = self.bot.update()

        if bot_result == TaskStatus.SUCCESS:
            return TaskStatus.SUCCESS
        
        return TaskStatus.ONGOING
                
    def render(self):
        self.display()

    def init_layout(self):
        print("Generating Ship Layout... Please wait...   ")
        dot = 0
        initial_cell = (random.randint(0, self.ship_size - 1), random.randint(0, self.ship_size - 1))
        self.open_cell(initial_cell)
        
        selected_next_cell = self.get_available_cells()

        while selected_next_cell is not None:
            self.open_cell(random.choice(selected_next_cell))
            # self.display()

            selected_next_cell = self.get_available_cells()

            dot += 1
            if dot % 400 == 0:
                print("\033[A                           \033[A")
                print("Generating Ship Layout... Please wait...   ")
            elif dot % 200 == 0:
                print("\033[A                           \033[A")
                print("Generating Ship Layout... Please wait..   ")
                
        dead_ends = self.get_dead_end_cells()
        
        # for i in range(len(dead_ends)):
        for i in range(int(len(dead_ends) / 2)):
            closed_neighbors = self.get_closed_neighbors(dead_ends[i])

            if (closed_neighbors is not None and len(closed_neighbors) > 0):
                self.open_cell(random.choice(closed_neighbors))

    # detects if leak is in an area, given center and radius
    def is_leak_in_area(self, area_center, area_radius):
        return (self.leak_location != None and self.location_is_in_square(self.leak_location, area_center, area_radius)) or \
            (self.leak_location2 != None and self.location_is_in_square(self.leak_location2, area_center, area_radius))

    # tuples (y, x)                                     k
    def location_is_in_square(self, location, square_center, radius):
            return square_center[0] - radius <= location[0] <= square_center[0] + radius and \
                    square_center[1] - radius <= location[1] <= square_center[1] + radius  
        

    def set_initial_states(self, handle_multiple_leaks):
        initial_bot_cell = random.choice(list(self.opened_cells))
        self.ship_grid[initial_bot_cell] = CellState.BOT
        
        opened_cells_outside_detection_square = [cell for cell in self.opened_cells if not self.location_is_in_square(cell, initial_bot_cell, self.detection_radius)]

        # display purposes, detection square
        for open_cell in self.opened_cells:
            if self.location_is_in_square(open_cell, initial_bot_cell, self.detection_radius) and open_cell != initial_bot_cell:
                # if abs(open_cell[0] - initial_bot_cell[0] == self.detection_radius) or abs(open_cell[1] - initial_bot_cell[1] == self.detection_radius):
                self.ship_grid[open_cell] = CellState.DETECTION_SQUARE

        initial_leak_cell = random.choice(opened_cells_outside_detection_square)
        self.ship_grid[initial_leak_cell] = CellState.LEAK
        
        opened_cells_outside_detection_square.remove(initial_leak_cell)

        initial_leak_cell2 = None

        if handle_multiple_leaks:
            initial_leak_cell2 = random.choice(opened_cells_outside_detection_square)
            self.ship_grid[initial_leak_cell2] = CellState.LEAK

        return initial_bot_cell, initial_leak_cell, initial_leak_cell2

    

    def open_cell(self, cell):
        # print("Opening cell: ", cell)
        self.ship_grid[cell] = CellState.OPENED
        # print(self.ship_grid[cell])
        self.opened_cells.add(cell)

    def get_dead_end_cells(self):
        # gets all the open cells that have one open neighbor
        dead_end_cells = []

        for open_cell in self.opened_cells:
            if len(self.get_opened_neighbors(open_cell)) == 1:
                dead_end_cells.append(open_cell)
        
        return dead_end_cells

    def get_available_cells(self):    
        # get all the neighbors of already opened cells, (since only those who are next to opened cells can have one or more neighbors)
        # do NOT include the opened cells
        # get the ones with one open neighbor
        # randomly select one
        # while the opened neighbors list is not empty
        available_cells = []

        for opened_cell in self.opened_cells:
            for neighbor in self.get_neighbors(opened_cell): 
                if neighbor not in self.opened_cells:
                    if len(self.get_opened_neighbors(neighbor)) == 1:
                        available_cells.append(neighbor)

        # print("Available Cells to open: ", available_cells)

        if len(available_cells) == 0:
            return None

        return available_cells

    def get_closed_neighbors(self, cell):
        closed_neighbors = []
        for neighbor in self.get_neighbors(cell):
            if self.ship_grid[neighbor] == CellState.CLOSED:
                closed_neighbors.append(neighbor)

        return closed_neighbors

    def get_opened_neighbors(self, cell):
        opened_neighbors = []
        for neighbor in self.get_neighbors(cell):
            if self.ship_grid[neighbor] != CellState.CLOSED:
                opened_neighbors.append(neighbor)

        return opened_neighbors

    def get_neighbors(self, cell):
        neighbors = set([])
        cell_y = cell[0]
        cell_x = cell[1]

        for y in range(max(0, cell_y - 1), min(cell_y + 2, self.ship_size)):
            if (y == cell_y):
                for x in range(max(0, cell_x - 1), min(cell_x + 2, self.ship_size)):
                    neighbors.add((y, x))

            neighbors.add((y, cell_x))
        
        neighbors.remove(cell)

        return neighbors

    def display(self):
        for x in range(len(self.ship_grid[0])):
            if x == 0:
                print(" __", end='')
            else:
                print("__", end='')

        print()
        for y in range(len(self.ship_grid[0])):
            print("|", end='')
            for x in range(len(self.ship_grid[1])):
                current_cell_display = CellState.to_display_string[self.ship_grid[y, x]]



                if x == len(self.ship_grid[1]) - 1:
                    current_cell_display += "|"
                # else:
                    # current_cell_display += ""

                print(current_cell_display, end="")

            print()

        for x in range(len(self.ship_grid[0])):
            if x == 0:
                print(" ‾‾", end='')
            else:
                print("‾‾", end='')

        print()

    def pre_generate_layouts(self, layout_count, layout_size):
        for i in range(1, layout_count + 1): # saving 100 50x50 layouts

            self.ship_size = layout_size

            self.ship_grid = np.zeros((self.ship_size, self.ship_size), np.int8)

            self.opened_cells = set([])

            self.init_layout()
            self.save_ship_layout(f"layout_{i}")

    def save_ship_layout(self, name):
        binary_str = ''.join([''.join(map(str, row)) for row in self.ship_grid])
        int_value = int(binary_str, 2)
        
        byte_length = (int_value.bit_length() + 7) // 8
        bytes = int_value.to_bytes(byte_length, 'big')

        with open(f"""saved_ship_layouts/{name}""", 'wb') as f:
            f.write(bytes)

    def load_ship_layout(self, name, nrows, ncols):
        with open(f"""saved_ship_layouts/{name}""", 'rb') as f:        
            byte_data = f.read()
        
        int_value = int.from_bytes(byte_data, 'big')
        binary_str = bin(int_value)[2:].zfill(nrows * ncols)
    
        loaded_layout = np.array([[int(binary_str[i * ncols + j]) for j in range(ncols)] for i in range(nrows)])
        self.ship_grid = loaded_layout

        for y in range(nrows):
            for x in range(ncols):
                if self.ship_grid[y, x] == CellState.OPENED:
                    self.opened_cells.add((y, x))