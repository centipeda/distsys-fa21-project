"""Class definitions for running, hosting, and drawing the game."""

import pygame, pygame.font
from pygame import mouse
import sys
import time
import socket
import math

from globalvars import *
import game_objects

class GameDisplay:
    """Renders the game state to the screen."""

    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.state = "init"
        self.camera_pos = (0,0)
    
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
                mouse_pos = pygame.mouse.get_pos()
                if self.quit_rect.collidepoint(mouse_pos):
                    self.state = "quit"
                if self.start_rect.collidepoint(mouse_pos):
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
    
    def draw_frame(self, client):
        """Draws the current state of the game to the screen."""
        engine = client.engine
        # draw background
        pygame.draw.rect(self.screen, COLOR_WHITE, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        # draw each entity
        for entity in engine.entities:
            ent_x, ent_y = entity.position
            cam_x, cam_y = self.camera_pos
            draw_pos = (ent_x-cam_x, ent_y-cam_y)
            # draw player entity
            if entity.kind == game_objects.EntityKind.PLAYER:
                pygame.draw.circle(self.screen, COLOR_RED, draw_pos, PLAYER_SIZE)
                if entity.uid == client.player_id:
                    dir_x,dir_y = entity.direction
                    angle = math.atan2(dir_y,dir_x)
                    l_x = (ent_x-cam_x) + GUIDELINE_LENGTH*math.cos(angle)
                    l_y = (ent_y-cam_y) + GUIDELINE_LENGTH*math.sin(angle)
                    pygame.draw.line(self.screen, COLOR_RED, draw_pos, (l_x,l_y), GUIDELINE_WIDTH)
            # draw projectile
            elif entity.kind == game_objects.EntityKind.PROJECTILE:
                pygame.draw.circle(self.screen, COLOR_BLUE, draw_pos, PROJECTILE_SIZE)

        # flip display
        pygame.display.flip()

class GameEngine:
    """Manages game state, accounting for inputs scheduled for the past,
    present, and future."""

    def __init__(self):
        self.current_tick = 0
        self.entities = []
        self.inputs = {}
        self.frames = {}
    
    def register_input(self, uid, user_input, tick=None):
        """Adds a set of input corresponding to a single tick."""
        if tick is None:
            tick = self.current_tick
        if tick not in self.inputs:
            self.inputs[tick] = {}
        self.inputs[tick][uid] = user_input
    
    def init_game(self):
        """Sets up or resets variables needed to start a game."""
        pass

    def advance_tick(self):
        """Advances the game by one tick, updating the positions and states
        of all game entities."""
        for entity in self.entities:
            if entity.kind == game_objects.EntityKind.PLAYER:
                if self.current_tick in self.inputs and entity.uid in self.inputs[self.current_tick]:
                    entity.update_velocity(self.inputs[self.current_tick][entity.uid])
                    if self.inputs[self.current_tick][entity.uid]['fired']:
                        p = entity.shoot_projectile()
                        if p is not None:
                            self.entities.append(p)
            elif entity.kind == game_objects.EntityKind.PROJECTILE:
                if entity.to_delete:
                    self.entities.remove(entity)
                    print(f'deleting {entity}')
                    continue
                hit = entity.check_collisions(self.entities)
                if hit is not None:
                    print(f'hit {hit}!')
            entity.update_position()

        self.current_tick += 1

    def add_user(self, uid, position=(0,0)):
        """Adds a user to a waiting or ongoing match."""
        # instantiate new Player
        new_player = game_objects.Player(uid=uid, position=position)
        self.entities.append(new_player)

    def remove_user(self, uid):
        """Removes a user to a waiting or ongoing match."""
        pass

    def rollback_to(self, tick, begin_tick=0):
        """Rolls the game state back to what it was at the specified tick."""
        pass

class GameClient:
    """Faciliates communication between the user and the server's game states."""
    def __init__(self):
        self.server_host = None
        self.server_port = None
        self.engine = GameEngine()
        self.input_state = {
            pygame.K_w : False,
            pygame.K_a : False,
            pygame.K_s : False,
            pygame.K_d : False,
            'fired': False
        }
        self.player_id = 0

    def get_input(self):
        input_state = dict(self.input_state)
        input_state['fired'] = False
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key in self.input_state:
                    input_state[event.key] = True
                if event.key == pygame.K_SPACE:
                    input_state['fired'] = True
            elif event.type == pygame.KEYUP:
                if event.key in self.input_state:
                    input_state[event.key] = False
            elif event.type == pygame.QUIT:
                sys.exit()
        return input_state
    
    def process_input(self):
        """Gets input from the user, registers it in the dict of all inputs,
        then sends it to the server."""
        # get current input state
        new_state = self.get_input()

        # check if this is different from last frame's input
        changed = False
        for key in self.input_state:
            if new_state[key] != self.input_state[key]:
                changed = True

        # record/send input to server only if there's been a change
        if changed:
            self.input_state = new_state
            self.send_input()
            # send input to game engine
            self.engine.register_input(self.player_id, self.input_state)


    def recv_input(self):
        """Checks if there is input from the server, and updates
        the local game state accordingly."""

    def advance_game(self):
        self.engine.advance_tick()

    def send_input(self):
        """Sends the current input state to the server."""
        pass

    def connect(self, host, port):
        """Connects to a server listening on the given host and port."""
        pass

    def join_game(self):
        """Attempts to join a game on the host server."""
        # Ask server to join a game
        # If we do get to join a game, set our player id and
        # reset the game state
        # dummy method: wait for a few seconds
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
