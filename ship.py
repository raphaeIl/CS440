# D x D np array
import numpy as np
import random
import time
import math

from bot import *
from fire import *

class CellState:
    CLOSED = 0
    OPENED = 1
    FIRE = 2
    BOT = 3
    BUTTON = 4

class Ship:
    def __init__(self, D, flammability):       
        self.D = D 
        self.flammability = flammability

        self.ship_grid = np.zeros((D, D), np.int8)

        self.opened_cells = set([])
        self.fire_cells = set([])

        self.init_layout()
        self.bot_location, self.button_location, self.initial_fire_location = self.get_initial_states()

        self.bot = Bot(self, self.bot_location)
        self.fire = Fire(self.initial_fire_location)


    def update(self):
        pass

    
    def render(self):
        self.display()

    def init_layout(self):
        initial_cell = (random.randint(0, self.D - 1), random.randint(0, self.D - 1))
        self.open_cell(initial_cell)
        self.display()

        selected_next_cell = self.get_available_cell()

        while selected_next_cell is not None:
            self.open_cell(selected_next_cell)
            self.display()
            # time.sleep(0.3)

            selected_next_cell = self.get_available_cell()


    def get_initial_states(self):
        states = set([])

        while len(states) < 3:
            states.add(random.choice(list(self.opened_cells)))

        initial_bot_cell = states.pop()
        initial_button_cell = states.pop()
        initial_fire_cell = states.pop()

        return initial_bot_cell, initial_button_cell, initial_fire_cell


    def open_cell(self, cell):
        print("Opening cell: ", cell)
        self.ship_grid[cell] = self.OPENED
        print(self.ship_grid[cell])
        self.opened_cells.add(cell)


    def get_available_cell(self):    
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

        print("Available Cells to open: ", available_cells)

        if len(available_cells) == 0:
            return None

        return available_cells[random.randint(0, len(available_cells) - 1)]


    def get_opened_neighbors(self, cell):
        opened_neighbors = []
        for neighbor in self.get_neighbors(cell):
            if self.ship_grid[neighbor] == self.OPENED:
                opened_neighbors.append(neighbor)

        return opened_neighbors
    

    def get_neighbors(self, cell):
        neighbors = set([])
        cell_y = cell[0]
        cell_x = cell[1]

        for y in range(max(0, cell_y - 1), min(cell_y + 2, self.D)):
            if (y == cell_y):
                for x in range(max(0, cell_x - 1), min(cell_x + 2, self.D)):
                    neighbors.add((y, x))

            neighbors.add((y, cell_x))
        
        neighbors.remove(cell)

        return neighbors


    def display(self):
        for x in range(len(self.ship_grid[0])):
            if x == 0:
                print(" _", end='')
            else:
                print("__", end='')

        print()
        for y in range(len(self.ship_grid[0])):
            print("|", end='')
            for x in range(len(self.ship_grid[1])):
                current_cell_display = " "

                if self.ship_grid[y, x] == CellState.CLOSED:
                    current_cell_display = "■"
                elif self.ship_grid[y, x] == self.FIRE:
                    current_cell_display = "F"

                if x == len(self.ship_grid[1]) - 1:
                    current_cell_display += "|"
                else:
                    current_cell_display += " "

                print(current_cell_display, end="")

            print()

        for x in range(len(self.ship_grid[0])):
            if x == 0:
                print(" ‾", end='')
            else:
                print("‾‾", end='')

        print()

