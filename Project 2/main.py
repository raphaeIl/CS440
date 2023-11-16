from simulation import Simulation, TaskStatus

def run_simulation(amount, ship_size, detection_radius, alpha, bot_number, saved_ship_layout_file = None, render_debug_logs = False):
    success_simulations = 0

    for i in range(amount):
        # sim = Simulation(ship_size, detection_radius, alpha, bot_number, f"layout_{i+1}", render_debug_logs)
        sim = Simulation(ship_size, detection_radius, alpha, bot_number, saved_ship_layout_file, render_debug_logs)

        result = sim.start()
        print(f"""Simulation {i + 1} - Total actions: {result}""")

        success_simulations += result
    
    return success_simulations / amount

# k_hyperparameters = [1, 2, 3, 4, 5]
# a_hyperparameters = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]

# for k in k_hyperparameters:
# for a in a_hyperparameters:

result = run_simulation(
    amount=10, # number of simulations to run
    ship_size=20, # (D value)
    detection_radius=5, # (k value)
    alpha=0.2, # (a value)
    bot_number=1, # Bot #
    saved_ship_layout_file=None, # Use pre-generated ship layouts? (there is a 100 50x50 layouts in the saved_ship_layouts folder). Example: saved_ship_layout_file="layout_69"
    render_debug_logs=False, # displays a cute emoji representation of the simulation in the console ^v^
    # (best viewed in the visual studio code terminal, other terminals might mess up the formatting)
)

print(f"Average Action (k={5}, a={0.2}, runs={10}): ", result, " per run")
