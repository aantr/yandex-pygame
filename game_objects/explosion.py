import random
from collections import defaultdict

import pygame
from Box2D import *

from constants import *
from game_objects.game_object import GameObject
from resources import Resources
from utils.utils import b2_coords
from utils.b2_factory import B2Factory
from utils.ray_cast_callback import RayCastCallback


class Explosion:
    @staticmethod
    def apply_impulses(world, pos, power, radius, count_rays, obj_from, damage_me=True):
        rays = []
        direction = pygame.Vector2(1, 0)
        rotate_angle = 360 / count_rays
        for i in range(count_rays):
            start_point = b2_coords(pos) / PPM
            end_point = b2_coords(direction * radius) / PPM + start_point
            ray = RayCastCallback(start_point, end_point)
            world.RayCast(ray, start_point, end_point)
            rays.append(ray)
            direction = direction.rotate(rotate_angle)

        exploded_objects = defaultdict(int)
        for i in rays:
            if not i.reports:
                continue
            last_report = i.reports[-1]
            impulse: b2Vec2 = i.end - last_report.point
            impulse.Normalize()
            impulse = impulse * power / count_rays * max(last_report.fraction + 0.5, 1)
            body: b2Body = last_report.fixture.body
            if damage_me is not True and isinstance(body.userData, damage_me):
                continue
            body.ApplyLinearImpulse(impulse, body.GetWorldPoint((0, 0)), True)
            if isinstance(body.userData, GameObject):
                exploded_objects[body.userData] += impulse.length
        for obj, power in exploded_objects.items():
            obj: GameObject
            obj.on_explosion(obj_from, power)

    @staticmethod
    def spawn_particles(world, cl, res, pos, particles, impulse,
                        count, game_object_group, timeout=2):
        direction = pygame.Vector2(1, 0)
        rotate_angle = 360 / count
        for i in range(count):
            impulse_direction = direction.rotate(random.uniform(-20, 20)) \
                                * impulse * random.uniform(0.5, 1.5)
            piece = ExplosionParticle(world, cl, res, pos + direction * 20,
                                      particles, impulse_direction,
                                      timeout, game_object_group)
            direction = direction.rotate(rotate_angle)


class ExplosionParticle(GameObject):
    layer = 0

    def __init__(self, world, cl, res: Resources, pos, images, vector, timeout,
                 game_object_group, *groups):
        super().__init__(world, cl, game_object_group, *groups)

        self.ignore_ray_casting = True
        self.draw_shadow = False

        self.set_init_image(random.choice(images))
        self.rect.center = pos

        shape = b2CircleShape()
        shape.radius = self.image.get_size()[0] / 2 / PPM
        fd = B2Factory.create_fixture(shape, 0.1, 0.1, 0.5)
        self.body = B2Factory.create_body(
            world, b2_dynamicBody, fd, b2_coords(pos) / PPM)
        self.body.userData = self
        self.body.linearDamping = 1
        self.body.fixedRotation = True
        self.body.ApplyLinearImpulse(b2_coords(vector) / PPM,
                                     self.body.GetWorldPoint((0, 0)), True)

        self.timer = 0
        self.timeout = timeout

    def update(self, dt: float, events):
        self.timer += dt
        if self.timer > self.timeout:
            self.dispose()

    def render(self):
        self.image.set_alpha((self.timeout - self.timer) / self.timeout * 255)
        self.rect.center = b2_coords(self.body.position) * PPM

    def dispose(self):
        super().dispose()
        self.world.DestroyBody(self.body)
