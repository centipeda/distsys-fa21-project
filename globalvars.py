"""Global variables and configuration settings."""

# set to true to enable debug print statements
DEBUG_ENABLED = True

# set to true to skip the startup animation on the client
SKIP_INTRO = True

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
COLOR_GREEN = (0, 255, 0)
COLOR_YELLOW = (255, 255, 0)
COLOR_GRAY  = (153, 153, 153)

GAME_TITLE = "Lag Fighters"

SERVER_HOST = "localhost"
SERVER_PORT = 5555

# Game config settings.

# How many ticks in advance inputs are scheduled for.
GLOBAL_INPUT_DELAY = 5
# How often the engine should record the current state for rollback.
STATE_SAVE_RATE = 100 # ticks apart
# How often to send re-synchronization packets to each client.
RESYNC_RATE = 300 # ticks apart
# How much lag to simulate on the client-side.
EXTRA_CLIENT_LATENCY = 0 # ticks


ARENA_SIZE  = 1000 # pixels
# Minimum players to start a match.
MIN_PLAYERS = 2
# Maximum players in a match.
MAX_PLAYERS = 4
# How many seconds the match should go on for.
MATCH_LENGTH = 15 # seconds
# How long of a countdown players should get before starting the match.
MATCH_START_DELAY = 3 # seconds

# How far from the edge of the arena players start at.
PLAYER_START_OFFSET = 30
PLAYER_SPEED = 5 # px/tick
PLAYER_SIZE = 20 # px
PROJECTILE_SPEED = 10 # px/tick
PROJECTILE_SIZE  = 10 # px
PICKUP_SIZE = 15
POINTS_PER_PICKUP = 15
# How many ticks between pickup spawns.
PICKUP_SPAWN_RATE = 30
# How many positions to pre-generate.
PICKUP_POSITIONS_GENERATED = 4096
MAX_PICKUPS = 5
GUIDELINE_LENGTH = 40
GUIDELINE_WIDTH  = 5

KNOCKBACK_TIME = 15 # ticks
KNOCKBACK_SPEED = 50 # px/tick
