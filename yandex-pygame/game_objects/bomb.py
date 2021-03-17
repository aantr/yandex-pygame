import pygame
from Box2D import *

from game_objects.explosion import Explosion
from game_objects.game_object import GameObject
from resources import Resources
from utils.utils import b2_coords, paint_images
from utils.b2_factory import B2Factory
from constants import *
import random


class Bomb(GameObject):
    layer = 0

    def __init__(self, world, cl, res: Resources, car, explosion_callback,
                 game_object_group, *groups):
        super().__init__(world, cl, game_object_group, *groups, connects=False)

        self.ignore_ray_casting = True
        radius = 26
        pos = car.get_position() + car.get_vector() * -50
        self.res = res
        image = res.image_bomb
        self.set_init_image(image)
        self.rect.center = pos
        self.explosion_callback = explosion_callback

        shape = b2CircleShape()
        shape.radius = radius / PPM
        fd = B2Factory.create_fixture(shape, 0.3, 0.1, 0.5)
        self.body = B2Factory.create_body(
            world, b2_dynamicBody, fd, b2_coords(pos) / PPM)
        self.body.userData = self
        self.body.linearDamping = 3
        impulse = 90
        self.body.ApplyTorque(random.randint(-impulse, impulse), True)
        self.timer = 0

    def update(self, dt: float, events):
        self.timer += dt
        if self.timer > 3:
            BombExplosion(self.world, self.cl, self.res,
                          b2_coords(self.body.position) * PPM,
                          self.game_object_group)
            self.explosion_callback()
            self.dispose()

    def render(self):
        self.set_rotated_sprite(self.body, self.init_image)

    def dispose(self):
        super().dispose()
        self.world.DestroyBody(self.body)


class BombExplosion(GameObject):
    layer = 0

    def __init__(self, world, cl, res: Resources, pos, game_object_group, *groups):
        super().__init__(world, cl, game_object_group, *groups)

        power = 2500
        radius = 500
        count_rays = 30
        Explosion.apply_impulses(world, pos, power, radius, count_rays, self)
        particles = paint_images(
            res.explosion_particles, lambda x: (0, 0, 0, x[3]))
        Explosion.spawn_particles(world, cl, res, pos, particles, 15, 10,
                                  self.game_object_group)
