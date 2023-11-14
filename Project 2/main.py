from simulation import Simulation, TaskStatus

def run_simulation(amount, ship_size, detection_radius, bot_number, saved_ship_layout_file = None, render_debug_logs = False):
    success_simulations = 0

    for i in range(amount):
        sim = Simulation(ship_size, detection_radius, bot_number, saved_ship_layout_file, render_debug_logs)

        result = sim.start()
        print(f"""Simulation {i} - Total actions: {result}""")

        success_simulations += result
    
    return success_simulations / amount


result = run_simulation(
    amount=100, # number of simulations to run
    ship_size=20, # (D value)
    detection_radius=3, # (k value)
    bot_number=2, # Bot1, Bot2, Bot3 or Bot4?
    saved_ship_layout_file=None, # Use pre-generated ship layouts? (there is a 100 50x50 layouts in the saved_ship_layouts folder). Example: saved_ship_layout_file="layout_69"
    render_debug_logs=False, # displays a cute emoji representation of the simulation in the console ^v^
    # (best viewed in the visual studio code terminal, other terminals might mess up the formatting)
)

print("Performance (Average Actions): ", result, " per run")
