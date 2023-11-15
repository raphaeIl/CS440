from simulation import Simulation, TaskStatus

def run_simulation(amount, ship_size, detection_radius, alpha, bot_number, saved_ship_layout_file = None, render_debug_logs = False):
    success_simulations = 0

    for i in range(amount):
        sim = Simulation(ship_size, detection_radius, alpha, bot_number, saved_ship_layout_file, render_debug_logs)

        result = sim.start()
        print(f"""Simulation {i} - Total actions: {result}""")

        success_simulations += result
    
    return success_simulations / amount

k_hyperparameters = [1, 2, 3, 4, 5]
a_hyperparameters = [0.001, 0.002, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009, 0.01]

for k in k_hyperparameters:
    result = run_simulation(
        amount=100, # number of simulations to run
        ship_size=30, # (D value)
        detection_radius=k, # (k value)
        alpha=0.001, # (a value)
        bot_number=3, # Bot1, Bot2, Bot3 or Bot4?
        saved_ship_layout_file=None, # Use pre-generated ship layouts? (there is a 100 50x50 layouts in the saved_ship_layouts folder). Example: saved_ship_layout_file="layout_69"
        render_debug_logs=True, # displays a cute emoji representation of the simulation in the console ^v^
        # (best viewed in the visual studio code terminal, other terminals might mess up the formatting)
    )
    
    print("Performance (Average Actions): ", result, " per run")
