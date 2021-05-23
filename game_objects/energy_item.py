import math

import pygame
from Box2D import *

from game_objects.game_object import GameObject
from resources import Resources
from utils.utils import b2_coords
from utils.b2_factory import B2Factory
from configurations import *


class EnergyItem(GameObject):
    def __init__(self, world, cl, res: Resources,
                 pos, game_object_group, *groups):
        super().__init__(world, cl, game_object_group, *groups)

        self.ignore_ray_casting = True
        self.set_init_image(res.energy_item)
        self.rect.center = pos

        shape = b2CircleShape()
        shape.radius = self.image.get_width() / 2 / PPM
        fd1 = B2Factory.create_fixture(shape, 0.2, 0.2, 0.2, True)

        self.body = B2Factory.create_body(world, b2_dynamicBody, fd1, b2_coords(pos) / PPM)
        self.body.userData = self
        self.body.fixedRotation = True

        self.timer = 0
        self.timeout = 0.5
        self.is_collecting = False

    def collect(self):
        res = not self.is_collecting
        self.is_collecting = True
        return res

    def update(self, dt: float, events):
        if self.is_collecting:
            self.timer += dt
            if self.timer >= self.timeout:
                self.dispose()

    def render(self):
        self.set_rotated_sprite(self.body, self.init_image)
        alpha = (1 - self.timer / self.timeout) * 255
        self.image.set_alpha(alpha)
        self.shadow.set_alpha(alpha)

    def dispose(self):
        super().dispose()
        self.world.DestroyBody(self.body)
