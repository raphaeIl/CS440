from cell_state import CellState
from task_status import TaskStatus

from collections import deque
import numpy as np

from bot import Bot

class Bot1(Bot):

    def start(self):
        super().start()

        # all cells might have leak at start
        self.leak_probability_grid = np.ones((self.ship.ship_size, self.ship.ship_size), np.int8)

        # walls can not have leaks
        for y in range(0, self.ship.ship_size):
            for x in range(0, self.ship.ship_size):
                if (y, x) not in self.ship.opened_cells:
                    self.leak_probability_grid[y, x] = CellState.P_NO_LEAK
        
        self.sense()

    def sense(self):
        sensed_leak = super().sense()

        # detection square bounds
        start_y, end_y, start_x, end_x = \
            max(0, self.location[0] - self.detection_radius), \
            min(self.ship.ship_size, self.location[0] + self.detection_radius + 1), \
            max(0, self.location[1] - self.detection_radius), \
            min(self.ship.ship_size, self.location[1] + self.detection_radius + 1)

        if sensed_leak: # if sensed and leak, mark everything in area that are not 0 to 1 and everything outside 0
            dection_area = np.zeros_like(self.leak_probability_grid, dtype=bool) # using mask to set everything ouside to 0, notice I'm not updating anything inside the detection area, that is not nessary since this probability matrix is binary, all possible leak cells in this area is marked with possible to begin with
            dection_area[start_y:end_y, start_x:end_x] = True
            self.leak_probability_grid[~dection_area] = 0
        else:           # if sensed and no leak, mark everything in area 0
            self.leak_probability_grid[start_y:end_y, start_x:end_x] = 0

        return sensed_leak
    
 
    def update(self):
        super().update()

        self.sense()
        nearest_cell = self.find_nearest_cell()

        # Since the instruction did not say to sense at every move, I will just directly go to the "nearest" cell without sensing at every move
        path = self.find_shortest_path(self.location, nearest_cell)

        for next_cell in path:
            if (self.ship.ship_grid[next_cell] == CellState.LEAK):
                return TaskStatus.SUCCESS, self.total_actions

            self.leak_probability_grid[next_cell] = 0
            self.move(next_cell)

        return TaskStatus.ONGOING, -1

    def find_nearest_cell(self):
        max_probability = CellState.P_MIGHT_CONTAIN_LEAK # max probability for any cell is 1 (since this probability matrix is binary, either contain or does not contain leak)
        max_probability_cells = []

        # find all cells with max prob (ignoring the current one the bot is in and all walls)
        for y in range(0, self.ship.ship_size):
            for x in range(0, self.ship.ship_size):
                if self.leak_probability_grid[y, x] == max_probability and (y, x) != self.location and (y, x) in self.ship.opened_cells:
                    max_probability_cells.append((y, x))
        
        # find the closest distance cell with max probability
        distances = [len(self.find_shortest_path(self.location, cell)) for cell in max_probability_cells]
        min_distance_cell = max_probability_cells[np.argmin(distances)]

        return min_distance_cell

    
    def render_probability_grid(self):  # this is for console display purposes, please ignore
        for x in range(len(self.leak_probability_grid[0])):
            if x == 0:
                print(" __", end='')
            else:
                print("__", end='')

        print()
        for y in range(len(self.leak_probability_grid[0])):
            print("|", end='')
            for x in range(len(self.leak_probability_grid[1])):
                current_cell_display = CellState.to_probability_display_string[self.leak_probability_grid[y, x]]

                if x == len(self.leak_probability_grid[1]) - 1:
                    current_cell_display += "|"

                print(current_cell_display, end="")

            print()
