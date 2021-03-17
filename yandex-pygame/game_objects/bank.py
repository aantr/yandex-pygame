import pygame
from Box2D import *

from constants import *
from game_objects.game_object import GameObject
from resources import Resources
from sprites.sprite import Group
from utils.b2_factory import B2Factory
from utils.contact_listener import ContactListener
from utils.utils import b2_coords


class Bank(GameObject):
    layer = 2

    def __init__(self, world: b2World, cl: ContactListener, res: Resources,
                 center, game_object_group: Group, *groups):
        super().__init__(world, cl, game_object_group, *groups)

        self.set_init_image(res.image_bank)
        self.rect.center = center

        render = res.font64.render('$  Банк  $', True, (0, 0, 0))
        self.image.blit(render, ((self.image.get_width() - render.get_width()) / 2, 230))

        shape = b2PolygonShape()
        shape.SetAsBox(*b2Vec2(self.rect.size) / 2 / PPM)
        fd = B2Factory.create_fixture(shape)
        self.body = B2Factory.create_body(self.world, b2_staticBody, fd, b2_coords(center) / PPM)
        self.body.userData = self

        LootArea(self.world, self.cl, center, self.game_object_group)


class LootArea(GameObject):
    layer = 1

    def __init__(self, world: b2World, cl: ContactListener, center,
                 game_object_group: Group, *groups):
        super().__init__(world, cl, game_object_group, *groups)
        radius = 400
        image = pygame.Surface((radius * 2, radius * 2)).convert_alpha()
        image.fill((0, 0, 0, 0))
        pygame.draw.circle(image, (100, 100, 100, 30), (radius, radius), radius)
        self.set_init_image(image)
        self.rect.center = center

        self.ignore_ray_casting = True
        self.draw_shadow = False
        shape = b2CircleShape()
        shape.radius = radius / PPM
        fd = B2Factory.create_fixture(shape, is_sensor=True)
        self.body = B2Factory.create_body(self.world, b2_staticBody, fd, b2_coords(center) / PPM)
        self.body.userData = self
