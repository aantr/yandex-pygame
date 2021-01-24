import math

import pygame
from Box2D import *

from game_objects.game_object import GameObject
from utils.utils import b2_coords
from utils.b2_factory import B2Factory
from constants import *


class BaseWall(GameObject):
    layer = 3

    # Ищем равные по углу и длине стены и экономим память
    images = {}

    def __init__(self, world, cl, image, width,
                 density, friction, restitution, body_type, point1, point2,
                 game_object_group, *groups):
        super().__init__(world, cl, game_object_group, *groups, connects=False)

        point1, point2 = sorted([point1, point2], key=lambda x: x[1])
        size = (width, pygame.Vector2(point1).distance_to(point2))
        self.sin = (point2[0] - point1[0]) / size[1]
        angle = math.asin(self.sin)
        self.size = tuple(map(int, size))
        self.center = (pygame.Vector2(point1) + pygame.Vector2(point2)) / 2
        self.image_stick = pygame.transform.scale(image, self.size).convert_alpha()
        self.width = width
        self.start = point1
        self.end = point2

        # Скругления
        shape = b2PolygonShape()
        shape.SetAsBox(*b2Vec2(size) / 2 / PPM)
        fd1 = B2Factory.create_fixture(shape, density, friction, restitution)
        self.body = B2Factory.create_body(world, body_type, fd1, b2_coords(self.center) / PPM)
        shape = b2CircleShape()
        shape.radius = width / 2 / PPM
        shape.pos = 0, size[1] / 2 / PPM
        fd2 = B2Factory.create_fixture(shape, density, friction, restitution)
        shape = b2CircleShape()
        shape.radius = width / 2 / PPM
        shape.pos = 0, -size[1] / 2 / PPM
        fd3 = B2Factory.create_fixture(shape, density, friction, restitution)
        self.body.CreateFixture(fd2)
        self.body.CreateFixture(fd3)

        self.body.userData = self
        self.body.angle = angle

    def create_image(self):
        # Изображение со скругленными углами
        width, size, sin = self.width, self.size, self.sin
        image = pygame.Surface((size[0], size[1] + width)).convert_alpha()
        image.fill((0, 0, 0, 0))
        image.blit(self.image_stick, (0, width / 2))
        for pos in [(width / 2, width / 2), (width / 2, size[1] + width / 2)]:
            pygame.draw.circle(image, image.get_at(
                tuple(map(lambda x: int(x / 2), image.get_size()))), pos, width / 2)
        self.set_init_image(image)
        self.set_rotated_sprite(self.body, self.get_init_image())
        self.images[(type(self), size, sin)] = self.image, self.shadow, self.rect
        self.rect.center = self.center

    def dispose(self):
        super().dispose()
        self.world.DestroyBody(self.body)
