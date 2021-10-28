"""Executable for joining and playing matches."""

import sys

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
                game_client.start_game()
                game_client.engine.add_user(game_client.player_id)
                continue
            game_display.draw_titlescreen()
        elif game_display.state == "waiting":
            # ask the server if there's a game to join
            game_client.join_game()
            # get input
            game_client.process_input()
            # update game state
            game_client.advance_game()
            # draw game
            game_display.draw_frame(game_client.engine)


if __name__ == "__main__":
    main()