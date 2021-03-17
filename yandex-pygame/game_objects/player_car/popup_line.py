import pygame

from game_objects.game_object import GameObject
from resources import Resources


class PopupLine(GameObject):
    layer = 3

    def __init__(self, world, cl, res: Resources, car, text,
                 game_object_group, *groups):
        super().__init__(world, cl, game_object_group, *groups, connects=False)

        self.ignore_ray_casting = True
        self.draw_shadow = False

        self.car = car
        image = res.font30.render(text, True, (0, 0, 0))
        self.set_init_image(image)

        self.timer = 0
        self.timeout = 2
        self.max_height = 150
        self.speed = 175

    def update(self, dt: float, events):
        self.timer += dt
        if self.timer > self.timeout:
            self.dispose()

    def render(self):
        self.image.set_alpha((1 - self.timer / self.timeout) * 255)
        self.rect.center = pygame.Vector2(self.car.get_position()) + \
                           pygame.Vector2(0, -30 - min(self.timer / self.timeout * self.speed, self.max_height))
        ...
