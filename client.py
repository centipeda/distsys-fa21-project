"""Executable for joining and playing matches."""

import sys

import pygame

import game
from globalvars import FRAMERATE, LOGGER, SERVER_HOST, SERVER_PORT, SKIP_INTRO, STATE_SAVE_RATE

def main():
    host = SERVER_HOST
    port = SERVER_PORT
    if len(sys.argv) > 1:
        host = sys.argv[1]

    game_client = game.GameClient(server_host=host,server_port=port,display=True)
    if not SKIP_INTRO:
        game_client.play_intro()
    game_state = "title"

    while True:
        # lock the global framerate
        game_client.display.tick(FRAMERATE)

        # client behavior based on client state
        if game_state == "title": # if we're on the title screen
            game_state = game_client.play_titlescreen()
            continue
        elif game_state == "connecting": 
            # check if we need to connect to the server
            if not game_client.connected():
                # update now to show the "connecting" message
                game_client.display.add_message('Connecting to server...')
                game_client.play_titlescreen()

            # try connecting to the server
            if game_client.connect_server():
                game_client.display.add_message('Connected!')
                # ask the server to join a game
                game_client.join_game()
                # initialize waiting room
                game_client.start_game()
                player = game_client.engine.add_user(game_client.player_id, (100, 100))
                game_client.engine.add_user(1, (500, 500))
                game_state = "waiting"
            else:
                game_client.display.add_message('Failed to connect to server.')
                game_state = "title"
        elif game_state == "waiting": # if we're connected to the server and are waiting for a match
            if not game_client.update_server():
                game_client.display.add_message('Disconnected from server.')
                game_state = "title"

            # check if we should start the match
            msg = game_client.check_join_game()
            if msg is not None:
                if msg['method'] == 'MATCH_JOINED':
                    game_client.display.add_message('Found match!')
                    player.uid = msg['user_id']
                elif msg['method'] == "START_MATCH":
                    game_client.display.add_message('Match beginning...')
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
            game_client.display.draw_messages()
            pygame.display.flip()

        elif game_state == "match": # if we're playing a match right now
            # try to communicate with server
            if not game_client.update_server():
                game_client.display.add_message('Disconnected from server.')
                game_state = "title"
                game_client.live_match = False

            game_client.recv_input()
            if game_client.recv_end():
                game_state = "title"

            # process local events
            game_client.process_input()
            game_client.advance_game()

            # draw game state to screen
            game_client.display.focus_entity(game_client.get_player())
            game_client.display.draw_frame(game_client)
            game_client.display.draw_messages()
            pygame.display.flip()
        
        elif game_state == "quit":
            sys.exit()

if __name__ == "__main__":
    main()