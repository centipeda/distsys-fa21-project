"""Class definitions for running, hosting, and drawing the game."""

import pygame, pygame.font
import sys
import socket

from globalvars import *

class GameDisplay:
    """Renders the game state to the screen."""

    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.state = "init"
    
    def get_center_pos(self, font, text, ypos):
        """Returns the top-lef tposition to render it at the center of the screen
        with the given font, text, and vertical position."""
        width, height = font.size(text)
        xpos = (SCREEN_WIDTH / 2) - width/2
        return (xpos, ypos)
    
    def init_titlescreen(self):
        """Sets up title screen."""
        self.state = "title"
        self.title_font = pygame.font.Font(pygame.font.get_default_font(), 64)
        self.menu_font  = pygame.font.Font(pygame.font.get_default_font(), 48)
        starttext = self.menu_font.render("START", False, COLOR_BLACK)
        self.start_rect = self.screen.blit(starttext, self.get_center_pos(self.menu_font, "START", 300))
        quittext = self.menu_font.render("QUIT", False, COLOR_BLACK)
        self.quit_rect = self.screen.blit(quittext, self.get_center_pos(self.menu_font, "QUIT", 500))

    def input_titlescreen(self):
        """Receives input from the user, checking if they've clicked a button
        on the title screen."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state = "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x,mouse_y = pygame.mouse.get_pos()
                if self.quit_rect.collidepoint(mouse_x, mouse_y):
                    self.state = "quit"
                if self.start_rect.collidepoint(mouse_x, mouse_y):
                    self.state = "waiting"

    def draw_titlescreen(self):
        """Draws the current state of the title screen to the screen."""
        self.screen.fill(COLOR_WHITE)

        title = self.title_font.render("Lag Warriors", False, COLOR_BLACK)
        self.screen.blit(title, self.get_center_pos(self.title_font, "Lag Warriors", 100))

        starttext = self.menu_font.render("START", False, COLOR_BLACK)
        r = self.screen.blit(starttext, self.get_center_pos(self.menu_font, "START", 300))
        r.update(r.left-5, r.top-5, r.width+10, r.height+10)
        pygame.draw.rect(self.screen, COLOR_BLACK, r, width=1)

        quittext = self.menu_font.render("QUIT", False, COLOR_BLACK)
        r = self.screen.blit(quittext, self.get_center_pos(self.menu_font, "QUIT", 500))
        r.update(r.left-5, r.top-5, r.width+10, r.height+10)
        pygame.draw.rect(self.screen, COLOR_BLACK, r, width=1)

        pygame.display.flip()
    
    def draw_frame(self, entities):
        """Draws the current state of the game to the screen."""

        pass

class GameEngine:
    """Manages game state, accounting for inputs scheduled for the past,
    present, and future."""

    def __init__(self):
        self.current_tick = 0
        self.entities = []
        self.inputs = {}
        self.frames = {}
    
    def register_input(self, user_input, tick=None):
        """Adds a set of input corresponding to a single tick."""
        if tick is None:
            tick = self.current_tick
        self.inputs[tick] = user_input
    
    def init_game(self):
        """Sets up or resets variables needed to start a game."""
        pass

    def advance_tick(self):
        """Advances the game by one tick, updating the positions and states
        of all game entities."""
        self.current_tick += 1

    def add_user(self):
        """Adds a user to a waiting or ongoing match."""
        pass

    def remove_user(self):
        """Removes a user to a waiting or ongoing match."""
        pass

    def rollback_to(self, tick):
        """Rolls the game state back to what it was at the specified tick."""
        pass

class GameClient:
    """Faciliates communication between the user and the server's game states."""
    def __init__(self):
        self.server_host = SERVER_HOST
        self.server_port = SERVER_PORT
        self.engine = GameEngine()
        self.input_state = {
            pygame.K_w : False,
            pygame.K_a : False,
            pygame.K_s : False,
            pygame.K_d : False,
            pygame.K_SPACE : False
        }
    
    def process_input(self):
        """Gets input from the user, registers it in the dict of all inputs,
        then sends it to the server."""
        # get input from queue
        for event in pygame.event.get():
            if event == pygame.KEYDOWN:
                if event.key in self.input_state:
                    self.input_state[event.key] = True
            elif event == pygame.KEYUP:
                if event.key in self.input_state:
                    self.input_state[event.key] = False
        # send input to server only if we have something pressed
        if True in self.input_state.values():
            self.send_input()
        # send input to game engine
        self.engine.register_input(self.input_state)

    def send_input(self):
        """Sends the current input state to the server."""

    def connect(self, host, port):
        """Connects to a server listening on the given host and port."""
        pass

    def join_game(self):
        """Attempts to join a game on the host server."""
        pass

    def start_game(self):
        """Starts the local game engine."""
        self.engine.init_game()

class GameServer:
    """Manages users joining/leaving matches, determines when matches begin and end,
    and relays inputs to and from players in a match."""
    socket = None
    user_sockets = []

    def __init__(self):
        self.engine = GameEngine()

    def listen(self, addr, port):
        """Listens for users on the specified host and port."""
        pass

    def start_match(self):
        """Begin a game, initializing the local game state and telling all
        users when the match will begin."""
        pass

    def end_match(self):
        """End a game, telling all users who the victor is."""
        pass

    def check_inputs(self):
        """Checks each player in the match for input."""
        pass

    def relay_inputs(self, inputs):
        """Relays the given input to all other players
        in the match."""
        pass

    def match_finished(self):
        """Determines whether the current match is over or not."""
        pass
