from cell_state import CellState
from task_status import TaskStatus

from collections import deque
import numpy as np
import random
import math

from bot import Bot

class Bot4(Bot):

    def start(self):
        super().start()

        # all cells might have leak
        self.leak_probability_grid = np.zeros((self.ship.ship_size, self.ship.ship_size), np.float16)

        # walls can not have leaks
        for y in range(0, self.ship.ship_size):
            for x in range(0, self.ship.ship_size):
                if (y, x) in self.ship.opened_cells:
                    self.leak_probability_grid[y, x] = 1 / len(self.ship.opened_cells)
        
        self.sense()


    def sense(self): # sense and update knownledge
        super().sense()
        # beep or not
        d = len(self.find_shortest_path(self.location, self.ship.leak_location)) # only using the leak location to find out if beep or not, 
        probability_equation = math.pow(math.e, -self.alpha * (d - 1))

        # P(beep in i)
        beep_in_i = 0
        for y in range(self.ship.ship_size):
            for x in range(self.ship.ship_size):
                if (y, x) in self.ship.opened_cells and (y, x) != self.location:
                    prob = self.leak_probability_grid[y, x] * math.pow(math.e, -self.alpha * (len(self.find_shortest_path(self.location, (y, x))) - 1))
                    beep_in_i += prob

        # Find P( leak in cell j | heard a beep in cell i )
        # = P(leak in j) (original prob in leak_probability_grid) * probability_equation / P(beep in i)
        for y in range(self.ship.ship_size):
            for x in range(self.ship.ship_size):
                if (y, x) != self.location and (y, x) in self.ship.opened_cells:
                    shortest_distance = len(self.find_shortest_path(self.location, (y, x)))
                    if random.random() <= probability_equation: # beep
                        self.leak_probability_grid[y, x] *= math.pow(math.e, -self.alpha * (shortest_distance - 1)) / beep_in_i
                    else: # no beep
                        self.leak_probability_grid[y, x] *= (1 - math.pow(math.e, -self.alpha * (shortest_distance - 1))) / (1 - beep_in_i)

    
    def bot_enters_cell_probability_update(self):
        for y in range(0, self.ship.ship_size):
            for x in range(0, self.ship.ship_size):
                if (y, x) in self.ship.opened_cells and (y, x) != self.location:
                    self.leak_probability_grid[y, x] /= (1 - self.leak_probability_grid[self.location])

        self.leak_probability_grid[self.location] = 0

    def update(self):
        super().update()

        self.bot_enters_cell_probability_update()
        self.sense()
        
        next_location = self.find_highest_probability_cell()


        path = self.find_shortest_path(self.location, next_location)
        for next_cell in path:
            if (self.ship.ship_grid[next_cell] == CellState.LEAK):
                return TaskStatus.SUCCESS, self.total_actions

            self.move(next_cell)
            self.bot_enters_cell_probability_update()

            # print(self.leak_probability_grid)
            # print(self.leak_probability_grid[next_location])

        return TaskStatus.ONGOING, -1

    def find_highest_probability_cell(self):
        search_radius = 10

        nearby_high_prob_cells = self.get_nearby_high_prob_cells(search_radius)

        if not nearby_high_prob_cells:
            return self.find_highest_probability_cell_old()

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
    
    # find the cell that has the highest probability of containing the leak
    def find_highest_probability_cell_old(self):
        # instead of moving to the nearest single cell that might contain the leak, I will move to the area that has the most cells that might contain the leak
        # finding the max local probability, which for the local prob of a cell, i'm just adding up all the cells in the detection area, higher the sum, more cells in that areas possibly contain the leak 
        max_local_probability = -99999999

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

        cluster_max_probability = -99999999

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if (y, x) != self.location and (y, x) in self.ship.opened_cells:
                    if self.leak_probability_grid[y, x] > cluster_max_probability:
                        cluster_max_probability = self.leak_probability_grid[y, x]


        cluster_max_probability_cells = []

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if (y, x) != self.location and (y, x) in self.ship.opened_cells:
                    if cluster_max_probability == self.leak_probability_grid[y, x]:
                        cluster_max_probability_cells.append((y, x))

        # print(cluster_max_probability_cells, cluster_max_probability, max_local_probability_cells, max_local_probability)
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
                    p = self.leak_probability_grid[y, x]
                    key = 0
                    if 0 <= p <= 0.001:
                        key = 0
                    elif 0.001 < p <= 0.002:
                        key = 0.5
                    elif 0.003 < p <= 1:
                        key = 1

                    current_cell_display = CellState.to_probability_display_string[key]

                    if x == len(self.leak_probability_grid[1]) - 1:
                        current_cell_display += "|"

                    print(current_cell_display, end="")

                print()
