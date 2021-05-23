import math

import pygame
from Box2D import *

from configurations import *
from game_objects.car import Car
from game_objects.explosion import Explosion
from game_objects.game_object import GameObject
from game_objects.tire import Tire
from resources import Resources
from utils.b2_factory import B2Factory
from utils.utils import b2_coords, paint_images, get_data


class Bullet(GameObject):
    layer = 1

    def __init__(self, world, cl, res: Resources, pos, vector,
                 game_object_group, *groups):
        super().__init__(world, cl, game_object_group, *groups)

        self.draw_shadow = False
        self.ignore_ray_casting = True
        self.set_init_image(paint_images([res.image_bullet], lambda x: (120, 0, 200, x[3]))[0])
        self.vector = pygame.Vector2(vector).normalize()
        pos = pygame.Vector2(pos) + self.vector * 100
        self.rect.center = pos
        self.res = res

        self.impulse = 2.5
        radius = 12
        shape = b2CircleShape()
        shape.radius = radius / PPM
        fd = B2Factory.create_fixture(shape, 0.3, 0, 1)
        self.body = B2Factory.create_body(
            world, b2_dynamicBody, fd, b2_coords(pos) / PPM)
        self.body.userData = self
        self.body.fixedRotation = True
        self.body.ApplyLinearImpulse(b2_coords(self.vector) * self.impulse, self.body.GetWorldPoint((0, 0)), True)

        self.timer = 0
        self.timeout = 3
        self.collide = False

    def update(self, dt: float, events):
        self.timer += dt
        if self.timer > self.timeout or self.collide:
            self.explode()

    def render(self):
        self.set_rotated_sprite(self.body, self.init_image)

    def begin_contact(self, contact: b2Contact):
        if self.collide:
            return
        data_a, data_b = get_data(contact)
        if isinstance(data_a, Car) or isinstance(data_a, Tire):
            self.collide = True
            data_a.on_explosion(self, 0)
        elif isinstance(data_b, Car) or isinstance(data_b, Tire):
            self.collide = True
            data_b.on_explosion(self, 0)

    def explode(self):
        particles = paint_images(
            self.res.explosion_particles, lambda x: (10, 90, 10, x[3]))
        Explosion.spawn_particles(self.world, self.cl, self.res,
                                  b2_coords(self.body.position) * PPM, particles, 15, 5,
                                  self.game_object_group, timeout=1)
        self.dispose()

    def dispose(self):
        super().dispose()
        self.world.DestroyBody(self.body)
