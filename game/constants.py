from enum import Enum

BOARD_SIZE = 9
NUM_WALLS = 10

class PlayerId(Enum):
    PLAYER_1 = 1 # Starts at top (y=0) or bottom (y=8)? Let's say Player 1 is bottom, aiming for top.
    PLAYER_2 = 2 # Starts at top, aiming for bottom.

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class WallOrientation(Enum):
    HORIZONTAL = 'H'
    VERTICAL = 'V'

# UI Constants
WIDTH = 1000
HEIGHT = 800
CELL_SIZE = 60
WALL_THICKNESS = 15
MARGIN = 50

# Colors - Premium Palette
COLOR_BG = (30, 30, 35)      # Dark slate background
COLOR_BOARD = (60, 45, 35)   # Rich dark wood
COLOR_GRID = (45, 35, 30)    # Subtle cell separators
COLOR_P1 = (220, 60, 60)     # Vibrant Red
COLOR_P2 = (60, 120, 240)    # Vibrant Blue
COLOR_WALL = (160, 110, 60)  # Golden oak wood for walls
COLOR_WALL_HOVER_VALID = (100, 255, 100, 160)
COLOR_WALL_HOVER_INVALID = (255, 100, 100, 160)
COLOR_MOVE_HOVER = (255, 255, 255, 60)
COLOR_TEXT = (240, 240, 240) # Off-white text
COLOR_BTN = (50, 50, 60)     # Button base color
COLOR_BTN_HOVER = (70, 70, 90)
COLOR_BTN_ACCENT = (100, 180, 255) # For selected state

FPS = 60
