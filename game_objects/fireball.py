import math

import pygame
from Box2D import *

from game_objects.explosion import Explosion
from game_objects.game_object import GameObject
from resources import Resources
from sprites.animation import Animation
from utils.utils import b2_coords, get_data
from utils.b2_factory import B2Factory
from constants import *


class Fireball(GameObject):
    layer = 1

    def __init__(self, world, cl, res: Resources, car, vector, explosion_callback,
                 game_object_group, *groups):
        super().__init__(world, cl, game_object_group, *groups)

        self.draw_shadow = False
        self.ignore_ray_casting = True
        self.animation = Animation(res.animation_fireball, 6, 20)
        self.image = self.animation.get_frame()
        self.vector = pygame.Vector2(vector).normalize()
        pos = car.get_position() + self.vector * 10
        self.rect = pygame.Rect(0, 0, *self.image.get_size())
        self.rect.center = pos
        self.res = res
        self.car = car
        self.callback = explosion_callback

        self.impulse = 5
        self.force = 15
        radius = 20
        shift = 40, 0

        shape = b2CircleShape()
        shape.radius = radius / PPM
        shape.pos = b2Vec2(shift) / PPM
        fd = B2Factory.create_fixture(shape, 0.3, 0.1, 0.5)
        self.body = B2Factory.create_body(
            world, b2_dynamicBody, fd, b2_coords(pos) / PPM)
        self.body.userData = self
        self.body.angle = math.radians(pygame.Vector2(self.vector).angle_to((1, 0)))
        self.body.fixedRotation = True
        self.body.linearDamping = 0.3
        self.body.ApplyLinearImpulse(b2_coords(self.vector) * self.impulse,
                                     self.body.GetWorldPoint((0, 0)), True)

        self.timer = 0
        self.collide = False

    def begin_contact(self, contact: b2Contact):
        data_a, data_b = get_data(contact)
        if data_a != self.car and data_b != self.car and \
                data_a not in self.car.tires and data_b not in self.car.tires and \
                isinstance(data_a, GameObject) and isinstance(data_b, GameObject) and \
                (not data_a.ignore_ray_casting or not data_b.ignore_ray_casting):
            self.collide = True

    def update(self, dt: float, events):
        self.animation.update(dt)
        self.timer += dt
        if self.timer > 1.5 or self.collide:
            self.explode()
        self.body.ApplyForce(b2_coords(self.vector) * self.force,
                             self.body.GetWorldPoint((0, 0)), True)

    def render(self):
        self.set_rotated_sprite(self.body, self.animation.get_frame())

    def explode(self):
        FireballExplosion(self.world, self.cl, self.res,
                          b2_coords(self.body.GetWorldPoint(
                              self.body.fixtures[0].shape.pos)) * PPM,
                          self.game_object_group)
        self.callback()
        self.dispose()

    def dispose(self):
        super().dispose()
        self.world.DestroyBody(self.body)


class FireballExplosion(GameObject):
    layer = 3

    def __init__(self, world, cl, res: Resources, pos, game_object_group, *groups):
        super().__init__(world, cl, game_object_group, *groups)

        self.draw_shadow = False
        self.ignore_ray_casting = True
        self.animation = Animation(res.animation_fireball_explosion, 6, 15)
        self.image = self.animation.get_frame()
        self.rect = pygame.Rect(0, 0, *self.image.get_size())
        self.rect.center = pos
        self.res = res

        power = 750
        radius = 150
        count_rays = 20
        Explosion.apply_impulses(world, pos, power, radius, count_rays, self)

    def update(self, dt: float, events):
        self.animation.update(dt)
        if self.animation.is_first_loop_passed():
            self.dispose()

    def render(self):
        self.image = self.animation.get_frame()
