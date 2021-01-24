import math

import pygame
from Box2D import *

from game_objects.game_object import GameObject
from resources import Resources
from utils.utils import b2_coords
from utils.b2_factory import B2Factory
from constants import *


class Line(GameObject):
    layer = 0

    def __init__(self, world, cl, res: Resources,
                 point1, point2, game_object_group, *groups):
        super().__init__(world, cl, game_object_group, *groups, connects=False)

        self.draw_shadow = False
        self.ignore_ray_casting = True

        width = 10
        point1, point2 = sorted([point1, point2], key=lambda x: x[1])
        size = (width, pygame.Vector2(point1).distance_to(point2) + width * 1)
        center = (pygame.Vector2(point1) + pygame.Vector2(point2)) / 2
        sin = (point2[0] - point1[0]) / (size[1] - width * 1)
        angle = math.asin(sin)
        image = pygame.transform.scale(res.image_wall, tuple(map(int, size)))

        self.start = point1
        self.end = point2
        self.set_init_image(image)
        self.rect.center = center

        shape = b2PolygonShape()
        shape.SetAsBox(*b2Vec2(size) / 2 / PPM)
        fd1 = B2Factory.create_fixture(shape, 2, 0.1, 0.5, True)

        self.body = B2Factory.create_body(world, b2_staticBody, fd1, b2_coords(center) / PPM)
        self.body.userData = self
        self.body.angle = angle

        self.set_rotated_sprite(self.body, self.get_init_image())

    def dispose(self):
        super().dispose()
        self.world.DestroyBody(self.body)
