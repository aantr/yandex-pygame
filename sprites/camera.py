import random

import pygame

from configurations import *
from game_objects.game_object import GameObject
from sprites.sprite import Group, Sprite
from utils.utils import b2_coords


class Camera:
    def __init__(self, group: Group, restriction=None):
        super().__init__()
        self.camera_shift = pygame.Vector2(0, 0)
        self.restriction = restriction

        self.group = group

        self.speed = 10
        self.chase_shift_speed = 0.05
        self.shift = pygame.Vector2()

        # Тряска камеры
        self.duration = 100
        self.frequency = 100
        self.amplitude = 3000
        self.sample_count = self.duration * self.frequency
        self.samples = [random.uniform(0, 1) * 2 - 1 for _ in range(self.sample_count)]
        self.shake_timer = 0
        self.shake_duration = 0

    def shake(self, duration, amplitude):
        self.shake_duration = duration
        self.amplitude = amplitude

    def get_camera_shift_car(self, car):
        velocity = car.get_velocity()
        min_velocity_length = car.max_forward_speed / 3 * PPM
        if velocity.length < min_velocity_length:
            return 0, 0
        velocity = velocity / 5 + car.get_vector() * 75
        return velocity

    def chase_sprite(self, sprite, dt, shift=pygame.Vector2()):
        self.shift += (shift - self.shift) * self.chase_shift_speed
        x = sprite.rect.center[0] - WIDTH / 2
        y = sprite.rect.center[1] - HEIGHT / 2
        self.camera_shift += (pygame.Vector2(x, y) -
                              self.camera_shift + self.shift) * dt * self.speed

        # Position restrictions
        if self.restriction:
            self.camera_shift.x = -max(-(self.restriction[2] - WIDTH),
                                       min(0, -self.camera_shift.x))
            self.camera_shift.y = -max(-(self.restriction[3] - HEIGHT),
                                       min(0, -self.camera_shift.y))

    def set_position(self, pos):
        self.camera_shift = pygame.Vector2(*pos) - pygame.Vector2(WIDTH, HEIGHT) / 2

    def get_position(self):
        return self.camera_shift + pygame.Vector2(WIDTH, HEIGHT) / 2

    def update(self, dt, events):
        self.group.update(dt, events)
        # Тряска
        self.shake_timer += dt
        if self.shake_timer > self.duration:
            self.shake_timer -= self.duration
        if self.shake_duration > 0:
            self.shake_duration -= dt
            time = self.shake_timer * self.frequency
            first = int(time)
            second = (first + 1) % self.sample_count
            third = (first + 2) % self.sample_count
            delta_t = time - int(time)
            delta_x = self.samples[first] * delta_t + self.samples[second] * (1 - delta_t)
            delta_x *= self.amplitude * min(self.shake_duration, 1)
            delta_y = self.samples[second] * delta_t + self.samples[third] * (1 - delta_t)
            delta_y *= self.amplitude * min(self.shake_duration, 1)

            self.camera_shift += pygame.Vector2(delta_x, delta_y)

    def draw_shadow(self, spr, surface_blit):
        surface_blit(spr.shadow, spr.shadow_rect.move(
            spr.shadow_shift - self.camera_shift))

    def draw_sprite(self, spr, surface_blit, spritedict, dirty_append, init_rect):
        shifted_rect = spr.rect.move(-1 * self.camera_shift)
        newrect = surface_blit(spr.image, shifted_rect)
        rec = spritedict[spr]
        if rec is init_rect:
            dirty_append(newrect)
        else:
            if newrect.colliderect(rec):
                dirty_append(newrect.union(rec))
            else:
                dirty_append(newrect)
                dirty_append(rec)
        spritedict[spr] = newrect

    def draw(self, surface):
        """The code was rewritten from the base pygame.sprite.Sprite class"""

        # Call render function in GameSprite
        self.group.render_sprites()

        # Draw with camera shift
        spritedict = self.group.spritedict
        surface_blit = surface.blit
        dirty = self.group.lostsprites
        self.group.lostsprites = []
        dirty_append = dirty.append
        init_rect = self.group._init_rect

        # Draw shadows in bottom layer
        for spr in self.group.get_sprites_from_layer(-1):
            spr: GameObject
            if spr.draw_shadow:
                self.draw_shadow(spr, surface_blit)
        # Draw sprite in bottom layer and move in opposite side
        for spr in self.group.get_sprites_from_layer(-1):
            spr: Sprite
            self.draw_sprite(spr, surface_blit, spritedict,
                             dirty_append, init_rect)
        # Draw shadows
        for spr in self.group.sprites():
            spr: GameObject
            if spr.layer == -1:
                continue
            if spr.draw_shadow:
                self.draw_shadow(spr, surface_blit)
        # Draw sprite and move in opposite side
        for spr in self.group.sprites():
            spr: Sprite
            if spr.layer == -1:
                continue
            self.draw_sprite(spr, surface_blit, spritedict,
                             dirty_append, init_rect)

        return dirty
