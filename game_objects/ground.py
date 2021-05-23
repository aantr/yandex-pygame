import math

import pygame
from Box2D import *

from game_objects.game_object import GameObject
from resources import Resources
from utils.utils import b2_coords
from utils.b2_factory import B2Factory
from configurations import *


class Ground(GameObject):
    layer = -1

    def __init__(self, world, cl, res: Resources,
                 rect: pygame.Rect, friction_modifier,
                 game_object_group, *groups):
        super().__init__(world, cl, game_object_group, *groups)

        self.friction_modifier = friction_modifier
        self.ignore_ray_casting = True
        self.draw_shadow = False

        rect = pygame.Rect(rect)
        image = pygame.transform.scale(res.image_ground, rect.size)
        self.set_init_image(image)
        self.rect = pygame.Rect(rect.topleft, image.get_size())

        shape = b2PolygonShape()
        shape.SetAsBox(*b2Vec2(*rect.size) / 2 / PPM)
        fd1 = B2Factory.create_fixture(shape, 0, is_sensor=True)

        self.body = B2Factory.create_body(world, b2_staticBody, fd1, b2_coords(rect.center) / PPM)
        self.body.userData = self

        self.set_rotated_sprite(self.body, self.get_init_image())

    def dispose(self):
        super().dispose()
        self.world.DestroyBody(self.body)
