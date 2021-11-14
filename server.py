"""Executable for hosting matches."""

import game
import sys
from globalvars import *

def main():
    # accept command-line args, including where to listen
    if len(sys.argv) != 1:
        sys.exit("Usage: server.py")

    # set up GameServer object
    game_server = game.GameServer()

    # listen on a port for users who want to start a match
    game_server.listen()

    while True:
        # wait for enough users to start a match
        game_server.wait_for_match()

        # when enough users connect, start a match
        game_server.start_match()
    
        # while the match is not over:
        while True:
            print(game_server.engine.current_tick)
            # get inputs from each user
            game_server.check_inputs()
            # relay inputs to each other user
            game_server.relay_inputs()
            # update the game state according to the inputs
            game_server.update_state()
            # check if the match is over
            if not 1: # Replace with condition
                game_server.end_match()

if __name__ == "__main__":
    main()