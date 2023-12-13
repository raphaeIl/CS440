import numpy as np
import random


def generate_diagram():
    D = 20
    diagram = np.zeros((D, D), dtype=np.int8) # 20 x 20 diagram

    color_order = random.sample(range(1, 4 + 1), 4) # pre-picking order of colors for the 4 wires 
    row_order = random.sample(range(20), 2) # pre-picking the order of rows to set to that color
    col_order = random.sample(range(20), 2) # pre-picking the order of columns

    if random.random() <= 0.5: # 50% chance starting with rows/columns 
        diagram[row_order[0],:] = color_order[0]
        diagram[:,col_order[0]] = color_order[1]
        diagram[row_order[1],:] = color_order[2]
        diagram[:,col_order[1]] = color_order[3]
    else:
        diagram[:,col_order[0]] = color_order[1]
        diagram[row_order[0],:] = color_order[0]
        diagram[:,col_order[1]] = color_order[3]
        diagram[row_order[1],:] = color_order[2]

    # display(diagram)

    dangerous = color_order.index(1) < color_order.index(3) # red before yellow means dangerous
    cut = color_order[2] # 3rd wire "always to be cut"

    return diagram, int(dangerous)

def to_emoji(color):
    colors = { 'red', 'blue', 'yellow', 'green' }
    color_emojis = [ '⬛', '🟥', '🟦', '🟨', '🟩' ]

    return color_emojis[color]

def display(diagram):
    for y in range(len(diagram)):
        for x in range(len(diagram[0])):
            print(to_emoji(diagram[y, x]), end='')
        print("")


X, y = generate_diagram()

print(X, y)