from ship import *
from task_status import TaskStatus

import time

class Simulation:

    def __init__(self, ship_size, detection_radius, alpha, bot_number, ship_layout_file = None, render_debug_logs = False):
        self.running = True
        self.FPS = 100000
        self.render_debug_logs = render_debug_logs
        self.time_elapsed = 0

        self.ship = Ship(ship_size, detection_radius, alpha, bot_number, ship_layout_file) # init ship

    def start(self): # Starts Game Loop
        self.ship.start()

        if self.render_debug_logs:
            self.ship.render()

        while self.running :
            start_time = time.time()

            status, result = self.update()

            if status != TaskStatus.ONGOING:
                self.stop(result)
                return result
            
            # if self.time_elapsed > 600:  # 10s timeout incase something happens
                # self.stop(result)
                # return TaskStatus.FAIL

            self.render()

            end_time = time.time()
            delta_time = end_time - start_time
            self.time_elapsed += delta_time
            delay = 1.0 / self.FPS - delta_time
            time.sleep(max(0, delay))

            # input()

    def stop(self, simulation_result):
        self.running = False

    def update(self): # this update and render are ran once per frame
        return self.ship.update()

    def render(self):
        if not self.render_debug_logs:
            return

        self.ship.render()