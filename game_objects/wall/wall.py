import pygame
from Box2D import *

from game_objects.wall.base_wall import BaseWall
from resources import Resources


class Wall(BaseWall):
    def __init__(self, world, cl, res: Resources,
                 point1, point2, game_object_group, *groups):
        super().__init__(world, cl, res.image_wall,
                         28, 2, 0.1, 0.5, b2_staticBody, point1, point2, game_object_group, *groups)

        width, size, sin = self.width, self.size, self.sin
        # Изображение со скругленными углами
        if (type(self), size, sin) not in self.images:
            self.create_image()
        else:
            im, shadow, rect, shadow_rect = self.images[(type(self), size, sin)]
            self.image = im
            if self.draw_shadow:
                self.shadow = shadow
                self.shadow_rect = pygame.Rect(shadow_rect)
                self.shadow_rect.center = self.center
            self.rect = pygame.Rect(rect)
        self.rect.center = self.center
