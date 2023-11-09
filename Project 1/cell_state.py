class CellState:
    CLOSED = 0
    OPENED = 1
    FIRE = 2
    BOT = 3
    BUTTON = 4
    PATH = 5
    WALKED_PATH = 6
    OLD_PATH = 7

    # to_display_string = ['■', ' ', '🔥', '🤖', '✅']
    # to_display_string = ['■', ' ', 'F', 'B', 'X']
    to_display_string = ['⬛', '  ', '🔥', '🤖', '🔴', '🟩', '🟦', '🟥']