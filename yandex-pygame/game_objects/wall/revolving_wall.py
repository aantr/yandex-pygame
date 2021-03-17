import math

import pygame
from Box2D import *

from game_objects.wall.base_wall import BaseWall
from resources import Resources
from utils.utils import b2_coords
from utils.b2_factory import B2Factory
from constants import *


class RevolvingWall(BaseWall):
    def __init__(self, world, cl, res: Resources,
                 center, radius, angle, speed, game_object_group, *groups):
        super().__init__(world, cl, res.image_revolving_wall,
                         28, 10, 0.1, 0.5, b2_dynamicBody,
                         (center[0] - radius, center[1]),
                         (center[0] + radius, center[1]), game_object_group, *groups)

        self.torque = speed
        self.body.angle = math.radians(angle)
        self.body.linearDamping = 1
        self.body.angularDamping = 1

        shape = b2PolygonShape()
        shape.SetAsBox(*b2Vec2(24, 24) / 4 / PPM)
        fd = B2Factory.create_fixture(shape)
        self.center_body = B2Factory.create_body(
            world, b2_staticBody, fd, b2_coords(center) / PPM)
        jd = b2RevoluteJointDef()
        jd.bodyA = self.body
        jd.bodyB = self.center_body
        self.world.CreateJoint(jd)

        self.create_image()

    def update(self, dt: float, events):
        self.body.ApplyTorque(self.torque * self.body.mass, True)

    def render(self):
        self.set_rotated_sprite(self.body, self.init_image)

    def dispose(self):
        super().dispose()
        self.world.DestroyBody(self.center_body)
