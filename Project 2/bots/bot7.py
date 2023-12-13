from cell_state import CellState
from task_status import TaskStatus

import numpy as np
import random
import math

from bot import Bot
class Bot7(Bot):

    def start(self):
        super().start()

        self.init_probability_grid()
        self.sense()
        self.leaks_found = 0        

    def init_probability_grid(self):
        self.leak_probability_grid = np.zeros((self.ship.ship_size, self.ship.ship_size), np.float16)

        # walls can not have leaks
        for y in range(0, self.ship.ship_size):
            for x in range(0, self.ship.ship_size):
                if (y, x) in self.ship.opened_cells:
                    self.leak_probability_grid[y, x] = 1 / len(self.ship.opened_cells)

    def sense(self): # sense and update knownledge
        sensed_leak = super().sense()
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
            for x in range(self.ship.ship_size):
                if (y, x) in self.ship.opened_cells:
                    prob = self.leak_probability_grid[y, x] * math.pow(math.e, -self.alpha * (len(self.find_shortest_path(self.location, (y, x))) - 1))
                    beep_in_i += prob
                    # print(prob)

        # print("P(beep in i)", beep_in_i)

        # Find P( leak in cell j | heard a beep in cell i )
        # = P(leak in j) (original prob in leak_probability_grid) * probability_equation / P(beep in i)
        # P(beep in i)
        for y in range(self.ship.ship_size):
            for x in range(self.ship.ship_size):
                if (y, x) != self.location and (y, x) in self.ship.opened_cells:
                    shortest_distance = len(self.find_shortest_path(self.location, (y, x)))
                    if random.random() <= p_leak1 or random.random() <= p_leak2: # beep
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
        max_probability = self.leak_probability_grid.max()
        max_probability_cells = [] # all cells with the highest probability

        for y in range(0, self.ship.ship_size):
            for x in range(0, self.ship.ship_size):
                if self.leak_probability_grid[y, x] == max_probability and (y, x) != self.location and (y, x) in self.ship.opened_cells:
                    max_probability_cells.append((y, x))
        
        # breaking ties by distance
        distances = [len(self.find_shortest_path(self.location, cell)) for cell in max_probability_cells]
        min_distance = min(distances)
        closest_cells = []

        for i in range(0, len(distances)):
            if distances[i] == min_distance:
                closest_cells.append(max_probability_cells[i])
        
        return random.choice(closest_cells) # chose one within all the cells with same distance


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
                if 0 <= p <= 0.333333:
                    key = 0
                elif 0.3333333 < p <= 0.6666666:
                    key = 0.5
                elif 0.6666666 < p <= 1:
                    key = 1

                current_cell_display = CellState.to_probability_display_string[key]

                if x == len(self.leak_probability_grid[1]) - 1:
                    current_cell_display += "|"

                print(current_cell_display, end="")

            print()