from abc import ABC, abstractmethod

from cell_state import CellState
from task_status import TaskStatus

# Abstract class for Bots to create the structure of all bots
class Bot(ABC):
    def __init__(self, ship, initial_location, detection_radius):
        """Initializes basic variables for all bots"""
        self.ship = ship
        self.location = initial_location
        self.detection_radius = detection_radius

        # self.path = self.find_shortest_path(initial_location, self.ship.button_location)
    
    @abstractmethod
    def start(self):
        pass
        """Initialization method for each bot, ran before the main game loop begins"""
    
    @abstractmethod
    def update(self):
        pass
        """Update values, ran once per frame during game loop"""


    @abstractmethod
    def find_shortest_path(self, start, destination):
        """Each bot must have it's custom pathfinding algorithm"""
        pass
    

    def move(self, destination):
        """Utility method for moving a bot"""
        self.ship.ship_grid[self.location] = CellState.WALKED_PATH

        self.location = destination
        self.ship.ship_grid[destination] = CellState.BOT