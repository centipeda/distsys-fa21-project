"""Class definitions for entities/objects used in the game."""

from enum import Enum, auto
import pygame

from globalvars import *

class EntityKind(Enum):
    PLAYER = auto()
    PROJECTILE = auto()

class GameEntity:
    """Base class for game entities."""

    def __init__(self, kind, position=(0,0), velocity=(0,0), speed=0):
        self.position = position
        self.velocity = velocity
        self.speed = speed
        self.kind = kind

    def update_position(self):
        x,y = self.position
        xvel,yvel = self.velocity
        x += xvel
        y += yvel
        self.position = (x,y)

class Player(GameEntity):
    """Class for player entities."""

    def __init__(self, uid=0, position=(0,0), velocity=(0,0)):
        super().__init__("player", position=position, velocity=velocity, speed=PLAYER_SPEED)
        self.uid = uid
    
    def update_velocity(self, input_state):
        vel_x = 0
        vel_y = 0

        if input_state[pygame.K_w]: # up
            vel_y -= self.speed
        if input_state[pygame.K_s]: # down
            vel_y += self.speed
        if input_state[pygame.K_a]: # left
            vel_x -= self.speed
        if input_state[pygame.K_d]: # right
            vel_x += self.speed
        
        if vel_x != 0 and vel_y != 0:
            # multiply by sqrt(2) to adjust for diagonal
            vel_x *= (2**0.5) 
            vel_y *= (2**0.5) 
        
        self.velocity = (vel_x, vel_y)
        

