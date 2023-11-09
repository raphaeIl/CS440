from cell_state import CellState
from task_status import TaskStatus

from collections import deque   

from bot import Bot

class Bot2(Bot):

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

    def find_shortest_path(self, start, destination):
        super().find_shortest_path(start, destination)
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