from cell_state import CellState
from task_status import TaskStatus
# from ship import Ship

import numpy as np

class Bot:

    def __init__(self, ship, initial_location):
        self.ship = ship
        self.location = initial_location

        # breath first
        # avoids initial cell, might want to add modes in simulation constructor
        self.ship.opened_cells.remove(self.ship.initial_fire_location)
        print(initial_location, self.ship.button_location)

        path = self.find_shortest_path(initial_location, self.ship.button_location)

        print(path)

    def find_shortest_path(self, locationA, locationB):
        queue = []
        # visited = set([])

        queue.append((locationA, []))
        # visited.add(locationB)

        while len(queue) > 0 and len(queue) < 50_000: # more than 50k items in queue means no path (infinite loop?)

            current, path = queue.pop(0)

            if current == self.ship.button_location:
                return path + [current]

            for neighbor in self.ship.get_opened_neighbors(current):
                # if neighbor not in visited:
                    # visited.add(current)
                    new_path = path + [current]
                    queue.append((neighbor, new_path))

        # find path
        return None

    def update(self):   
        # if moved to fire, fail if moved to button sucess
        if (self.location == self.ship.button_location):
            return TaskStatus.SUCCESS

        return TaskStatus.ONGOING

    def move(self, y, x):
        self.ship.ship_grid[self.location] = CellState.OPENED
        
        self.location = (y, x)
        self.ship.ship_grid[self.location] = CellState.BOT
    