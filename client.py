"""Executable for joining and playing matches."""

import sys

import pygame

import game
from globalvars import FRAMERATE

def main():
    game_client  = game.GameClient()
    game_display = game.GameDisplay()
    game_display.init_titlescreen()
    while True:
        # lock the global framerate
        game_display.clock.tick(FRAMERATE)

        if game_display.state == "title":
            game_display.input_titlescreen()
            if game_display.state == "quit":
                sys.exit()
            elif game_display.state == "waiting":
                # initialize waiting room
                game_client.start_game()
                player = game_client.engine.add_user(game_client.player_id, (100, 100))
                game_client.engine.add_user(1, (500, 500))

                # ask to join a game
                game_client.join_game()
                continue
            game_display.draw_titlescreen()

        elif game_display.state == "waiting":
            game_client.update_server()
            msg = game_client.check_join_game()
            if msg is not None and msg['method'] == 'MATCH_JOINED':
                player.uid = msg['user_id']
            # get input
            game_client.process_input()
            #game_client.send_input()
            # update game state
            game_client.advance_game()
            # draw game
            game_display.focus_entity(player)
            game_display.draw_frame(game_client)

if __name__ == "__main__":
    main()