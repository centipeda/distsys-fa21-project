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
            elif game.display.state == "game":
                game_client.start_game()
                continue
            game_display.draw_titlescreen()
        elif game_display.state == "game":
            game_client.accept_input()


if __name__ == "__main__":
    main()