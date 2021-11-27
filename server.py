"""Executable for hosting matches."""

import time
import game
import sys
from globalvars import *

def main():
    # accept command-line args, including where to listen
    if len(sys.argv) == 1:
        port = SERVER_PORT
    elif len(sys.argv) == 2:
        try:
            port = int(sys.argv[1])
        except:
            sys.exit("Usage: server.py [port]")
    else:
        sys.exit("Usage: server.py [port]")

    # set up GameServer object
    game_server = game.GameServer(port=port)

    # listen on a port for users who want to start a match
    game_server.listen()

    while True:
        # wait for enough users to start a match
        LOGGER.debug('waiting for match...')
        game_server.wait_for_match()

        # when enough users connect, start a match
        LOGGER.debug('starting match...')
        game_server.start_match()
    
        # while the match is not over:
        last_tick = time.time()
        while game_server.in_game:
            #print(game_server.engine.current_tick)
            # get inputs from each user
            game_server.check_inputs()
            # relay inputs to each other user
            game_server.relay_inputs()

            # check if we need to move to the next frame
            t = time.time()
            if t-last_tick > 1/FRAMERATE: # seconds per frame
                last_tick = t
                game_server.advance_game()

            # check if the match is over
            if game_server.match_finished(): 
                game_server.end_match()


if __name__ == "__main__":
    main()