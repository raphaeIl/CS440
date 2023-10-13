from simulation import Simulation, TaskStatus

# run layout files
def run_simulation(amount, ship_size, ship_flammability, bot_number, saved_ship_layout_file = None, render_debug_logs = False):
    success_simulations = 0

    for i in range(amount):
        sim = Simulation(ship_size, ship_flammability, bot_number, saved_ship_layout_file, render_debug_logs)

        result = sim.start()

        if result == TaskStatus.SUCCESS:
            success_simulations += 1
        else: # if fail, we wanna see what went wrong
            sim.render()

    return success_simulations / amount

# cases for instant fail
# path is None, no path to button
# bot is closer to the button than the fire

result = run_simulation(
    amount=10_000, # number of simulations to run
    ship_size=20, # (D value)
    ship_flammability=0.5, # (q value)
    bot_number=4, # Bot1, Bot2, Bot3 or Bot4?
    saved_ship_layout_file=None, # Use pre-generated ship layouts? (there is a 100 50x50 layouts in the saved_ship_layouts folder)
    render_debug_logs=False, # displays a cute emoji representation of the simulation in the console ^v^
    # (best viewed in the visual studio code terminal, other terminals might mess up the formatting)
)

print("Performance: ", result * 100, "% sucess rate")
# performance:
# values between q 0 and 1
# 
# 

