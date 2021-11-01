"""Global variables and configuration settings."""

FRAMERATE = 60 # frames per second

SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 800

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0,0,0)
COLOR_RED   = (255, 0, 0)
COLOR_BLUE   = (0, 0, 255)

GAME_TITLE = "Lag Warriors"

SERVER_HOST = "localhost"
SERVER_PORT = 5555

# Game config settings.

ARENA_SIZE  = 600 # pixels
# Minimum players to start a match.
MIN_PLAYERS = 2
# Maximum players in a match.
MAX_PLAYERS = 2

PLAYER_SPEED = 5 # px/tick
PLAYER_SIZE = 20 # px
PROJECTILE_SPEED = 10 # px/tick
PROJECTILE_SIZE  = 10 # px
GUIDELINE_LENGTH = 40
GUIDELINE_WIDTH  = 10