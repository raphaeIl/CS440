from cell_state import CellState
from task_status import TaskStatus

from collections import deque

from bot import Bot

class Bot1(Bot):

    def start(self):
        start_status = super().start()
        
        if start_status == TaskStatus.FAIL:
            return TaskStatus.FAIL

        self.current_cell = 0

        for i in range(1, len(self.path) - 1): # solely used for displaying to console for fun, no actual functional uses
            self.ship.ship_grid[self.path[i]] = CellState.PATH
    
    def update(self):
        super().update()
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
                if neighbor in visited:
                    continue

                queue.append((neighbor, path + [current]))

        return None

