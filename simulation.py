from ship import *
from bot import *
from fire import *

import time

class Simulation:

    def __init__(self, ship_size, ship_flammability):
        self.running = True
        self.FPS = 1

        self.ship = Ship(ship_size, ship_flammability) # init ship

        self.start()

    def start(self): # Starts Game Loop
        while self.running:
            start_time = time.time()

            self.running = self.update() # if update returns a fail status, this will be false
            self.render()

            end_time = time.time()
            delta_time = end_time - start_time
            delay = 1.0 / self.FPS - delta_time
            time.sleep(delay)

    def update(self): # this update and render are ran once per frame
        self.ship.update()

    def render(self):
        self.ship.render()