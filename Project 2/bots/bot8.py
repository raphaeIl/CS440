from cell_state import CellState
from task_status import TaskStatus

import random
import math

from bot import Bot
class Bot8(Bot):
    """
    For the Probabilistic Leak Detectors: Bot 8 and 9
    I used a dictionary to represent the knowledge base, it contains all unique possible combination of pairs of opened_cells as the keys (no duplicates), 
        where each key is in the format of: [(cell_a_y, cell_a_x), (pair_b_y, pair_b_x)]
          and each value is the probability of both pair_a and pair_b containing the leak = P(leak in j AND leak in k)

    The length of the dict is: length = n Choose 2 = (n * (n - 1)) / 2, where n is the length of the number of opened_cells, not the total number of cells in the ship
    
    For example, for a 2x2 ship (all open, n = 4), starting values for my dictionary would look like this (length = 4 * 3 / 2):
    {   
            key           :     value
        "[(0, 0), (0, 1)]":     1 / 6    
        "[(0, 0), (0, 1)]":     1 / 6       
        "[(0, 0), (1, 1)]":     1 / 6    
        "[(0, 1), (1, 0)]":     1 / 6    
        "[(0, 1), (1, 1)]":     1 / 6    
        "[(1, 0), (1, 1)]":     1 / 6    
        
    }

    I'm not really sure but I think this might be a bit easier than using for instance a higher dimension matrix to represent the pairs of probabilities
    """
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