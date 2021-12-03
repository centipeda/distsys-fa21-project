"""Executable for hosting matches."""

import time
import game_bot
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
    game_server = game_bot.GameServer(port=port)

    # listen on a port for users who want to start a match
    game_server.listen()

    while True:
        # wait for enough users to start a match
        LOGGER.debug('waiting for match...')
        if not game_server.wait_for_match():
            continue

        # when enough users connect, try to start a match
        LOGGER.debug('starting match...')
        if not game_server.start_match():
            LOGGER.debug('failed to start match.')
            continue
    
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
                # send a synchronization packet to all clients if it's time
                if game_server.engine.current_tick > 0 and \
                   game_server.engine.current_tick % RESYNC_RATE == 0:
                    LOGGER.debug('syncing clients...')
                    game_server.sync_clients()

            # check if the match is over
            if game_server.match_finished(): 
                print("\n\n\n\n\n")
                print("GAME ENDED: ")
                print("Rollback Count:", game_server.engine.rollback_cnt)
                print("Rollback Ticks Lost:", game_server.engine.rollback_lost)
                print("Ops Count:", game_server.ops_cnt)
                print("Ops/Sec:", game_server.ops_cnt/MATCH_LENGTH)
                print("Sec/ops:", MATCH_LENGTH/game_server.ops_cnt)
                print("\n\n\n\n\n")
                game_server.end_match()


if __name__ == "__main__":
    main()