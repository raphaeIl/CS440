from ship import *
from task_status import TaskStatus

import time

class Simulation:

    def __init__(self, ship_size, detection_radius, bot_number, ship_layout_file = None, render_debug_logs = False):
        self.running = True
        self.FPS = 100
        self.render_debug_logs = render_debug_logs

        self.ship = Ship(ship_size, detection_radius, bot_number, ship_layout_file) # init ship

    def start(self): # Starts Game Loop
        if self.ship.start() == TaskStatus.FAIL:
            return TaskStatus.FAIL

        while self.running:
            start_time = time.time()

            result = self.update() # if update returns a fail status, this will be false

            if result != TaskStatus.ONGOING:
                self.stop(result)
                return result
            print("result", result)

            self.render()

            end_time = time.time()
            delta_time = end_time - start_time
            delay = 1.0 / self.FPS - delta_time
            time.sleep(max(0, delay))

            # input()

    def stop(self, simulation_result):
        self.running = False

        if self.render_debug_logs:
            print("Success!" if simulation_result == TaskStatus.SUCCESS else "Fail")

    def update(self): # this update and render are ran once per frame
        return self.ship.update()

    def render(self):
        if not self.render_debug_logs:
            return

        self.ship.render()