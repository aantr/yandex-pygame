import math
import pygame
from Box2D import *

from constants import *
from sprites.sprite import Sprite, Group
from utils.utils import b2_coords, paint_images
from utils.contact_listener import ContactListener


class GameObject(Sprite):
    def __init__(self, world: b2World, cl: ContactListener,
                 game_object_group: Group, *groups, connects=True):
        super().__init__()
        self.world = world
        self.cl = cl
        self.game_object_group = game_object_group
        game_object_group.add(self, layer=self.layer)
        self.groups = groups
        for i in groups:
            i: Group
            i.add(self, layer=self.layer)

        self.ignore_ray_casting = False
        self.draw_shadow = True

        # Box2D body collides
        if connects:
            self.cl.connect_begin_contact(self)
            self.cl.connect_end_contact(self)
            self.cl.connect_pre_solve(self)
            self.cl.connect_post_solve(self)

        # Shadow image
        self.init_shadow = pygame.Surface((0, 0))
        self.shadow = self.init_shadow.copy()
        self.shadow_shift = pygame.Vector2(10, 10)
        self.shadow_color = 150, 150, 150, 255

    def update(self, dt: float, events):
        ...

    def render(self):
        ...

    def dispose(self):
        # Надо очичтить используемые объекты, чтобы весь объект
        # выгрузмлся из памяти, т.к. есть существуют ссылка на GameObject
        super().dispose()
        self.game_object_group.remove(self)
        for i in self.groups:
            i.remove(self)
        del self.cl
        del self.shadow
        del self.init_shadow

    def begin_contact(self, contact: b2Contact):
        ...

    def end_contact(self, contact: b2Contact):
        ...

    def pre_solve(self, contact: b2Contact, old_manifold: b2Manifold):
        ...

    def post_solve(self, contact: b2Contact, impulse: b2ContactImpulse):
        ...

    def on_explosion(self, obj_from, power):
        ...

    def set_rotated_sprite(self, body: b2Body, image):
        """Rotates sprite image and shadow from b2Body"""

        # Base image
        angle = math.degrees(body.angle)
        self.rect.center = b2_coords(body.position) * PPM
        new_rect, rotated_im = self.rotate_image_center(
            self.rect, angle, image)
        self.image = rotated_im
        self.rect = new_rect

        # Shadow image
        if self.draw_shadow:
            _, rotated_im = self.rotate_image_center(
                self.rect, angle, self.init_shadow)
            self.shadow = rotated_im

    def set_init_image(self, image: pygame.Surface):
        super().set_init_image(image)
        if self.draw_shadow:
            self.init_shadow = self.process_image_to_shadow(image, self.shadow_color)
            self.shadow = self.init_shadow

    @staticmethod
    def process_image_to_shadow(image: pygame.Surface, color):
        """Makes image black like shadow with alpha"""
        res = paint_images([image], lambda x: (*color[:3], color[3] * x[3] // 255))[0]
        return res
