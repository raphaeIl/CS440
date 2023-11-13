from abc import ABC, abstractmethod

from cell_state import CellState
from task_status import TaskStatus

import heapq

# Abstract class for Bots to create the structure of all bots
class Bot(ABC):
    def __init__(self, ship, initial_location, detection_radius):
        """Initializes basic variables for all bots"""
        self.ship = ship
        self.location = initial_location
        self.detection_radius = detection_radius
        self.total_actions = 0

        # self.path = self.find_shortest_path(initial_location, self.ship.button_location)
    
    @abstractmethod
    def start(self):
        pass
        """Initialization method for each bot, ran before the main game loop begins"""
    
    @abstractmethod
    def update(self):
        pass
        """Update values, ran once per frame during game loop"""

    def move(self, destination):
        """Utility method for moving a bot"""
        self.total_actions += 1

        self.ship.ship_grid[self.location] = CellState.WALKED_PATH

        self.location = destination
        self.ship.ship_grid[destination] = CellState.BOT

    def sense(self):
        """Sense and update knowledge, Default Implementation"""
        self.total_actions += 1

        has_sensed_leak = self.ship.is_leak_in_area(self.location, self.detection_radius)
        
        return has_sensed_leak
    
    def find_shortest_path(self, start, destination): # A*
        """
            Using A* for all bots to make it fair, since we focusing on optimizing probability algorithms rather than searching ones
            Returns the path in a list, Use len(path) if you only need the shortest distance
        """
        
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
                if neighbor in visited:
                    continue

                g = len(path) + 1  # distance from start to current node
                h = self.heuristic(neighbor, destination)  # h cost
                f = g + h

                heapq.heappush(heapQueue, (f, neighbor, path + [current]))

        return None
    
    def heuristic(self, a, b): # Manhattan Distance Heuristic
        return abs(a[0] - b[0]) + abs(a[1] - b[1])