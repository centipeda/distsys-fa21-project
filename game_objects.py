"""Class definitions for entities/objects used in the game."""

from enum import Enum, auto
import pygame

from globalvars import *

class EntityKind(Enum):
    PLAYER = auto()
    PROJECTILE = auto()

class GameEntity:
    """Base class for game entities."""

    def __init__(self, kind, size, position=(0,0), velocity=(0,0), speed=0):
        self.position = position
        self.velocity = velocity
        self.speed = speed
        self.kind = kind
        self.size = size

    def update_position(self):
        """Updates position based on current velocity."""
        x,y = self.position
        xvel,yvel = self.velocity
        x += xvel
        y += yvel
        self.position = (x,y)
    
    def bound_position(self):
        """Returns the current position of the entity, adjusted to
        be within the bounds of the screen."""
        x,y = self.position
        if x-self.size < 0:
            x = self.size
        elif x+self.size > SCREEN_WIDTH:
            x = SCREEN_WIDTH-self.size
        if y-self.size < 0:
            y = self.size
        elif y+self.size > SCREEN_HEIGHT:
            y = SCREEN_HEIGHT-self.size
        return (x,y)
        

class Player(GameEntity):
    """Class for player entities."""

    def __init__(self, uid=0, position=(0,0), velocity=(0,0)):
        super().__init__(EntityKind.PLAYER, PLAYER_SIZE, position=position, velocity=velocity, speed=PLAYER_SPEED)
        self.uid = uid
        self.direction = self.get_normal_velocity()
    
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
            vel_x = int(vel_x/(2**0.5))
            vel_y = int(vel_y/(2**0.5))
        
        self.velocity = (vel_x, vel_y)
        if vel_x != 0 or vel_y != 0:
            self.direction = self.get_normal_velocity()
    
    def get_normal_velocity(self):
        x,y = self.velocity
        return (x/self.speed, y/self.speed)

    def shoot_projectile(self):
        dir_x, dir_y = self.direction
        if dir_x == 0 and dir_y == 0:
            return None
        proj_vel = (dir_x*PROJECTILE_SPEED, dir_y*PROJECTILE_SPEED)
        return Projectile(self.uid, self.position, proj_vel)
    
    def update_position(self):
        super().update_position()
        self.position = self.bound_position()
        
class Projectile(GameEntity):
    """Class for projectile entities."""

    def __init__(self, owner_uid, position, velocity):
        super().__init__(EntityKind.PROJECTILE, PROJECTILE_SIZE, position=position, velocity=velocity)
        self.owner_uid = owner_uid