from cell_state import CellState
from task_status import TaskStatus

from collections import deque   
import heapq

from bot import Bot

class Bot4(Bot):

    def start(self):
        return super().start()

    def update(self):   
        super().update()

        # if moved to fire, fail if moved to button sucess
        for cell in self.path:
            if (self.ship.ship_grid[cell] == CellState.FIRE): # only reroute if needded (fire blocks original path)
                for original_path in self.path:
                    if self.ship.ship_grid[original_path] == CellState.PATH:
                       self.ship.ship_grid[original_path] = CellState.OLD_PATH

                self.path = self.find_shortest_path(self.location, self.ship.button_location)

        if (self.path == None):
            return TaskStatus.FAIL

        next_cell = self.path[self.path.index(self.location) + 1]

        for i in range(self.path.index(self.location), len(self.path) - 1): # solely used for displaying to console for fun, no actual functional uses
            self.ship.ship_grid[self.path[i]] = CellState.PATH

        self.move(next_cell)

        if (next_cell == self.ship.button_location):
            return TaskStatus.SUCCESS
        elif (next_cell in self.ship.fire.fire_cells):
            return TaskStatus.FAIL
        
        return TaskStatus.ONGOING
    
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
                if neighbor in visited or neighbor in self.ship.fire.fire_cells or neighbor in self.ship.fire.get_adjacent_fire_cells():
                    continue

                g = len(path) + 1  # distance from start to current node
                h = self.heuristic(neighbor, destination)  # h cost
                f = g + h

                heapq.heappush(heapQueue, (f, neighbor, path + [current]))


        # if no path can be found, try again without taking into account of the adjcent fire cells
        while heapQueue:
            # Get the node in open_list having the lowest f (g + h) value.
            _, current, path = heapq.heappop(heapQueue)

            if current in visited:
                continue

            visited.add(current)

            if current == destination:
                return path + [current]

            for neighbor in self.ship.get_opened_neighbors(current):
                if neighbor in visited or neighbor in self.ship.fire.fire_cells:
                    continue

                g = len(path) + 1  # distance from start to current node
                h = self.heuristic(neighbor, destination)  # h cost
                f = g + h

                heapq.heappush(heapQueue, (f, neighbor, path + [current]))

        return None

    def heuristic(self, a, b): # Manhattan Distance
        return abs(a[0] - b[0]) + abs(a[1] - b[1])