import numpy as np
import random

from bots.bot1 import Bot1
from bots.bot2 import Bot2
from bots.bot3 import Bot3
from bots.bot4 import Bot4
from fire import Fire
from cell_state import CellState
from task_status import TaskStatus

class Ship:
    def __init__(self, D, flammability, bot_number, load_from_file = None):         
        self.ship_size = D 

        self.ship_grid = np.zeros((D, D), np.int8)

        self.opened_cells = set([])

        if load_from_file == None:        
            self.init_layout()
        else:
            self.load_ship_layout(load_from_file, D, D)

        self.bot_location, self.button_location, self.initial_fire_location = self.set_initial_states()
        self.opened_cells.remove(self.initial_fire_location)

        self.fire = Fire(self, self.initial_fire_location, flammability)

        if bot_number == 1:
            self.bot = Bot1(self, self.bot_location)
        elif bot_number == 2:
            self.bot = Bot2(self, self.bot_location)
        elif bot_number == 3:
            self.bot = Bot3(self, self.bot_location)
        elif bot_number == 4:
            self.bot = Bot4(self, self.bot_location)

        print("Running Simulation....")

    def start(self):
        start_status = self.bot.start()

        if start_status == TaskStatus.FAIL: # instant fail, no path available
            return TaskStatus.FAIL

    def update(self):
        bot_result = self.bot.update()
        fire_result = self.fire.update()

        if (bot_result == TaskStatus.FAIL or fire_result == TaskStatus.FAIL):
            return TaskStatus.FAIL
        
        return bot_result
            
     # if both return success, timestep completed sucessfully

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

    def set_initial_states(self):
        states = set([])

        while len(states) < 3:
            states.add(random.choice(list(self.opened_cells)))

        initial_bot_cell = states.pop()
        self.ship_grid[initial_bot_cell] = CellState.BOT
        
        initial_button_cell = states.pop()
        self.ship_grid[initial_button_cell] = CellState.BUTTON
        
        initial_fire_cell = states.pop()
        self.ship_grid[initial_fire_cell] = CellState.FIRE

        return initial_bot_cell, initial_button_cell, initial_fire_cell

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