import random
from Box2D import *

from game_objects.game_object import GameObject
from resources import Resources
from utils.utils import b2_coords
from utils.b2_factory import B2Factory
from constants import *


class TireParticle(GameObject):
    def __init__(self, world, cl, res: Resources, pos, game_object_group, *groups):
        super().__init__(world, cl, game_object_group, *groups, connects=False)

        self.ignore_ray_casting = True
        self.draw_shadow = False

        image = res.image_tire_particle
        self.set_init_image(image)
        self.rect.center = pos

        shape = b2CircleShape()
        shape.radius = self.image.get_size()[0] / 2 / PPM
        fd = B2Factory.create_fixture(shape, 1, 0.1, 0.5, True)
        self.body = B2Factory.create_body(
            world, b2_dynamicBody, fd, b2_coords(pos) / PPM)
        self.body.userData = self
        self.body.linearDamping = 3
        self.body.fixedRotation = True
        impulse = 0.5
        self.body.ApplyLinearImpulse(
            (random.uniform(-impulse, impulse), random.uniform(-impulse, impulse)),
            self.body.GetWorldPoint((0, 0)), True)

        self.timer = 0
        self.timeout = 0.2

    def update(self, dt: float, events):
        self.timer += dt
        if self.timer > self.timeout:
            self.dispose()

    def render(self):
        self.image.set_alpha((1 - self.timer / self.timeout) * 255)
        self.rect.center = b2_coords(self.body.position) * PPM
        ...

    def dispose(self):
        super().dispose()
        self.world.DestroyBody(self.body)
