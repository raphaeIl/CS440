import random

from cell_state import CellState
from task_status import TaskStatus

class Fire:
    
    def __init__(self, ship, initial_location, flammability):
        self.ship = ship
        self.initial_location = initial_location
        self.flammability = flammability

        self.fire_cells = set([initial_location])

    def update(self):
        if len(self.ship.opened_cells) <= 0:
            return TaskStatus.FAIL
        
        opened_neighbors_of_fire_cells = set([])
        
        for fire_cell in self.fire_cells:
            for neighbor in self.ship.get_opened_neighbors(fire_cell):
                if neighbor not in self.fire_cells:
                    opened_neighbors_of_fire_cells.add(neighbor)

        # get_opened_neighbors of init fire cell, pick a random one, start_fire
        # print("Cells that fire can spread to: ", opened_neighbors_of_fire_cells)
        fire_cell = random.choice(list(opened_neighbors_of_fire_cells))

        # get_opened_neighbors of the list of fire cells, repeat step 2
        if random.random() > (1 - pow((1 - self.flammability), len(self.get_burning_neighbors(fire_cell)))):
            print("Fire failed to spread")
        else:
            if fire_cell == self.ship.button_location or fire_cell == self.ship.bot_location:
                return TaskStatus.FAIL

            self.set_cell_fire(fire_cell)

        return TaskStatus.ONGOING

    def set_cell_fire(self, cell):
        print("Setting cell on fire: ", cell)
        self.ship.ship_grid[cell] = CellState.FIRE

        self.fire_cells.add(cell)
        self.ship.opened_cells.remove(cell)
        
    def get_burning_neighbors(self, cell):
        burning_neighbors = set([])

        for neighbor in self.ship.get_neighbors(cell):
            if self.ship.ship_grid[neighbor] == CellState.FIRE:
                burning_neighbors.add(neighbor)

        return burning_neighbors