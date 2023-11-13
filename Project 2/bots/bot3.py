from cell_state import CellState
from task_status import TaskStatus

from collections import deque
import numpy as np
import random
import math
import heapq
from bot import Bot
class Bot3(Bot):

    def start(self):
        start_status = super().start()
        self.current_path = deque()

        # all cells might have leak
        self.leak_probability_grid = np.zeros((self.ship.ship_size, self.ship.ship_size), np.float16)

        # walls can not have leaks
        for y in range(0, self.ship.ship_size):
            for x in range(0, self.ship.ship_size):
                if (y, x) in self.ship.opened_cells:
                    self.leak_probability_grid[y, x] = 1 / len(self.ship.opened_cells)
                    print(1 / len(self.ship.opened_cells))
        
        # self.sense()
        print(self.leak_probability_grid)
        
        # input()

    def sense(self): # sense and update knownledge
        # beep or not
        alpha = 0.5
        d = len(self.find_shortest_path(self.location, self.ship.leak_location)) # only using the leak location to find out if beep or not, 
        probability_equation = math.pow(math.e, -alpha * (d - 1))

        # P(beep in i)
        beep_in_i = 0
        for y in range(self.ship.ship_size):
            for x in range(self.ship.ship_size):
                if (y, x) in self.ship.opened_cells:
                    prob = self.leak_probability_grid[y, x] * math.pow(math.e, -alpha * (len(self.find_shortest_path(self.location, (y, x))) - 1))
                    beep_in_i += prob
                    print(prob)

        # Find P( leak in cell j | heard a beep in cell i )
        # = P(leak in j) (original prob in leak_probability_grid) * probability_equation / P(beep in i)

        # P(beep in i)
        for y in range(self.ship.ship_size):
            for x in range(self.ship.ship_size):
                if (y, x) != self.location and (y, x) in self.ship.opened_cells:
                    shortest_distance = len(self.find_shortest_path(self.location, (y, x)))
                    if random.random() <= probability_equation: # beep
                        self.leak_probability_grid[y, x] *= math.pow(math.e, -alpha * (shortest_distance - 1)) / beep_in_i
                    else: # no beep
                        self.leak_probability_grid[y, x] *= (1 - math.pow(math.e, -alpha * (shortest_distance - 1))) / (1 - beep_in_i)

 
    def update(self):
        super().update()

        # find all cells with highest probability
        # get distance of all, find shortest

        # if destination is different from preivous, change path

        # start moving towards it
        # if no leak at current cell, sense

        # sensed_leak = self.sense()
        # print(sensed_leak)
        
        nearest_cell = self.find_nearest_cell()

        # 0 means reached destination
        if len(self.current_path) == 0:
            path = self.find_shortest_path(self.location, nearest_cell)
            self.current_path.extend(path)

        self.render_probability_grid()
        
        last_destination = self.current_path[len(self.current_path) - 1]
        # if new destination for nearest cell found, 
        if nearest_cell != last_destination and \
            self.manhattan_distance(self.location, nearest_cell) < self.manhattan_distance(self.location, last_destination):
            self.current_path = deque()
            return TaskStatus.ONGOING

        # move to next location in path, if leak sucess if not set prob 0
        next_cell  = self.current_path.popleft()

        if (self.ship.ship_grid[next_cell] == CellState.LEAK):
            print("Total actions: ", self.total_actions)
            return TaskStatus.SUCCESS
        
        # update P(current) and P(all others) same?
        # print("sum of all probability before:", self.leak_probability_grid.sum())

        # for y in range(self.ship.ship_size):
        #     for x in range(self.ship.ship_size):
        #         if (y, x) != next_cell:
        #             self.leak_probability_grid[y, x] = self.leak_probability_grid[y, x] / (self.leak_probability_grid[next_cell])
        self.leak_probability_grid[next_cell] = 0

        # total_probability = np.sum(self.leak_probability_grid)
        
        # if total_probability > 0:
            # self.leak_probability_grid /= total_probability

        # print("sum of all probability after:", self.leak_probability_grid.sum())
        self.move(next_cell)
        self.sense()

        # print(self.leak_probability_grid)

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

    
    def manhattan_distance(self, a, b): # Manhattan Distance
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def find_shortest_path(self, start, destination): # A*
        super().find_shortest_path(start, destination)
        heapQueue = [(0, start, [])]  # Priority queue: (f, current_position, path)
        visited = set()

        while heapQueue:
            # Get the node in open_list having the lowest f (g + h) value.
            _, current, path = heapq.heappop(heapQueue)

            if current in visited:
                continue

            visited.add(current)
            if current == destination:
                return path + [current]

            for neighbor in self.ship.get_opened_neighbors(current):
                if neighbor in visited:
                    continue

                g = len(path) + 1  # distance from start to current node
                h = self.heuristic(neighbor, destination)  # h cost
                f = g + h

                heapq.heappush(heapQueue, (f, neighbor, path + [current]))

        return None

    def heuristic(self, a, b): # Manhattan Distance
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def find_shordest_path(self, start, destination):
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
