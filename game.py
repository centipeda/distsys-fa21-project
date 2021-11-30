"""Class definitions for running, hosting, and drawing the game."""

import random
import pygame, pygame.font, pygame.time
import time
import sys
import math
import socket
import uuid
import select

from globalvars import *
import helpers
from game_objects import Pickup, Player,EntityKind,deserialize_entity


class GameDisplay:
    """Renders the game state to the screen."""

    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.camera_pos = (0,0)
        self.title_font = pygame.font.Font('assets/Iceland-Regular.ttf', 96)
        self.menu_font  = pygame.font.Font('assets/Iceland-Regular.ttf', 48)
        self.subtitle_font  = pygame.font.Font('assets/Iceland-Regular.ttf', 26)
        self.message_font = pygame.font.Font('assets/CourierPrime-Regular.ttf', 18)
        self.top_button_rect = None
        self.bot_button_rect = None
        self.max_messages = 5
        self.messages = []
    
    def tick(self, framerate):
        """Ticks the pygame clock forward to lock the framerate."""
        self.clock.tick(framerate)
    
    def get_center_pos(self, font, text, ypos):
        """Returns the top-left position to render text at the center of the screen
        with the given font, string, and vertical position."""
        width, _height = font.size(text)
        xpos = (SCREEN_WIDTH / 2) - width/2
        return (xpos, ypos)
    
    def draw_text_at(self, font, color, string, position):
        """Render the string to the screen with the top-left
        at the given (x,y) position. Returns a rect of the affected
        pixels."""
        text = font.render(string, False, color)
        return self.screen.blit(text, position)

    def draw_text_centered(self, font, color, string, y_position, x_offset=0):
        """Render the string to the screen at the given y position, with
        the given x offset. Returns a rect of the affected positions."""
        text = font.render(string, False, color)
        x,y = self.get_center_pos(font, string, y_position)
        x += x_offset
        return self.screen.blit(text, (x,y))
    
    def add_message(self, message):
        """Adds a message to the 'console readout', removing old
        ones if necessary."""
        self.messages.insert(0, message)
        if len(self.messages) > self.max_messages:
            self.messages.pop()
    
    def draw_messages(self):
        """Draws 'console message' readout to screen."""
        msgbox_height = self.message_font.get_linesize()*(self.max_messages+1)
        msgbox_width = 400
        msgbox_padding = 15
        msgbox_rect = pygame.Rect(SCREEN_WIDTH-msgbox_width, SCREEN_HEIGHT-msgbox_height, msgbox_width,msgbox_height)
        msgbox_surface = pygame.Surface((msgbox_width, msgbox_height))
        msgbox_surface.set_alpha(128)
        pygame.draw.rect(msgbox_surface, COLOR_BLACK, (0,0,msgbox_width,msgbox_height), border_radius=5)
        self.screen.blit(msgbox_surface, msgbox_rect.topleft)

        x,y = msgbox_rect.bottomleft
        x += msgbox_padding
        y -= self.message_font.get_linesize()
        for msg in self.messages:
            self.draw_text_at(self.message_font, COLOR_GREEN, msg, (x,y))
            y -= self.message_font.get_linesize()
    
    def play_intro(self):
        """Plays the startup animation."""
        shing_sound = pygame.mixer.Sound('assets/shing.wav')
        thump_sound = pygame.mixer.Sound('assets/thump.wav')
        credit_string = "Made by Rafael Mendizabal and Joshua Cepeda"
        tick = 0
        angle = 80 # degrees
        letter = 0
        offset = SCREEN_HEIGHT/2*math.tan(math.pi / 180 * angle)
        empty = 120
        slash = 10
        slide = 30
        title = 50
        end = empty+slash+slide+title

        t = 0
        empty_screen = range(t, t+empty)
        t += empty
        slash_screen = range(t, t+slash)
        t += slash
        slide_screen = range(t, t+slide)
        t += slide
        title_write = range(t, t+title)

        while True:
            # tick forward intro
            tick += 1
            self.clock.tick(FRAMERATE)
            # catch quit event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            if tick in empty_screen:
                progress = (tick-empty_screen[0])/len(empty_screen)
                shade = (1 - 2**(-10*progress))*255
                self.screen.fill(COLOR_BLACK)
                pygame.draw.circle(self.screen, COLOR_WHITE, (SCREEN_WIDTH/2,SCREEN_HEIGHT/2), 200)
                wrap = int(len(credit_string)/2)+5
                self.draw_text_centered(self.menu_font, (shade, shade, shade), credit_string[0:wrap], 50)
                self.draw_text_centered(self.menu_font, (shade, shade, shade), credit_string[wrap:], 50+self.menu_font.get_linesize())
                self.draw_text_centered(self.menu_font, (shade, shade, shade), "Distributed Systems, Fall 2021", 700)
            elif tick in slash_screen:
                if tick == slash_screen[0]:
                    shing_sound.play()
                progress = (tick-slash_screen[0])/len(slash_screen)
                start_pos = (SCREEN_WIDTH/2+offset, 0)
                end_pos = (SCREEN_WIDTH/2+offset-(offset*2*progress), (SCREEN_HEIGHT)*progress)

                self.screen.fill(COLOR_BLACK)
                pygame.draw.circle(self.screen, COLOR_WHITE, (SCREEN_WIDTH/2,SCREEN_HEIGHT/2), 200)
                pygame.draw.line(self.screen, COLOR_WHITE, start_pos, end_pos, width=5)
            elif tick in slide_screen:
                progress = (tick-slide_screen[0])/len(slide_screen)
                eased_progress = 1 - 2**(-10*progress) # easing algorithm
                start_pos = (SCREEN_WIDTH/2+offset, 0)
                end_pos = (SCREEN_WIDTH/2-offset, SCREEN_HEIGHT)
                start_angle = (90 - angle)/180*math.pi
                end_angle = start_angle + math.pi
                slide_offset = (eased_progress*50)
                xslide = slide_offset*math.cos((90-angle)/180*math.pi)
                yslide = slide_offset*math.sin((90-angle)/180*math.pi)
                color_progress = int(255*progress)
                reddish = (255, 255-color_progress, 255-color_progress)
                blueish = (255-color_progress, 255-color_progress, 255)

                self.screen.fill(COLOR_BLACK)
                # pygame.draw.circle(self.screen, COLOR_WHITE, (SCREEN_WIDTH/2,SCREEN_HEIGHT/2), 200)
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        pygame.draw.arc(self.screen, reddish, (200+xslide+i, 200-yslide+j, 400, 400), start_angle=start_angle, stop_angle=end_angle,width=200)
                        pygame.draw.arc(self.screen, blueish, (200-xslide+i, 200+yslide+j, 400, 400), start_angle=end_angle, stop_angle=start_angle,width=200)
                pygame.draw.line(self.screen, COLOR_WHITE, start_pos, end_pos, width=5)
            elif tick in title_write:
                progress = (tick-title_write[0])/len(title_write)
                eased_progress = 1 - (1-progress)**3
                credit_text_offset = 100
                if int(len(GAME_TITLE)*progress)+1 > letter:
                    thump_sound.play()
                letter = int(len(GAME_TITLE)*progress)+1
                start_pos = (SCREEN_WIDTH/2+offset, 0)
                end_pos = (SCREEN_WIDTH/2-offset, SCREEN_HEIGHT)

                self.screen.fill(COLOR_BLACK)
                # pygame.draw.circle(self.screen, COLOR_WHITE, (SCREEN_WIDTH/2,SCREEN_HEIGHT/2), 200)
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        pygame.draw.arc(self.screen, COLOR_RED, (200+xslide+i, 200-yslide+j, 400, 400), start_angle=start_angle, stop_angle=end_angle,width=200)
                        pygame.draw.arc(self.screen, COLOR_BLUE, (200-xslide+i, 200+yslide+j, 400, 400), start_angle=end_angle, stop_angle=start_angle,width=200)
                pygame.draw.line(self.screen, COLOR_WHITE, start_pos, end_pos, width=5)
                self.draw_text_centered(self.title_font, COLOR_WHITE, GAME_TITLE[:letter], 50)
                self.draw_text_centered(self.subtitle_font, COLOR_WHITE, credit_string, 700+credit_text_offset*(1-eased_progress))
                self.draw_text_centered(self.subtitle_font, COLOR_WHITE, "Distributed Systems, Fall 2021", 700+self.subtitle_font.get_linesize()+credit_text_offset*(1-eased_progress))
            elif tick == end:
                return
            else:
                self.screen.fill(COLOR_BLACK)
                # pygame.draw.circle(self.screen, COLOR_WHITE, (SCREEN_WIDTH/2,SCREEN_HEIGHT/2), 200)
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        pygame.draw.arc(self.screen, COLOR_RED, (200+xslide+i, 200-yslide+j, 400, 400), start_angle=start_angle, stop_angle=end_angle,width=200)
                        pygame.draw.arc(self.screen, COLOR_BLUE, (200-xslide+i, 200+yslide+j, 400, 400), start_angle=end_angle, stop_angle=start_angle,width=200)
                pygame.draw.line(self.screen, COLOR_WHITE, start_pos, end_pos, width=5)
                title = self.title_font.render(GAME_TITLE)
                self.screen.blit(title, self.get_center_pos(self.title_font, GAME_TITLE, 50))
                # self.draw_text_centered(self.menu_font, COLOR_WHITE, "Distributed Systems, Fall 2021", 700)
                self.draw_text_centered(self.title_font, COLOR_WHITE, "START", 260, x_offset=40)
                self.draw_text_centered(self.title_font, COLOR_WHITE, "QUIT", 450, x_offset=-50)

            pygame.display.flip()

    def draw_titlescreen(self, hover_start=False, hover_quit=False):
        """Draws the current state of the title screen to the screen."""
        credit_string = "Made by Rafael Mendizabal and Joshua Cepeda"
        credit_text_offset = 100
        angle = 80 # degrees
        xslide = 50*math.cos((90-angle)/180*math.pi)
        yslide = 50*math.sin((90-angle)/180*math.pi)
        offset = SCREEN_HEIGHT/2*math.tan(math.pi / 180 * angle)
        start_angle = (90 - angle)/180*math.pi
        end_angle = start_angle + math.pi
        start_pos = (SCREEN_WIDTH/2+offset, 0)
        end_pos = (SCREEN_WIDTH/2-offset, SCREEN_HEIGHT)

        top_fill = COLOR_WHITE if hover_start else COLOR_RED
        bot_fill = COLOR_WHITE if hover_quit else COLOR_BLUE
        top_text = COLOR_WHITE if not hover_start else COLOR_RED
        bot_text = COLOR_WHITE if not hover_quit else COLOR_BLUE

        self.screen.fill(COLOR_BLACK)
        # pygame.draw.circle(self.screen, COLOR_WHITE, (SCREEN_WIDTH/2,SCREEN_HEIGHT/2), 200)
        self.top_button_rect = pygame.draw.arc(self.screen, top_fill, (200+xslide, 200-yslide, 400, 400), start_angle=start_angle, stop_angle=end_angle,width=200)
        self.bot_button_rect = pygame.draw.arc(self.screen, bot_fill, (200-xslide, 200+yslide, 400, 400), start_angle=end_angle, stop_angle=start_angle,width=200)
        for i in range(-1, 2):
            for j in range(-1, 2):
                pygame.draw.arc(self.screen, top_fill, (200+xslide+i, 200-yslide+j, 400, 400), start_angle=start_angle, stop_angle=end_angle,width=200)
                pygame.draw.arc(self.screen, bot_fill, (200-xslide+i, 200+yslide+j, 400, 400), start_angle=end_angle, stop_angle=start_angle,width=200)
        pygame.draw.line(self.screen, COLOR_WHITE, start_pos, end_pos, width=5)
        title = self.title_font.render(GAME_TITLE, False, COLOR_WHITE)
        self.screen.blit(title, self.get_center_pos(self.title_font, GAME_TITLE, 50))
        self.draw_text_centered(self.title_font, top_text, "START", 260, x_offset=40)
        self.draw_text_centered(self.title_font, bot_text, "QUIT", 450, x_offset=-50)
        self.draw_text_centered(self.subtitle_font, COLOR_WHITE, credit_string, 700)
        self.draw_text_centered(self.subtitle_font, COLOR_WHITE, "Distributed Systems, Fall 2021", 700+self.subtitle_font.get_linesize())
    
    def focus_entity(self, entity):
        """Center camera on entity by setting camera position to entity's position."""
        x,y = entity.position
        self.camera_pos = (x-SCREEN_WIDTH/2, y-SCREEN_HEIGHT/2)
        self.camera_pos = (x,y)

    def world_to_screen_pos(self, position):
        x,y = position
        cam_x, cam_y = self.camera_pos
        p = (x-cam_x+SCREEN_WIDTH/2, y-cam_y+SCREEN_HEIGHT/2)
        return p
    
    def draw_countdown(self, countdown_time):
        """Draws an indicator counting down to the match beginning."""
        self.draw_text_centered(self.menu_font, COLOR_GREEN, "STARTING IN", 350)
        self.draw_text_centered(self.menu_font, COLOR_GREEN, str(countdown_time), 350+self.menu_font.get_linesize())
    
    def draw_frame(self, client):
        """Draws the current state of the game to the screen."""
        engine = client.engine
        cam_x, cam_y = self.camera_pos
        # draw background
        pygame.draw.rect(self.screen, COLOR_BLACK, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        arena_rect = pygame.Rect(self.world_to_screen_pos((0,0)), (ARENA_SIZE, ARENA_SIZE))
        pygame.draw.rect(self.screen, COLOR_GRAY, arena_rect)

        # draw each entity
        for entity_id in engine.entities:
            entity = engine.entities[entity_id]
            ent_x, ent_y = self.world_to_screen_pos(entity.position)
            # draw player entity
            if entity.kind == EntityKind.PLAYER:
                pygame.draw.circle(self.screen, COLOR_RED, (ent_x,ent_y), PLAYER_SIZE)
                if entity.uid == client.player_id:
                    dir_x,dir_y = entity.direction
                    angle = math.atan2(dir_y,dir_x)
                    l_x = ent_x + GUIDELINE_LENGTH*math.cos(angle)
                    l_y = ent_y + GUIDELINE_LENGTH*math.sin(angle)
                    pygame.draw.line(self.screen, COLOR_RED, (ent_x,ent_y), (l_x,l_y), GUIDELINE_WIDTH)
            # draw projectile
            elif entity.kind == EntityKind.PROJECTILE:
                pygame.draw.circle(self.screen, COLOR_BLUE, (ent_x,ent_y), PROJECTILE_SIZE)
            elif entity.kind == EntityKind.PICKUP:
                pygame.draw.circle(self.screen, COLOR_YELLOW, (ent_x,ent_y), PICKUP_SIZE)

        # draw the HUD
        if client.live_match:
            time_remaining = (MATCH_LENGTH - int(client.engine.current_tick/FRAMERATE))
            self.draw_text_centered(self.menu_font, COLOR_GREEN, str(time_remaining), 25)


class GameEngine:
    """Manages game state, accounting for inputs scheduled for the past,
    present, and future."""

    def __init__(self):
        self.input_delay = GLOBAL_INPUT_DELAY
        self.reset_game()

    def reset_game(self):
        """Sets up or resets variables needed to start a game."""
        self.current_tick = 0
        self.entities = {}
        self.inputs = {}
        self.frames = {}
        self.pickup_positions = []
        self.pickups_generated = 0
        self.live_pickups = 0

    def serialize_current_state(self):
        """Returns a dict representing the current state of the game."""
        return {
            "entities": [e.serialize() for e in self.entities.values()],
            "tick": self.current_tick,
            "generated": self.pickups_generated,
            "live": self.live_pickups
        }

    def register_state(self, game_state=None):
        """Saves a state of the game to the engine. If a game state
        dict is not passed, it will save the current state of the game."""
        if game_state is None:
            game_state = self.serialize_current_state()
        self.frames[game_state['tick']] = game_state

    def register_input(self, uid, user_input, tick=None):
        """Adds a set of input corresponding to a single tick."""
        if tick is None:
            tick = self.current_tick + self.input_delay
        if tick not in self.inputs:
            self.inputs[tick] = {}
        self.inputs[tick][uid] = user_input
    
    def load_state(self, game_state):
        """Load the given game state to the current tick.  If one is not 
        given, load the most recent game state we've been given."""
        if game_state is not None:
            self.frames[game_state['tick']] = game_state
            self.current_tick = game_state['tick']
            self.pickups_generated = game_state['generated']
            self.live_pickups = game_state['live']
            self.entities = {}
            for e in game_state['entities']:
                entity = deserialize_entity(e)
                self.entities[id(entity)] = entity

    def advance_tick(self):
        """Advances the game by one tick, updating the positions and states
        of all game entities."""
        # save the current state every STATE_SAVE_RATE frames
        if self.current_tick % STATE_SAVE_RATE == 0:
            self.register_state()

        to_delete = set()
        to_add = []
        for entity_id in self.entities:
            entity = self.entities[entity_id]

            # calculate collisions
            collisions = self.check_collisions()

            # process this frame's input
            if entity.kind == EntityKind.PLAYER:
                if self.current_tick in self.inputs and entity.uid in self.inputs[self.current_tick]:
                    entity.update_velocity(self.inputs[self.current_tick][entity.uid])
                    if self.inputs[self.current_tick][entity.uid]['fired']:
                        p = entity.shoot_projectile()
                        if p is not None:
                            to_add.append(p)
                else:
                    entity.update_velocity()

            # process projectile collisions
            if entity.kind == EntityKind.PROJECTILE:
                if id(entity) in collisions:
                    _colls = collisions[id(entity)]
                    for collided in _colls:
                        if collided.kind == EntityKind.PLAYER and collided.uid != entity.owner_uid:
                            collided.take_hit(entity)
                            to_delete.add(entity)
                        elif collided.kind == EntityKind.PROJECTILE:
                            to_delete.add(entity)
                            to_delete.add(collided)
                # delete if the projectile has gone past the screen
                if entity.bound_position() != entity.position:
                    to_delete.add(entity)
            
            if entity.kind == EntityKind.PICKUP:
                if id(entity) in collisions:
                    _colls = collisions[id(entity)]
                    for collided in _colls:
                        if collided.kind == EntityKind.PLAYER:
                            collided.collect_pickup(entity)
                            self.live_pickups -= 1
                            to_delete.add(entity)

            # update positions based on collisions
            entity.update_position()

        # spawn pickup if we're supposed to
        if self.live_pickups < MAX_PICKUPS and self.current_tick % PICKUP_SPAWN_RATE == 0:
            self.spawn_pickup()

        # cull entities
        for e in to_delete:
            self.remove_entity(e)
            LOGGER.debug('deleting %s', entity)
        # add entities
        for e in to_add:
            self.add_entity(e)

        # advance tick
        self.current_tick += 1

    def check_collisions(self):
        """Checks all combinations of entities for collisions with other entities.
        
        Returns a dict, where keys are the id of each Entity and the values are a list 
        of other entities the Entity has collided with."""
        # this is O(N^2)... we can turn it into an O(N) algorithm
        # with something like the GJK distance algorithm, but we'll
        # cross that bridge when we get to it
        all_collisions = {}
        for entity_id in self.entities:
            entity = self.entities[entity_id]
            collisions = []
            for entity_id2 in self.entities:
                if entity_id2 == entity_id:
                    continue
                other = self.entities[entity_id2]
                if self.collided(entity, other):
                    collisions.append(other)
            if collisions:
                all_collisions[entity_id] = collisions
        return all_collisions
    
    def collided(self, a, b):
        """Checks whether two Entities A and B have collided by
        comparing the distance between their centres with their
        respective sizes."""
        ax,ay = a.position
        bx,by = b.position
        distance = ( (ax-bx)**2 + (ay-by)**2 )**0.5
        # if distance minus both sizes is zero, the entities
        # have collided
        return ((distance - a.size - b.size) < 0)

    def add_user(self, uid, position=(0,0)):
        """Adds a user to a waiting or ongoing match."""
        # instantiate new Player
        return self.add_entity(Player(uid=uid, position=position))

    def remove_user(self, uid):
        """Removes a user to a waiting or ongoing match."""
        return self.remove_entity(self.entities[uid])

    def rollback(self, begin_tick):
        """Recalculates the current game state according to recorded inputs,
        starting at begin_tick."""
        tick_now = self.current_tick
        self.rollback_to(begin_tick=begin_tick)
        self.advance_to(tick_now)

    def rollback_to(self, begin_tick=0):
        """Rolls the game state back to what it was at the specified tick. If 
        we don't have a game state from that tick, load from the next 
        earliest tick."""
        while begin_tick not in self.frames:
            begin_tick -= 1
        self.load_state(self.frames[begin_tick])

    def advance_to(self, tick):
        """Advances the game state to the specified tick."""
        while self.current_tick < tick:
            self.advance_tick()

    def add_entity(self, entity):
        self.entities[id(entity)] = entity
        return entity
    
    def remove_entity(self, entity):
        return self.entities.pop(id(entity))
    
    def place_players(self):
        """Places all players at starting positions."""
        players = [e for e in self.entities.values() if e.kind == EntityKind.PLAYER]
        if not players:
            return
        offset = PLAYER_START_OFFSET+players[0].size
        if len(players) > 0:
            players[0].position = (offset, offset)
        if len(players) > 1:
            players[1].position = (ARENA_SIZE-offset, ARENA_SIZE-offset)
        if len(players) > 2:
            players[2].position = (ARENA_SIZE-offset, offset)
        if len(players) > 3:
            players[3].position = (offset, ARENA_SIZE-offset)

    def generate_pickup_locations(self, seed):
        """Deterministically generates a list of pickup positions from the given seed."""
        LOGGER.debug('generating positions from %s', seed)
        self.pickup_positions = []
        random.seed(seed)
        for p in range(PICKUP_POSITIONS_GENERATED):
            x = random.randrange(PICKUP_SIZE, ARENA_SIZE-PICKUP_SIZE)
            y = random.randrange(PICKUP_SIZE, ARENA_SIZE-PICKUP_SIZE)
            self.pickup_positions.append((x,y))

    def spawn_pickup(self):
        """Creates a new pickup at the next position in the pickup position list."""
        position = self.pickup_positions[self.pickups_generated % len(self.pickup_positions)]
        LOGGER.debug('spawning pickup: %s', str(position))
        self.add_entity(Pickup(position))
        self.pickups_generated += 1
        self.live_pickups += 1
    
    def get_scores(self):
        """Gets the scores of every player currently in the game. Returns a dict with
        keys as user IDs, and values as integers representing scores."""
        return {
            e.uid : e.score for (e_id, e) in self.entities.items() if e.kind == EntityKind.PLAYER
        }
    
class GameClient:
    """Faciliates communication between the user and the server's game states."""
    def __init__(self, server_host=SERVER_HOST, server_port=SERVER_PORT, display=True):
        self.socket = None
        self.server_host = server_host
        self.server_port = server_port
        self.engine = GameEngine()
        self.input_state = {
            pygame.K_w : False,
            pygame.K_a : False,
            pygame.K_s : False,
            pygame.K_d : False,
            'fired': False
        }
        self.player_id = 0
        self.match_id = 0
        self.incoming_messages = []
        self.outgoing_messages = []
        self.scoreboard = {}
        # Whether we're in a waiting room or a real match.
        self.live_match = False
        # self.connect_server()
        if display:
            self.display = GameDisplay()
    
    def connected(self):
        """Returns false if our socket is None or has a negative file descriptor."""
        return self.socket is None or self.socket.fileno() < 0
    
    def play_intro(self):
        """Plays the opening animation."""
        self.display.play_intro()

    def play_titlescreen(self):
        """Manages drawing and input for the title screen/initial menu. Returns
        a string describing the next state of the game client: "start" to start
        waiting for a match, "quit" to exit the client, and "title" to continue
        rendering the title screen."""

        # get input
        state = "title"
        mouse_pos = pygame.mouse.get_pos()
        if self.display.top_button_rect and self.display.bot_button_rect:
            hover_start = self.display.top_button_rect.collidepoint(mouse_pos)
            hover_quit = self.display.bot_button_rect.collidepoint(mouse_pos)
        else:
            hover_quit = hover_start = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state = "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if hover_start:
                    state = "connecting"
                if hover_quit:
                    state = "quit"
        
        # draw title screen
        self.display.draw_titlescreen(hover_start=hover_start,hover_quit=hover_quit)
        self.display.draw_messages()
        pygame.display.flip()

        return state
    
    def get_player(self):
        """Gets the player in the game engine matching our player ID."""
        for entity in self.engine.entities.values():
            if entity.kind == EntityKind.PLAYER and entity.uid == self.player_id:
                return entity
        return None

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
            tick = self.engine.current_tick + GLOBAL_INPUT_DELAY
            self.input_state = new_state
            if self.live_match:
                self.send_input(tick)
            # send input to game engine
            self.engine.register_input(self.player_id, self.input_state, tick=tick)
    
    def recv_state(self):
        """Checks if there is a game state update from the server, if so,
        register it with the game engine."""
        remaining_messages = []
        for message in self.incoming_messages:
            if message['method'] == "GAME_STATE":
                LOGGER.debug('received game state from server')
                self.engine.load_state(message['state'])
            else:
                remaining_messages.append(message)
        self.incoming_messages = remaining_messages
    
    def recv_input(self):
        """Checks if there is input from the server, and updates
        the local game state accordingly, including rolling back to
        a previous game state to account for past input."""
        remaining_messages = []
        for message in self.incoming_messages:
            if message['method'] == "USER_INPUT":
                lowest_tick = self.engine.current_tick
                # register inputs from message
                for player_input in message['inputs']:
                    self.engine.register_input(player_input['user_id'],
                        player_input['input_state'],
                        tick=player_input['tick']
                    )
                    # check if we have an old message
                    if player_input['tick'] < lowest_tick:
                        lowest_tick = player_input['tick']
                # if we have old input, roll back to account for it
                if lowest_tick < self.engine.current_tick:
                    self.engine.rollback(lowest_tick)
            elif message['method'] == "REMOVE_PLAYER":
                # Remove user if server communicates so
                self.engine.remove_user(message['user'])
            else:
                # only get the user input messages from the queue
                remaining_messages.append(message)
        self.incoming_messages = remaining_messages

    def recv_join(self):
        """Checks if there is a match join update from the server, if so,
        update our local game state to prepare to start the match."""
        remaining_messages = []
        m = None
        for message in self.incoming_messages:
            LOGGER.debug('%s', message)
            if message['method'] == "MATCH_JOINED":
                LOGGER.debug('got MATCH_JOINED: %s', message)
                self.player_id = message['user_id']
                self.match_id = message['match_id']
                m = message
            elif message['method'] == "START_MATCH":
                LOGGER.debug('got START_MATCH: %s', message)
                self.start_game(self.match_id)
                self.engine.load_state(message['state'])
                self.live_match = True
                LOGGER.debug('sending ACK')
                try:
                    helpers.send_packet(self.socket, helpers.marshal_message({
                        "method": "ACKNOWLEDGE"
                    }))
                except Exception as e:
                    LOGGER.debug('err sending ACK: %s', e)
                    return self.communication_error_handler()
                m = message
            else:
                remaining_messages.append(message)
        self.incoming_messages = remaining_messages
        return m
    
    def recv_end(self):
        finished = False
        remaining_messages = []
        for message in self.incoming_messages:
            if message['method'] == "END_MATCH":
                victor = 'You' if (message['victor_id'] == self.player_id) else message['victor_id'][0:6]
                self.display.add_message(f"Game over. {victor} won!")
                finished = True
            else:
                # only get the user input messages from the queue
                remaining_messages.append(message)
        self.incoming_messages = remaining_messages

        return finished
    
    def send_input(self, tick):
        """Sends the current input state to the server, scheduled for the given tick."""
        msg = {
            "method": "USER_INPUT",
            "user_id": self.player_id,
            "input_state": self.input_state,
            "tick": self.engine.current_tick
        }
        self.send_msg(msg)

    def send_msg(self, message):
        """Formats a message (a dict) to be send to the server and adds
        it to the outgoing message queue."""
        LOGGER.debug('queueing message %s', message)
        self.outgoing_messages.append(helpers.marshal_message(message))

    def connect_server(self):
        """Connects to a server listening on the given host and port, and
        sets the socket property of this client."""
        try:
            LOGGER.debug('attempting to connnect to %s:%d...', self.server_host, self.server_port)
            self.socket = socket.create_connection((self.server_host, self.server_port))
        except ConnectionError as e:
            LOGGER.debug('Failed to connect to server: %s', e)
            return False
        return True

    def update_server(self):
        """Checks if packet has come in from the server, and add the 
        contents of the packet to the incoming queue if so. Additionally,
        checks if the server socket is ready for writing, in which case
        send a message from the outgoing queue.
        
        If the socket to the server is broken (fileno is -1), return False.
        Else, return True."""
        if self.socket.fileno() < 0:
            LOGGER.debug("server connection broken!")
            return False

        [readable, writable, x] = select.select([self.socket], [self.socket], [], 0)

        if self.socket in readable or PACKET_HEADER in helpers.INCOMING_BUFFER:
            try:
                packet = helpers.recv_packet(self.socket)
            except Exception as e:
                    LOGGER.debug('err receiving message to server: %s', e)
                    return self.communication_error_handler()
            LOGGER.debug('read packet from server: %s', packet)
            if packet:
                self.incoming_messages.append(helpers.unmarshal_message(packet))
    
        if self.socket in writable and self.outgoing_messages:
            LOGGER.debug('sending message to server')
            msg = self.outgoing_messages.pop(0)
            try:
                helpers.send_packet(self.socket, msg)
            except Exception as e:
                LOGGER.debug('err sending message to server: %s', e)
                return self.communication_error_handler()
        return True

    def advance_game(self):
        """Advances the game engine by a single tick."""
        self.engine.advance_tick()
    
    def update_scoreboard(self):
        """Updates the local scoreboard, noting any changes since the last check."""
        new_scores = self.engine.get_scores()
        for uid in new_scores:
            if uid not in self.scoreboard:
                self.scoreboard[uid] = new_scores[uid]
            if new_scores[uid] > self.scoreboard[uid]:
                LOGGER.debug('score increase: %s to %d', uid, new_scores[uid])
                player = "You" if uid == self.player_id else uid[0:6]
                increase = new_scores[uid] - self.scoreboard[uid]
                self.scoreboard[uid] = new_scores[uid]
                self.display.add_message(f"{player} got {increase} points! Score: {new_scores[uid]}")
    
    def join_game(self):
        """Attempts to join a game on the host server. If our socket isn't
        connected, return False without doing anything."""
        if self.socket is None or self.socket.fileno() < 0:
            return False
        self.send_msg({"method": "JOIN_MATCH"})

    def start_game(self, match_id):
        """Starts the local game engine."""
        self.engine.reset_game()
        self.engine.generate_pickup_locations(match_id)

    def check_join_game(self):
        """Determines if a game has been joined. If so, set player ID
        and reset the game state."""
        return self.recv_join()

    def communication_error_handler(self):
        """Handle a disconnect from server"""
        self.socket.close()
        return False

class GameServer:
    """Manages users joining/leaving matches, determines when matches begin and end,
    and relays inputs to and from players in a match."""

    def __init__(self, port=SERVER_PORT):
        self.engine = GameEngine()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("0.0.0.0", port))
        self.match_id = str(uuid.uuid4())
        self.user_inputs = []
        self.ready_users = []
        self.in_game = False
        self.user_sockets = {}

    def listen(self):
        """Listens for users on the specified host and port."""
        self.socket.listen()
        addr,port = self.socket.getsockname()
        print(f"Listening for users on {addr}:{port}...")
    
    def disconnect_user(self, user_id=0, user_socket=None):
        """If the user's socket is still open, close their connection and remove their
        socket from our dict of connections."""
        if user_id == 0 and user_socket is not None:
            user_id = self.get_uid_by_socket()
        if user_id in self.user_sockets:
            self.user_sockets[user_id].close()
            self.user_sockets.pop(user_id)
        if user_id in self.ready_users:
            self.ready_users.remove(user_id)
                
    def get_uid_by_socket(self, user_socket):
        """Returns the user id corresponding to the socket, if we have one. Else,
        return None."""
        for uid,sock in self.user_sockets.items():
            if sock == user_socket:
                return uid
        return None
    
    def wait_for_match(self):
        """Waits for enough users to connect and send JOIN_MATCH to begin the match. Returns
        True if we have enough players to start the match, False if something went wrong."""
        self.ready_users = []
        self.engine.reset_game()

        while len(self.ready_users) < MIN_PLAYERS:
            for uid in self.user_sockets:
                if not self.user_connected(uid):
                    LOGGER.debug('we have %d users and %d players', len(self.user_sockets), len(self.ready_users))
                    self.disconnect_user(uid)

            # server socket + user sockets
            all_sockets = [self.socket, *self.user_sockets.values()]
            # Check for readable sockets
            r_sockets, _w, _e = select.select(all_sockets, [], [], 1)
            while r_sockets:
                s = r_sockets.pop()
                if s == self.socket:
                    # If the socket is the server, then accept the connection
                    (conn, addr) = s.accept()
                    # and give them a user id
                    user_id = str(uuid.uuid4())
                    self.user_sockets[user_id] = conn
                    LOGGER.debug('we have %d users and %d players', len(self.user_sockets), len(self.ready_users))
                else:  # If the socket is a client
                    # get their user ID
                    user_id = self.get_uid_by_socket(s)

                    try:
                        packet = helpers.recv_packet(s)
                        if packet is None:
                            self.disconnect_user(user_id=user_id)
                            continue
                        request_data = helpers.unmarshal_message(packet)
                        if request_data['method'] != "JOIN_MATCH":
                            continue

                        try: # Handle request, expect JOIN_MATCH
                            helpers.send_packet(s, helpers.marshal_message({"method": "MATCH_JOINED", "user_id": user_id, "match_id": self.match_id}))
                            self.ready_users.append(user_id)
                            self.engine.add_user(user_id) # Add user to engine
                        except Exception as e:
                            LOGGER.debug('err responding to join_match: %s', e)
                            
                    except Exception as e: # If something with request goes wrong, remove from socket_dicts
                        LOGGER.debug('we have %d users and %d players', len(self.user_sockets), len(self.ready_users))
                        self.disconnect_user(user_id=user_id)
        
        return True

    def start_match(self):
        """Begin a game, initializing the local game state and telling all
        users when the match will begin."""
        # check if our player sockets are still valid
        invalid = False
        for user_id in self.ready_users:
            if self.user_sockets[user_id].fileno() < 0:
                self.user_sockets.pop(user_id)
                invalid = True
        if invalid:
            return False

        if len(self.ready_users) < MIN_PLAYERS:
            return False

        # set the starting positions, reset tick counter
        self.engine.place_players()
        self.engine.inputs = {}
        self.engine.current_tick = 0
        self.engine.register_state()

        # LOGGER.debug("starting match: users %s", self.user_sockets)
        # save the current state to send to users
        start_state = self.engine.serialize_current_state()

        message = helpers.marshal_message({
            "method": "START_MATCH",
            "start_in": MATCH_START_DELAY,
            "state": start_state,
        })
        # notify users of match start
        to_start = time.time()+MATCH_START_DELAY
        for user_id in dict(self.user_sockets): # copy dict before we iterate through it
            try:
                helpers.send_packet(self.user_sockets[user_id], message)
            except Exception as e:
                LOGGER.debug('err sending START_MATCH: %s', e)
                if user_id in self.user_sockets:
                    self.user_sockets.pop(user_id)
        while time.time() < to_start:
            pass

        # generate pickup positions
        self.engine.generate_pickup_locations(self.match_id)

        self.in_game = True
        return True

    def end_match(self):
        """End a game, telling all users who the victor is."""
        scores = self.engine.get_scores()
        victor_id = 0
        highest = -1
        for uid in scores:
            if scores[uid] > highest:
                highest = scores[uid]
                victor_id = uid

        packet = helpers.marshal_message({"method":"END_MATCH","victor_id": victor_id})
        while self.ready_users:
            sockets = [self.user_sockets[uid] for uid in self.ready_users]
            _r, writable, _x = select.select([], sockets, [])
            for sock in writable:
                uid = self.get_uid_by_socket(sock)
                try:
                    helpers.send_packet(sock, packet)
                except Exception as e:
                    LOGGER.debug('err with communicating end_match() : %s', e)
                    self.disconnect_user(user_id=uid)
                self.ready_users.remove(uid)
        self.in_game = False

    def check_inputs(self):
        """Checks each player in the match for input."""
        [readable, w, x] = select.select(self.user_sockets.values(), [], [], 0)
        while readable:
            user = readable.pop()
            try:
                packet = helpers.recv_packet(user)
                if packet is None:
                    del(self.user_sockets[user])
                    continue
                message = helpers.unmarshal_message(packet)
                if message['method'] != "USER_INPUT":
                    continue
                LOGGER.debug('msg: %s', message)
                self.engine.register_input(message['user_id'], message['input_state'], tick=message['tick'])
                if message['tick'] < self.engine.current_tick:
                    self.engine.rollback(message['tick'])
                self.user_inputs.append({
                    "user_id": message['user_id'],
                    "input_state": message['input_state'],
                    "tick": message['tick']
                })
            except OSError as e:
                LOGGER.debug('err relaying input: %s', e)
                self.remove_user(user)


    def relay_inputs(self):
        """Relays the given input to all other players
        in the match."""
        if self.user_inputs:
            packet = helpers.marshal_message({
                "method": "USER_INPUT",
                "inputs": list(self.user_inputs)
            })
            # TODO: only send inputs to users that didn't do them
            ids = [m['user_id'] for m in self.user_inputs]
            # LOGGER.debug('input packet: %s', packet)
            for user_id in self.user_sockets:
                try:
                    helpers.send_packet(self.user_sockets[user_id], packet)
                except OSError as e:
                    LOGGER.debug('err relaying input: %s', e)
                    self.remove_user(user_id=user_id)

            self.user_inputs = []

    def sync_clients(self):
        packet = helpers.marshal_message({
            "method": "GAME_STATE",
            "state": self.engine.serialize_current_state()
        })
        for user_id in dict(self.user_sockets):
            try:
                helpers.send_packet(self.user_sockets[user_id], packet)
            except OSError as e:
                LOGGER.debug('err relaying input: %s', e)
                self.remove_user(user_id=user_id)

    def match_finished(self):
        """Determines whether the current match is over or not."""
        # check whether we're over the match length time in ticks
        if self.engine.current_tick > (MATCH_LENGTH+MATCH_START_DELAY)*FRAMERATE:
            LOGGER.debug('reached match end, ending match')
            return True

    def advance_game(self):
        """Advance the game engine by one tick."""
        self.engine.advance_tick()

    def remove_user(self, user):
        """Remove user when disconnect happens"""
        LOGGER.debug('removing user: %s', self.user_sockets[user])
        temp_user = id(self.user_sockets[user])
        self.engine.remove_user(temp_user)
        del(self.user_sockets[user])
        
        # Idea is to relay to all users that a user has disconnected. Having some issues with id's and which ones to send
        '''
        # Communicate to rest of players that this user has disconnected
        message = helpers.marshal_message({
            "method": "REMOVE_PLAYER",
            "user": temp_user,
        })
        for player in self.user_sockets:
            try:
                helpers.send_packet(player, message)
            except Exception as e:
                LOGGER.debug('err sending REMOVE_PLAYER: %s', e)
                self.remove_user(player)'''

    def user_connected(self, user_id):
        """Returns whether the user represented by the given user ID has
        a socket that is not closed or in a failure state."""
        return (user_id in self.user_sockets) and (not self.user_sockets[user_id].fileno() < 0)

