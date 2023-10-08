class CellState:
    CLOSED = 0
    OPENED = 1
    FIRE = 2
    BOT = 3
    BUTTON = 4
    PATH = 5
    WALKED_PATH = 6

    # to_display_string = ['■', ' ', '🔥', '🤖', '✅']
    # to_display_string = ['■', ' ', 'F', 'B', 'X']
    to_display_string = ['⬛', '  ', '🔥', '🤖', '🔴', '🟩', '🟦']