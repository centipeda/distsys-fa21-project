"""Global variables and configuration settings."""

# set to true to enable debug print statements
DEBUG_ENABLED = True

import logging
# set up debug logging
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s %(asctime)s] %(message)s')
LOGGER = logging.getLogger()
if DEBUG_ENABLED:
    LOGGER.setLevel(logging.DEBUG)

PACKET_READ_SIZE = 4096 # bytes
PACKET_HEADER    = b'\x57\x67' # packet header
PACKET_TERM      = b'\xF1\x54'  # packet terminator

FRAMERATE = 60 # frames per second

SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 800

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0,0,0)
COLOR_RED   = (255, 0, 0)
COLOR_BLUE   = (0, 0, 255)
COLOR_GRAY  = (153, 153, 153)

GAME_TITLE = "Lag Warriors"

SERVER_HOST = "localhost"
SERVER_PORT = 5555

# Game config settings.

# How many ticks in advance inputs are scheduled for.
GLOBAL_INPUT_DELAY = 10
# How often the engine should record the current state for rollback.
STATE_SAVE_RATE = 100 # ticks apart


ARENA_SIZE  = 1000 # pixels
# Minimum players to start a match.
MIN_PLAYERS = 2
# Maximum players in a match.
MAX_PLAYERS = 2

# How far from the edge of the arena players start at.
PLAYER_START_OFFSET = 30
PLAYER_SPEED = 5 # px/tick
PLAYER_SIZE = 20 # px
PROJECTILE_SPEED = 10 # px/tick
PROJECTILE_SIZE  = 10 # px
GUIDELINE_LENGTH = 40
GUIDELINE_WIDTH  = 5

KNOCKBACK_TIME = 10 # ticks
KNOCKBACK_SPEED = 5 # px/tick