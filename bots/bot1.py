from cell_state import CellState
from task_status import TaskStatus
    
from collections import deque

class Bot1:
    def __init__(self, ship, initial_location):
        self.ship = ship
        self.location = initial_location

        self.ship.opened_cells.remove(self.ship.initial_fire_location)
        self.current_cell = 0

        print(initial_location, self.ship.button_location)

        self.path = self.find_shortest_path(initial_location, self.ship.button_location)
        
        # move to render for other bots
        for i in range(1, len(self.path) - 1): # solely used for displaying to console for fun, no actual functional uses
            self.ship.ship_grid[self.path[i]] = CellState.PATH

        print(self.path)

    def find_shortest_path(self, start, destination):
        queue = deque([(start, [])])
        visited = set()

        while len(queue) > 0:
            current, path = queue.popleft()

            visited.add(current)

            if current == destination:
                return path + [current]

            for neighbor in self.ship.get_opened_neighbors(current):
                if neighbor in visited: # this instead of using a set to track visited nodes
                    continue

                queue.append((neighbor, path + [current]))

        return None

    def update(self):   
        if self.path == None:
            return TaskStatus.FAIL

        # if moved to fire, fail if moved to button sucess
        self.current_cell += 1
        next_cell = self.path[self.current_cell]

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
        print(self.ship.ship_grid[destination])
    