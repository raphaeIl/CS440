from ship import Ship, CellState
import random
class Fire:
    
    def __init__(self, ship: Ship, initial_location):
        self.ship = ship
        self.location = initial_location
    
    def update(self):
        pass

    def start_fire(self):
        # pick a random open cell from opened_cells
        print(set(self.opened_cells))
        start_fire_from_cell = random.choice(list(self.opened_cells))

        # get_opened_neighbors of init fire cell, pick a random one, start_fire
        fire_cell = random.choice(list(self.get_opened_neighbors(start_fire_from_cell)))
        self.set_cell_fire(fire_cell)
        self.display()

        while len(self.opened_cells) > 0:
            opened_neighbors_of_fire_cells = set([])

            for fire_cell in self.fire_cells:
                for neighbor in self.get_opened_neighbors(fire_cell):
                    opened_neighbors_of_fire_cells.add(neighbor)

            print("Cells that fire can spread to: ", opened_neighbors_of_fire_cells)
            fire_cell = random.choice(list(opened_neighbors_of_fire_cells))

            # get_opened_neighbors of the list of fire cells, repeat step 2
            if random.random() > (1 - pow((1 - self.flammability), len(self.get_burning_neighbors(fire_cell)))):
                print("Fire failed to spread")
            else:
                self.set_cell_fire(fire_cell)
            
            self.display()    
            time.sleep(1)

    def spread(self, y, x):
        self.ship.ship_grid[self.location] = CellState.OPENED
        
        self.location = (y, x)
        self.ship.ship_grid[self.location] = CellState.BOT

    def set_cell_fire(self, cell):
        print("Setting cell on fire: ", cell)
        self.ship_grid[cell] = self.FIRE
        print(self.ship_grid[cell])
        self.fire_cells.add(cell)
        self.opened_cells.remove(cell)
        
    def get_burning_neighbors(self, cell):
        burning_neighbors = set([])

        for neighbor in self.get_neighbors(cell):
            if self.ship_grid[neighbor] == self.FIRE:
                burning_neighbors.add(neighbor)

        return burning_neighbors