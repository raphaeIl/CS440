from ship import Ship, CellState

class Bot:

    def __init__(self, ship: Ship, initial_location):
        self.ship = ship
        self.location = initial_location

    def update(self):
        pass

    def move(self, y, x):
        self.ship.ship_grid[self.location] = CellState.OPENED
        
        self.location = (y, x)
        self.ship.ship_grid[self.location] = CellState.BOT
    