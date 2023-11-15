from cell_state import CellState
from task_status import TaskStatus

from collections import deque
import numpy as np
import random

from bot import Bot

class Bot6(Bot):

    def start(self):
        super().start()

        self.init_probability_grid()
        self.sense()
        self.leaks_found = 0
        

    def init_probability_grid(self):
        # all cells might have leak at start
        self.leak_probability_grid = np.ones((self.ship.ship_size, self.ship.ship_size), np.int8)
        self.current_path = deque()
        # walls can not have leaks
        for y in range(0, self.ship.ship_size):
            for x in range(0, self.ship.ship_size):
                if (y, x) not in self.ship.opened_cells:
                    self.leak_probability_grid[y, x] = CellState.P_NO_LEAK


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
                self.leaks_found += 1
                if self.leaks_found == 2:
                    return TaskStatus.SUCCESS, self.total_actions

                if next_cell == self.ship.leak_location:
                    self.ship.leak_location = None
                else:
                    self.ship.leak_location2 = None

                print("First leak found at action: ", self.total_actions)
                self.init_probability_grid()

            self.leak_probability_grid[next_cell] = 0
            self.ship.ship_grid[next_cell] = CellState.OPENED
            self.move(next_cell)

        return TaskStatus.ONGOING, -1

    
    def find_nearest_cell(self):
        # Define a search radius based on the ship size or other criteria
        search_radius = min(10, self.ship.ship_size // 2)

        # Get nearby cells with high probability
        nearby_high_prob_cells = self.get_nearby_high_prob_cells(search_radius)

        # If no nearby high probability cells, default to previous method
        if not nearby_high_prob_cells:
            return self.find_nearest_cell_old()

        # Use A* or another efficient pathfinding algorithm
        paths_and_distances = [(cell, self.find_shortest_path(self.location, cell)) for cell in nearby_high_prob_cells]
        min_distance_cell, _ = min(paths_and_distances, key=lambda x: len(x[1]))

        return min_distance_cell

    def get_nearby_high_prob_cells(self, radius):
        y, x = self.location
        nearby_cells = []

        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                new_y, new_x = y + dy, x + dx
                if 0 <= new_y < self.ship.ship_size and 0 <= new_x < self.ship.ship_size:
                    if self.leak_probability_grid[new_y, new_x] == CellState.P_MIGHT_CONTAIN_LEAK and (new_y, new_x) in self.ship.opened_cells:
                        nearby_cells.append((new_y, new_x))

        return nearby_cells
    
    def find_nearest_cell_old(self):
        # instead of moving to the nearest single cell that might contain the leak, I will move to the area that has the most cells that might contain the leak
        # finding the max local probability, which for the local prob of a cell, i'm just adding up all the cells in the detection area, higher the sum, more cells in that areas possibly contain the leak 
        max_local_probability = 0

        for y in range(0, self.ship.ship_size):
            for x in range(0, self.ship.ship_size):
                start_y, end_y, start_x, end_x = max(0, y - self.detection_radius), min(self.ship.ship_size, y + self.detection_radius + 1), max(0, x - self.detection_radius), min(self.ship.ship_size, x + self.detection_radius + 1)
                local_probability = self.leak_probability_grid[start_y:end_y, start_x:end_x].sum()

                if (y, x) != self.location and (y, x) in self.ship.opened_cells:
                    if local_probability > max_local_probability:
                        max_local_probability = local_probability

        # find all cell that has the max local probability amount the max single ones
        max_local_probability_cells = []

        for y in range(0, self.ship.ship_size):
            for x in range(0, self.ship.ship_size):
                start_y, end_y, start_x, end_x = max(0, y - self.detection_radius), min(self.ship.ship_size, y + self.detection_radius + 1), max(0, x - self.detection_radius), min(self.ship.ship_size, x + self.detection_radius + 1)
                local_probability = self.leak_probability_grid[start_y:end_y, start_x:end_x].sum()
                
                if (y, x) != self.location and (y, x) in self.ship.opened_cells:
                    if local_probability == max_local_probability:
                        max_local_probability_cells.append((y, x))
    

        # in case that there is multiple ones with the max probability, choose the nearest one by distance
        distances = []

        for cell in max_local_probability_cells:
            shortest_path = self.find_shortest_path(self.location, cell)

            distances.append(len(shortest_path))

        min_distance_cell = max_local_probability_cells[np.argmin(distances)]

        # for that nearest cluster, find the largest prob in that cluster and that is the target
        start_y, end_y, start_x, end_x = max(0, min_distance_cell[0] - self.detection_radius), min(self.ship.ship_size, min_distance_cell[0] + self.detection_radius + 1), max(0, min_distance_cell[1] - self.detection_radius), min(self.ship.ship_size, min_distance_cell[1] + self.detection_radius + 1)

        cluster_max_probability = 0
        
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if (y, x) != self.location and (y, x) in self.ship.opened_cells:
                    if self.leak_probability_grid[y, x] > cluster_max_probability:
                        cluster_max_probability = self.leak_probability_grid[y, x]

        cluster_max_probability_cells = []

        print(cluster_max_probability, cluster_max_probability_cells)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if (y, x) != self.location and (y, x) in self.ship.opened_cells:
                    if cluster_max_probability == self.leak_probability_grid[y, x]:
                        cluster_max_probability_cells.append((y, x))

        cluster_distances = []

        for cell in cluster_max_probability_cells:
            shortest_path = self.find_shortest_path(self.location, cell)

            cluster_distances.append(len(shortest_path))

        final_min_distance_cell = cluster_max_probability_cells[np.argmin(cluster_distances)]

        return final_min_distance_cell


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
