from cell_state import CellState
from task_status import TaskStatus

from collections import deque
import numpy as np
import random

from bot import Bot

class Bot1(Bot):

    def start(self):
        start_status = super().start()


        # all cells might have leak
        self.leak_probability_grid = np.ones((self.ship.ship_size, self.ship.ship_size), np.int8)

        # walls can not have leaks
        for y in range(0, self.ship.ship_size):
            for x in range(0, self.ship.ship_size):
                if (y, x) not in self.ship.opened_cells:
                    self.leak_probability_grid[y, x] = 0
        
        self.sense()

    def sense(self): # sense and update knownledge
        # if sensed and no leak, mark everything in area 0
        # if sensed and leak, mark everything in area that are not 0 to 0.5 (possible), and everything outside 0
        # if only one 1 left, that must be leak
        sensed_leak = self.ship.is_leak_in_area(self.location, self.detection_radius)
        
        # detection square
        start_y, end_y, start_x, end_x = \
            max(0, self.location[0] - self.detection_radius), \
            min(self.ship.ship_size - 1, self.location[0] + self.detection_radius), \
            max(0, self.location[1] - self.detection_radius), \
            min(self.ship.ship_size - 1, self.location[1] + self.detection_radius)

        if sensed_leak:
            for y in range(0, self.ship.ship_size):
                for x in range(0, self.ship.ship_size):
                    if (y, x) not in self.ship.opened_cells:
                        continue

                    if self.ship.location_is_in_square((y, x), self.location, self.detection_radius):
                        if self.leak_probability_grid[y, x] != 0:
                            self.leak_probability_grid[y, x] = 1
                    else:
                        self.leak_probability_grid[y, x] = 0


        else:
            self.leak_probability_grid[start_y:end_y, start_x:end_x] = 0
        return sensed_leak
    
 
    def update(self):
        super().update()

        sensed_leak = self.sense()
        print(sensed_leak)
        
        nearest_cell = self.find_nearest_cell()
        path = self.find_shortest_path(self.location, nearest_cell)
        print(self.location, nearest_cell, path)
        for next_cell in path:

            if (self.ship.ship_grid[next_cell] == CellState.LEAK):
                return TaskStatus.SUCCESS

            self.leak_probability_grid[next_cell] = 0
            self.move(next_cell)

        # if no leak, move to highest % neighbor
        # if leak 
        self.render_probability_grid()

        return TaskStatus.ONGOING

    def find_nearest_cell(self):
        # print(self.leak_probability_grid)
        max_probability = self.leak_probability_grid.max()

        # print(max_probability)
        max_probability_cells = []

        for y in range(0, self.ship.ship_size):
            for x in range(0, self.ship.ship_size):
                if self.leak_probability_grid[y, x] == max_probability and (y, x) != self.location and (y, x) in self.ship.opened_cells:
                    max_probability_cells.append((y, x))
        
        distances = [self.manhattan_distance(self.location, cell) for cell in max_probability_cells]

        min_distance_cell = max_probability_cells[np.argmin(distances)]
        # random

        # print(min_distance_cell, self.manhattan_distance(self.location, min_distance_cell))
        # get max probability
        # get all cells with that porbability in a list
        # find all their distances
        # find the path to the nearest and moves towards

        return min_distance_cell

    def render_probability_grid(self):
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

    
    def manhattan_distance(self, a, b): # Manhattan Distance
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def find_shortest_path(self, start, destination):
        super().find_shortest_path(start, destination)
        queue = deque([(start, [])])
        visited = set()

        while len(queue) > 0:
            current, path = queue.popleft()

            visited.add(current)

            if current == destination:
                return path + [current]

            for neighbor in self.ship.get_opened_neighbors(current):
                if neighbor in visited:
                    continue

                queue.append((neighbor, path + [current]))

        return None



            # area = self.leak_probability_grid[start_y:end_y, start_x:end_x]


            # for y in range(start_y, end_y + 1):
            #     for x in range(start_x, end_x + 1):
            #         if self.leak_probability_grid[y, x] != 0 and (y, x) in self.ship.opened_cells:
            #             self.leak_probability_grid[y, x] = 1

            # mask = np.zeros_like(self.leak_probability_grid, dtype=bool)
            # mask[start_y:end_y, start_x:end_x] = True
            
            # for y in range(0, self.ship.ship_size):
            #     for x in range(0, self.ship.ship_size):
            #         if (y, x) not in self.ship.opened_cells:
            #             mask[start_y:end_y, start_x:end_x] = True

            # self.leak_probability_grid[~mask] = 0

            # self.leak_probability_grid[start_y:end_y, start_x:end_x][area == 1] = 0.5