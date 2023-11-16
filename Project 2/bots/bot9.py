from cell_state import CellState
from task_status import TaskStatus

from collections import deque
import numpy as np
import random
import math
from bot import Bot

class Bot9(Bot):

    def start(self):
        super().start()

        self.init_probability_grid()
        self.sense()
        self.leaks_found = 0        

    def init_probability_grid(self):
        self.opened_cells_list = list(self.ship.opened_cells)
        self.leak_probability_grid = { }
        pairs_count = (len(self.ship.opened_cells) * (len(self.ship.opened_cells) - 1)) / 2

        for a in range(0, len(self.ship.opened_cells)):
            for b in range(a + 1, len(self.ship.opened_cells)):
                self.leak_probability_grid[self.opened_cells_list[a], self.opened_cells_list[b]] = 1 / pairs_count

    def sense(self): # sense and update knownledge
        super().sense()
    
        # beep or not

        p_leak1 = 0
        p_leak2 = 0

        if self.ship.leak_location != None:
            d1 = len(self.find_shortest_path(self.location, self.ship.leak_location)) # only using the leak location to find out if beep or not, 
            p_leak1 = math.pow(math.e, -self.alpha * (d1 - 1))


        if self.ship.leak_location2 != None: 
            d2 = len(self.find_shortest_path(self.location, self.ship.leak_location2)) # only using the leak location to find out if beep or not, 
            p_leak2 = math.pow(math.e, -self.alpha * (d2 - 1))
        
        # P(beep in i)
        beep_in_i = 0

        for key in self.leak_probability_grid:
            j_does_cause_a_beep = (1 - math.pow(math.e, -self.alpha * ((len(self.find_shortest_path(self.location, key[0]))) - 1)))
            k_does_cause_a_beep = (1 - math.pow(math.e, -self.alpha * ((len(self.find_shortest_path(self.location, key[1]))) - 1)))
                
            beep_in_i += self.leak_probability_grid[key] * j_does_cause_a_beep * k_does_cause_a_beep

        # For beep in i: (equations in write-up)
        # P(leak in j AND leak in k | beep in i)

        # No beep in i:
        # 1 - P(leak in j AND leak in k | beep in i)
        for key in self.leak_probability_grid:
            cell_j, cell_k = key[0], key[1]

            if cell_j == self.location or cell_k == self.location:
                continue

            j_does_cause_a_beep = (1 - math.pow(math.e, -self.alpha * ((len(self.find_shortest_path(self.location, cell_j))) - 1)))
            k_does_cause_a_beep = (1 - math.pow(math.e, -self.alpha * ((len(self.find_shortest_path(self.location, cell_k))) - 1)))
            p_peak_in_j_and_leak_in_k = (self.leak_probability_grid[cell_j, cell_k] * (1 - (j_does_cause_a_beep) * (k_does_cause_a_beep))) / beep_in_i

            if random.random() <= p_leak1 or random.random() <= p_leak2: # beep 
                self.leak_probability_grid[cell_j, cell_k] = p_peak_in_j_and_leak_in_k
            else: # no beep
                self.leak_probability_grid[cell_j, cell_k] = 1 - p_peak_in_j_and_leak_in_k 


    def find_highest_probability_cell(self):
        max_probability = -999999
        max_probability_cells = [] # all cells with the highest probability

        for key in self.leak_probability_grid:
            if self.leak_probability_grid[key] > max_probability:
                max_probability = self.leak_probability_grid[key]

        for key in self.leak_probability_grid:
            if self.leak_probability_grid[key] > max_probability:
                max_probability = self.leak_probability_grid[key]

            if self.leak_probability_grid[key] == max_probability:
                max_probability_cells.append(key[0])


        # breaking ties by distance
        distances = [len(self.find_shortest_path(self.location, cell)) for cell in max_probability_cells]
        min_distance = min(distances)
        closest_cells = []

        for i in range(0, len(distances)):
            if distances[i] == min_distance:
                closest_cells.append(max_probability_cells[i])
        
        return random.choice(closest_cells) # chose one within all the cells with same distance
    
    def bot_enters_cell_probability_update(self):
        p = 0 # find the p of the cell that we entered, which is sum (cell we entered, pairs of that), set all to 0 and normalize rest
        for key in self.leak_probability_grid:
            if key[0] == self.location:
                p += self.leak_probability_grid[key]
                self.leak_probability_grid[key] = 0

        for key in self.leak_probability_grid:
            if key[0] != self.location:
                self.leak_probability_grid[key] /= (1 - p)
        # print("update, total sum of p: ", 1 - p)

    def update(self):
        super().update()

        self.bot_enters_cell_probability_update()
        self.sense()
        
        next_location = self.find_highest_probability_cell()
        path = self.find_shortest_path(self.location, next_location)
        
        for next_cell in path:
            if (self.ship.ship_grid[next_cell] == CellState.LEAK):
                # self.ship.render()

                self.leaks_found += 1
                if self.leaks_found == 2:
                    return TaskStatus.SUCCESS, self.total_actions

                if next_cell == self.ship.leak_location:
                    self.ship.leak_location = None
                else:
                    self.ship.leak_location2 = None

                print("First leak found at action: ", self.total_actions)
                self.init_probability_grid()

            self.move(next_cell)
            self.bot_enters_cell_probability_update()
        return TaskStatus.ONGOING, -1
    
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
        for x in range(self.ship.ship_size):
            if x == 0:
                print(" __", end='')
            else:
                print("__", end='')

        print()
        for y in range(self.ship.ship_size):
            print("|", end='')
            for x in range(self.ship.ship_size):
                p = 0

                for key in self.leak_probability_grid:
                    if key[0] == (y, x):
                        p += self.leak_probability_grid[key]

                key = 0
                if p <= 0:
                    key = 0
                else:
                    key = 1

                current_cell_display = CellState.to_probability_display_string[key]

                if x == self.ship.ship_size - 1:
                    current_cell_display += "|"

                print(current_cell_display, end="")

            print()