class CellState:
    CLOSED = 0
    OPENED = 1
    LEAK = 2
    BOT = 3
    BUTTON = 4
    PATH = 5
    WALKED_PATH = 6
    OLD_PATH = 7
    DETECTION_SQUARE = 8

    P_NO_LEAK = 0
    P_MIGHT_CONTAIN_PEAK = 1

    # to_display_string = ['■', ' ', '🔥', '🤖', '✅']
    # to_display_string = ['■', ' ', 'F', 'B', 'X']
    to_display_string = ['⬛', '  ', '💧', '🤖', '🔴', '🟩', '🟦', '🟥', '🟨']
    to_probability_display_string = {
        -1: '⬛', # wall
        0: '🟥',  # 0% possiblity of containing leak
        0.5: '🟨', 
        1: '🟩',
        999: '🟦'
    }