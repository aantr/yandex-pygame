import math
import pygame
from Box2D import *

from configurations import *
from game_objects.game_object import GameObject
from game_objects.player_car.player_car import PlayerCar
from resources import Resources
from sprites.sprite import Group
from utils.b2_factory import B2Factory
from utils.contact_listener import ContactListener
from utils.utils import get_data, b2_coords


class ConversationBarrier(GameObject):
    def __init__(self, world: b2World, cl: ContactListener, res: Resources, start, end,
                 game_object_group: Group, *groups):
        super().__init__(world, cl, game_object_group, *groups)

        self.ignore_ray_casting = True
        self.draw_shadow = False
        width = 24
        point1, point2 = sorted([start, end], key=lambda x: x[1])
        size = (width, pygame.Vector2(point1).distance_to(point2))
        sin = (point2[0] - point1[0]) / size[1]
        angle = math.asin(sin)
        size = tuple(map(int, size))
        center = (pygame.Vector2(point1) + pygame.Vector2(point2)) / 2

        shape = b2PolygonShape()
        shape.SetAsBox(*b2Vec2(size) / 2 / PPM, (0, 0), angle)
        fd = B2Factory.create_fixture(shape, is_sensor=True)
        self.body = B2Factory.create_body(self.world, b2_staticBody, fd, b2_coords(center) / PPM)
        self.body.userData = self

        self.collided = False

    def begin_contact(self, contact: b2Contact):
        data_a, data_b = get_data(contact)
        if type(data_a) == PlayerCar or type(data_b) == PlayerCar:
            self.collided = True

    def dispose(self):
        super().dispose()
        self.world.DestroyBody(self.body)
