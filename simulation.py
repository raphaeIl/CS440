from ship import *
from fire import *
from task_status import TaskStatus

import time

class Simulation:

    def __init__(self, ship_size, ship_flammability, ship_layout_file = None):
        self.running = True
        self.FPS = 5

        self.ship = Ship(ship_size, ship_flammability, ship_layout_file) # init ship

        self.start()

    def start(self): # Starts Game Loop
        while self.running:
            start_time = time.time()

            result = self.update() # if update returns a fail status, this will be false

            if result != TaskStatus.ONGOING:
                self.stop(result)
            
            self.render()

            end_time = time.time()
            delta_time = end_time - start_time
            delay = 1.0 / self.FPS - delta_time
            time.sleep(max(0, delay))

    def stop(self, simulation_result):
        self.running = False

        print("Success!" if simulation_result == TaskStatus.SUCCESS else "Fail")

    def update(self): # this update and render are ran once per frame
        return self.ship.update()
        pass

    def render(self):
        self.ship.render()
        pass


# check if no path in the beginning, fire on button, dist from fire to button is longer than dist from robot to button == win