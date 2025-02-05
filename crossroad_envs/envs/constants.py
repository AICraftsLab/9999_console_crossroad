CELL_SIZE = 25
CELL_BORDER_WIDTH = 1
CELL_INNER_BORDER_WIDTH = 4
CELL_BORDER_COLOR = 'darkgray'
CELL_INNER_BORDER_COLOR = 'gray'
CELL_INNER_COLOR = 'darkgray'

CHARACTER_BORDER_COLOR = 'black'
CHARACTER_INNER_BORDER_COLOR = CELL_INNER_BORDER_COLOR
CHARACTER_INNER_COLOR = 'black'

CELL_MIDDLE_SIZE = CELL_SIZE - (CELL_BORDER_WIDTH*2)
CELL_INNER_SIZE = CELL_MIDDLE_SIZE - (CELL_INNER_BORDER_WIDTH*2)

BG_RECT_INFLATION = 2

TEXTS_COLOR = 'black'
PLAYER_COLOR = 'blue'
PLAYER_LIVES = 4
PLAYER_FOV = 2 # Can see two rows up, 2 rows down, and of course its row

# Train presets, currently not inuse
TRAINS = [
    (0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    (0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0),
    (0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1),
    (1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0),
    (1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0),
    (1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1),
    (1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0),
    (0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1),
    (0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0),
    (1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1),
]