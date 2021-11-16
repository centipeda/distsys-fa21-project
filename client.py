"""Executable for joining and playing matches."""

import sys

import pygame

import game
from globalvars import FRAMERATE, LOGGER, STATE_SAVE_RATE

def main():
    game_client  = game.GameClient()
    game_display = game.GameDisplay()
    game_display.init_titlescreen()
    game_state = "title"

    while True:
        # lock the global framerate
        game_display.clock.tick(FRAMERATE)

        if game_state == "title":
            next_state = game_display.input_titlescreen()
            if next_state == "quit":
                sys.exit()
            elif next_state == "waiting":
                # initialize waiting room
                game_client.start_game()
                player = game_client.engine.add_user(game_client.player_id, (100, 100))
                game_client.engine.add_user(1, (500, 500))

                # ask to join a game
                game_client.join_game()
            game_display.draw_titlescreen()
            game_state = next_state

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
            game_display.focus_entity(player)
            game_display.draw_frame(game_client)
        
        elif game_state == "match":
            if game_client.engine.current_tick % STATE_SAVE_RATE == 0:
                LOGGER.debug('saving frame on tick %d', game_client.engine.current_tick)

            game_client.update_server()
            game_client.recv_input()

            game_client.process_input()

            game_client.advance_game()

            game_display.focus_entity(game_client.get_player())
            game_display.draw_frame(game_client)

if __name__ == "__main__":
    main()