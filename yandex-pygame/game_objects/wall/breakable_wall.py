import pygame
from Box2D import *

from constants import *
from game_objects.bomb import BombExplosion
from game_objects.explosion import Explosion
from game_objects.wall.base_wall import BaseWall
from resources import Resources
from utils.utils import b2_coords, paint_images


class BreakableWall(BaseWall):
    def __init__(self, world, cl, res: Resources, point1, point2,
                 game_object_group, *groups):
        super().__init__(world, cl, res.image_breakable_wall,
                         28, 2, 0.1, 0.5, b2_staticBody, point1, point2,
                         game_object_group, *groups)

        width, size, sin = self.width, self.size, self.sin
        self.res = res

        if (type(self), size, sin) not in self.images:
            self.create_image()
        else:
            im, shadow, rect = self.images[(type(self), size, sin)]
            self.image = im
            if self.draw_shadow:
                self.shadow = shadow
            self.rect = pygame.Rect(rect)
        self.rect.center = self.center

    def on_explosion(self, obj_from, power):
        if type(obj_from) == BombExplosion:
            if power > 200:
                particles = paint_images(
                    self.res.explosion_particles, lambda x: (0, 0, 0, x[3]))
                Explosion.spawn_particles(self.world, self.cl, self.res,
                                          b2_coords(self.body.position) * PPM, particles, 15, 10,
                                          self.game_object_group)
                self.dispose()

    def dispose(self):
        super().dispose()
