# D x D np array
import numpy as np
import random
import time
import math

from bot import Bot
from fire import Fire
from cell_state import CellState
from task_status import TaskStatus

class Ship:
    def __init__(self, D, flammability):       
        self.ship_size = D 

        self.ship_grid = np.zeros((D, D), np.int8)

        self.opened_cells = set([])

        self.init_layout()
        self.bot_location, self.button_location, self.initial_fire_location = self.set_initial_states()

        self.bot = Bot(self, self.bot_location)
        self.fire = Fire(self, self.initial_fire_location, flammability)

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
        initial_cell = (random.randint(0, self.ship_size - 1), random.randint(0, self.ship_size - 1))
        self.open_cell(initial_cell)
        self.display()

        selected_next_cell = self.get_available_cell()

        while selected_next_cell is not None:
            self.open_cell(selected_next_cell)
            self.display()
            # time.sleep(0.3)

            selected_next_cell = self.get_available_cell()


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
        print("Opening cell: ", cell)
        self.ship_grid[cell] = CellState.OPENED
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

