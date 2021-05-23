import pygame

from configurations import *
from sprites.sprite import Sprite
from utils.utils import bound


class PoliceEffect(Sprite):
    layer = 1

    def __init__(self, *groups):
        super().__init__(*groups)

        self.image = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        self.image.set_alpha(15)
        self.rect = pygame.Rect(0, 0, 0, 0)

        self.is_updating = False
        self.state = 0
        self.switch_color = 2

    def set_enabled(self, value):
        self.is_updating = value
        if not value:
            self.image.fill((0, 0, 0, 0))

    def update(self, dt: float, events):
        if not self.is_updating:
            return
        self.state += dt
        if self.state >= self.switch_color:
            self.state = 0

    def render(self):
        if not self.is_updating:
            return
        state = self.state if self.state < 1 else 2 - self.state
        self.image.fill((255 * state, 0, 255 * (1 - state)))

