import math
import pygame
from Box2D import *

from game_objects.game_object import GameObject
from game_objects.turret.bullet import Bullet
from resources import Resources
from utils.b2_factory import B2Factory
from utils.utils import b2_coords
from configurations import *


class Turret(GameObject):
    layer = 2

    def __init__(self, world, cl, res: Resources, pos,
                 game_object_group, *groups):
        super().__init__(world, cl, game_object_group, *groups)
        self.set_init_image(res.image_turret)
        self.rect.center = pos
        self.res = res
        self.force = 10 ** 4
        self.base = TurretBase(self.world, self.cl, self.res, pos, self.game_object_group)

        radius = 40
        shape = b2CircleShape()
        shape.radius = radius / PPM
        fd = B2Factory.create_fixture(shape, 1, 0.1, 0.2)
        self.body = B2Factory.create_body(
            world, b2_dynamicBody, fd, b2_coords(pos) / PPM)
        shape = b2PolygonShape()
        shape.SetAsBox(28 / 2 / PPM, 81 / 2 / PPM, (0, 81 / 2 / PPM), 0)
        fd = B2Factory.create_fixture(shape, 1, 0.1, 0.2)
        self.body.CreateFixture(fd)
        self.body.userData = self
        self.body.angularDamping = 3

        shape = b2PolygonShape()
        shape.SetAsBox(*b2Vec2(10, 10) / 4 / PPM)
        fd = B2Factory.create_fixture(shape)
        self.center_body = B2Factory.create_body(
            world, b2_staticBody, fd, b2_coords(pos) / PPM)
        jd = b2RevoluteJointDef()
        jd.bodyA = self.body
        jd.bodyB = self.center_body
        self.world.CreateJoint(jd)

        self.shot_timer = 0
        self.shot_timeout = 1

    def update(self, dt: float, events):
        self.body.ApplyTorque(dt * self.force, True)
        self.shot_timer += dt
        if self.shot_timer >= self.shot_timeout:
            self.shot_timer = 0
            self.shot()

    def get_angle(self):
        return math.degrees(self.body.angle)

    def get_vector(self):
        angle = math.radians(self.get_angle())
        return pygame.Vector2(math.sin(angle), math.cos(angle)) * -1

    def shot(self):
        Bullet(self.world, self.cl, self.res, b2_coords(self.body.position) * PPM,
               self.get_vector(), self.game_object_group)

    def render(self):
        self.set_rotated_sprite(self.body, self.init_image)

    def dispose(self):
        self.world.DestroyBody(self.body)
        self.world.DestroyBody(self.center_body)


class TurretBase(GameObject):
    layer = 0

    def __init__(self, world, cl, res: Resources, pos,
                 game_object_group, *groups):
        super().__init__(world, cl, game_object_group, *groups)
        self.set_init_image(res.image_turret_base)
        self.rect.center = pos
