import pygame, pygame.font
import sys
import socket

from globalvars import *

class GameDisplay:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.state = "init"
    
    # return top-left position to render text at to center it on screen with
    # the given font, text, and vertial position
    def get_center_pos(self, font, text, ypos):
        width, height = font.size(text)
        xpos = (SCREEN_WIDTH / 2) - width/2
        return (xpos, ypos)
    
    def init_titlescreen(self):
        self.state = "title"
        self.title_font = pygame.font.Font(pygame.font.get_default_font(), 64)
        self.menu_font  = pygame.font.Font(pygame.font.get_default_font(), 48)
        starttext = self.menu_font.render("START", False, COLOR_BLACK)
        self.start_rect = self.screen.blit(starttext, self.get_center_pos(self.menu_font, "START", 300))
        quittext = self.menu_font.render("QUIT", False, COLOR_BLACK)
        self.quit_rect = self.screen.blit(quittext, self.get_center_pos(self.menu_font, "QUIT", 500))

    def input_titlescreen(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state = "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x,mouse_y = pygame.mouse.get_pos()
                if self.quit_rect.collidepoint(mouse_x, mouse_y):
                    self.state = "quit"
                if self.start_rect.collidepoint(mouse_x, mouse_y):
                    self.state = "game"

    def draw_titlescreen(self):
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
        pass

class GameEngine:
    def __init__(self):
        self.current_tick = 0
        self.entities = []
        self.inputs = {}
        self.frames = {}
    
    def register_input(self, user_input, tick=None):
        if tick is None:
            tick = self.current_tick
        self.inputs[tick] = user_input
    
    def init_game(self):
        pass

    def advance_frame(self):
        self.current_tick += 1

    def add_user(self):
        pass

    def remove_user(self):
        pass

class GameClient:
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
    
    def accept_input(self):
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

    def connect_server(self):
        pass

    def join_game(self):
        pass

    def start_game(self):
        self.engine.init_game()

class GameServer:
    def __init__(self):
        self.engine = GameEngine()