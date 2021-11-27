"""Executable for joining and playing matches."""

import sys

import pygame

import game
from globalvars import FRAMERATE, LOGGER, SERVER_HOST, SERVER_PORT, STATE_SAVE_RATE

def main():
    host = SERVER_HOST
    port = SERVER_PORT
    if len(sys.argv) > 1:
        host = sys.argv[1]

    LOGGER.debug('attempting to connnect to %s:%d...', host, port)

    game_client = game.GameClient(server_host=host,server_port=port,display=True)
    game_client.play_intro()
    game_state = "title"

    while True:
        # lock the global framerate
        game_client.display.tick(FRAMERATE)

        if game_state == "title":
            next_state = game_client.play_titlescreen()

            if next_state == "quit":
                sys.exit()
            elif next_state == "waiting":
                game_state = next_state
                # initialize waiting room
                game_client.start_game()
                player = game_client.engine.add_user(game_client.player_id, (100, 100))
                game_client.engine.add_user(1, (500, 500))

                # ask to join a game
                game_client.join_game()

        elif game_state == "waiting":
            if not game_client.update_server():
                game_state = "title"
            msg = game_client.check_join_game()
            if msg is not None:
                if msg['method'] == 'MATCH_JOINED':
                    player.uid = msg['user_id']
                elif msg['method'] == "START_MATCH":
                    player = game_client.get_player()
                    game_state = "match"
            # get input
            game_client.process_input()
            #game_client.send_input()
            # update game state
            game_client.advance_game()
            # draw game
            game_client.display.focus_entity(player)
            game_client.display.draw_frame(game_client)
        
        elif game_state == "match":
            # communicate with server
            game_client.update_server()
            game_client.recv_input()
            if game_client.recv_end():
                game_state = "title"

            # process local events
            game_client.process_input()
            game_client.advance_game()

            # draw game state to screen
            game_client.display.focus_entity(game_client.get_player())
            game_client.display.draw_frame(game_client)

if __name__ == "__main__":
    main()