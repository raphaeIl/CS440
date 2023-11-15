from cell_state import CellState
from task_status import TaskStatus

from collections import deque
import numpy as np
import random
import math
import heapq
from bot import Bot
class Bot8(Bot):

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

        print(len(self.leak_probability_grid))
        print(pairs_count)

        # for key in self.leak_probability_grid:
            # print(key, self.leak_probability_grid[key])

    def sense(self): # sense and update knownledge
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

        for y in range(self.ship.ship_size):
            print("|", end='')
            for x in range(self.ship.ship_size):
                prob = 0 # P(k)

                for key in self.leak_probability_grid:
                    if key[0] == (y, x):
                        prob += self.leak_probability_grid[key] * math.pow(math.e, -self.alpha * (len(self.find_shortest_path(self.location, key[0])) - 1)) \
                                * math.pow(math.e, -self.alpha * (len(self.find_shortest_path(self.location, key[1])) - 1))

                beep_in_i += prob
                # print(beep_in_i)

        # For beep in i:
        # P(leak in j AND leak in k | beep in i)
        # = P(beep in i | leak in j and leak in k) * P(leak in j and leak in k) / P(beep in i)
        # where:
        # P(beep in i | leak in j and leak in k) = 1 - (1 - P( j does cause a beep in i | leak in cell j )) * (1 - P( k does cause a beep in i | leak in cell k ))
        # P(leak in j and leak in k) = self.leak_probability_grid[j, k]
        # P(beep in i) = beep_in_i above

        # No beep in i:
        # 1 - P(leak in j AND leak in k | beep in i)

        for a in range(0, len(self.ship.opened_cells)):
            for b in range(a + 1, len(self.ship.opened_cells)):
                cell_j, cell_k = self.opened_cells_list[a], self.opened_cells_list[b]

                if cell_j == self.location or cell_k == self.location:
                    continue

                if random.random() <= p_leak1 or random.random() <= p_leak2: # beep 
                    self.leak_probability_grid[cell_j, cell_k] *= 1 - (1 - math.pow(math.e, -self.alpha * (len(self.find_shortest_path(self.location, cell_j)) - 1))) * (1 - math.pow(math.e, -self.alpha * (len(self.find_shortest_path(self.location, cell_k)) - 1)))
                else: # no beep
                    self.leak_probability_grid[cell_j, cell_k] *= (1 - math.pow(math.e, -self.alpha * (len(self.find_shortest_path(self.location, cell_j)) - 1))) * (1 - math.pow(math.e, -self.alpha * (len(self.find_shortest_path(self.location, cell_k)) - 1)))

    def bot_enters_cell_probability_update(self):
        p = 0 # find the p of the cell that we entered, which is sum (cell we entered, pairs of that), set all to 0 and normalize rest
        for key in self.leak_probability_grid:
            if key[0] == self.location:
                p += self.leak_probability_grid[key]
                self.leak_probability_grid[key] = 0

        for key in self.leak_probability_grid:
            if key[0] != self.location:
                self.leak_probability_grid[key] /= (1 - p)
        print("update, total sum of p: ", 1 - p)

        # for y in range(0, self.ship.ship_size):
            # for x in range(0, self.ship.ship_size):
                # if (y, x) in self.ship.opened_cells and (y, x) != self.location:
                    # self.leak_probability_grid[y, x] /= (1 - p)
        
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

        for y in range(self.ship.ship_size):
            for x in range(self.ship.ship_size):
                p = 0

                for key in self.leak_probability_grid:
                    if key[0] == (y, x):
                        p += self.leak_probability_grid[key]

                if p > max_probability:
                    max_probability = p

        print(max_probability)

        for y in range(self.ship.ship_size):
            for x in range(self.ship.ship_size):
                p = 0

                for key in self.leak_probability_grid:
                    if key[0] == (y, x):
                        p += self.leak_probability_grid[key]

                if p == max_probability:
                    max_probability_cells.append((y, x))

        # breaking ties by distance
        distances = [len(self.find_shortest_path(self.location, cell)) for cell in max_probability_cells]
        min_distance = min(distances)
        closest_cells = []

        for i in range(0, len(distances)):
            if distances[i] == min_distance:
                closest_cells.append(max_probability_cells[i])
        
        print(min_distance, closest_cells)
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