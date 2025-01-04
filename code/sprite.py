from random import randint
import pygame
from pygame.math import Vector2 as vector
from math import sin, cos, radians
from settings import *

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf = pygame.Surface((TILE_SIZE, TILE_SIZE)), groups = None, z = Z_LAYERS['main']):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)
        self.old_rect = self.rect.copy()
        self.z = z

class AnimatedSprite(Sprite):
    def __init__(self, pos, frames, groups, z = Z_LAYERS['main'], animathion_speed = ANIMATION_SPEED):
        self.frames, self.frame_index = frames, 0
        super().__init__(pos, self.frames[self.frame_index], groups, z)
        self.animathion_speed = animathion_speed

    def animate(self, dt):
        self.frame_index += self.animathion_speed * dt
        self.image = self.frames[int(self.frame_index % len(self.frames))]

    def update(self, dt):
        self.animate(dt)

class Item(AnimatedSprite):
    def __init__(self, item_type, pos, frames, groups, data):
        super().__init__(pos, frames, groups)
        self.rect.center=pos
        self.item_type = item_type
        self.data = data

    def activate(self):
        match self.item_type:
            case 'gold': self.data.coins += 5
            case 'silver': self.data.coins += 1
            case 'diamond': self.data.coins += 20
            case 'skull': self.data.coins += 50
            case 'potion': self.data.health += 1

class Cloud(Sprite):
    def __init__(self, pos, surf, groups, z=Z_LAYERS['clouds']):
        super().__init__(pos, surf, groups, z)
        self.speed = randint(50, 120)
        self.direction = -1
        self.rect.midbottom = pos

    def update(self, dt):
        self.rect.x += self.direction * self.speed * dt
        if self.rect.right <= 0:
            self.kill()

class Node(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, level, data, paths):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center=(pos[0]+TILE_SIZE/2, pos[1]+TILE_SIZE/2))
        self.z = Z_LAYERS['path']

        self.level = level
        self.data = data
        self.paths = paths
        self.grid_pos = (int(pos[0] / TILE_SIZE), int(pos[1] / TILE_SIZE))

    def can_move(self, direction):
        if direction in list(self.paths.keys()) and int(self.paths[direction][0][0]) <= self.data.unlocked_level:
            return True

class ParticleEffectSprite(AnimatedSprite):
    def __init__(self, pos, frames, groups):
        super().__init__(pos, frames, groups)
        self.rect.center = pos
        self.z = Z_LAYERS['fg']

    def animate(self, dt):
        self.frame_index += self.animathion_speed *dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

class MovingSprite(AnimatedSprite):
    def __init__(self, frames, groups, start_pos, end_pos, move_dir, speed, flip):
        super().__init__(start_pos, frames, groups)
        self.rect.center = start_pos
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.moving = True

        self.speed = speed
        self.direction = vector(1, 0) if move_dir == 'x' else vector (0, 1)
        self.move_dir = move_dir

        self.flip = flip
        self.reverse = {'x': False, 'y': False}

    def check_border(self):
        if self.move_dir == 'x':
            if self.rect.right >= self.end_pos[0] and self.direction.x == 1:
                self.direction.x = -1
                self.rect.right = self.end_pos[0]
            if self.rect.centerx <= self.start_pos[0] and self.direction.x == -1:
                self.direction.x = 1
                self.rect.centerx = self.start_pos[0]
            self.reverse['x'] = True if self.direction.x < 0 else False
        else:
            if self.rect.bottom >= self.end_pos[1] and self.direction.y == 1:
                self.direction.y = -1
                self.rect.bottom = self.end_pos[1]
            if self.rect.centery <= self.start_pos[1] and self.direction.y == -1:
                self.direction.y = 1
                self.rect.centery = self.start_pos[1]
            self.reverse['y'] = True if self.direction.y > 0 else False

    def update(self, dt):
        self.old_rect = self.rect.copy()
        self.rect.topleft += self.direction * self.speed * dt
        self.check_border()
        self.animate(dt)

        if self.flip:
            self.image = pygame.transform.flip(self.image, self.reverse['x'], self.reverse['y'] )

class Spike(Sprite):
    def __init__(self, pos, surf, groups, radius, speed, start_angle, end_angle, z=Z_LAYERS['main']):
        self.center = pos
        self.speed = speed
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.radius = radius
        self.angle = self.start_angle
        self.direction = 1
        self.full_circle = True if self.end_angle == -1 else False

        x= self.center[0] + cos(radians(self.angle)) * self.radius
        y= self.center[1] + sin(radians(self.angle)) * self.radius

        super().__init__((x, y), surf, groups, z)

    def update(self, dt):
        self.angle += self.direction * self.speed * dt
        if not self.full_circle:
            if self.angle >= self.end_angle:
                self.direction = -1
            if self.angle <= self.start_angle:
                self.direction = 1
        x = self.center[0] + cos(radians(self.angle)) * self.radius
        y = self.center[1] + sin(radians(self.angle)) * self.radius
        self.rect.center = (x,y)

class Icon(pygame.sprite.Sprite):
    def __init__(self, pos, groups, frames):
        super().__init__(groups)
        self.icon = True
        self.path = None
        self.direction = vector(0,0)
        self.speed = 400

        self.frames, self.frame_index = frames, 0
        self.state = 'idle'
        self.image = self.frames[self.state][self.frame_index]
        self.z = Z_LAYERS['main']

        self.rect = self.image.get_frect(center=pos)

    def start_move(self, path):
        self.rect.center = path[0]
        self.path = path[1:]
        self.find_path()

    def find_path(self):
        if self.path:
            if self.rect.centerx == self.path[0][0]:
                self.direction = vector(0, 1 if self.path[0][1]>self.rect.centery else -1)
            else:
                self.direction = vector(1 if self.path[0][0] > self.rect.centerx else -1, 0)
        else:
            self.direction = vector(0,0)

    def point_collision(self):
        if self.direction.y == 1 and self.rect.centery >= self.path[0][1] or \
                self.direction.y == -1 and self.rect.centery <= self.path[0][1]:
            self.rect.centery = self.path[0][1]
            del self.path[0]
            self.find_path()

        if self.direction.x == 1 and self.rect.centerx >= self.path[0][0] or \
                self.direction.x == -1 and self.rect.centerx <= self.path[0][0]:
            self.rect.centerx = self.path[0][0]
            del self.path[0]
            self.find_path()

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]

    def get_state(self):
        self.state = 'idle'
        if self.direction == vector(1, 0):  self.state = 'right'
        if self.direction == vector(-1, 0): self.state = 'left'
        if self.direction == vector(0, 1):  self.state = 'down'
        if self.direction == vector(0, -1): self.state = 'up'

    def update(self, dt):
        if self.path:
            self.point_collision()
            self.rect.center += self.direction * self.speed * dt
        self.get_state()
        self.animate(dt)

class PathSprite(Sprite):
	def __init__(self, pos, surf, groups, level):
		super().__init__(pos, surf, groups, Z_LAYERS['path'])
		self.level = level