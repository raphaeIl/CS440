from cell_state import CellState
from task_status import TaskStatus

from collections import deque   

class Bot2:
    def __init__(self, ship, initial_location):
        self.ship = ship
        self.location = initial_location

        self.ship.opened_cells.remove(self.ship.initial_fire_location)

        # print(initial_location, self.ship.button_location)

        self.path = self.find_shortest_path(initial_location, self.ship.button_location) # check here first path invalod
        # move to render for other bots
        for i in range(1, len(self.path) - 1): # solely used for displaying to console for fun, no actual functional uses
            self.ship.ship_grid[self.path[i]] = CellState.PATH

        # print(self.path)

    def find_shortest_path(self, start, destination):
        queue = deque([(start, [])])
        visited = set()

        while len(queue) > 0:
            current, path = queue.popleft()

            visited.add(current)

            if current == destination:
                return path + [current]

            for neighbor in self.ship.get_opened_neighbors(current):
                if neighbor in visited or neighbor in self.ship.fire.fire_cells:
                    continue

                queue.append((neighbor, path + [current]))

        return None

    def update(self):   
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

    def move(self, destination):
        self.ship.ship_grid[self.location] = CellState.WALKED_PATH

        self.location = destination
        self.ship.ship_grid[destination] = CellState.BOT
        # print(self.ship.ship_grid[destination])