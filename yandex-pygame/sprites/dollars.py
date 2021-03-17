import pygame
import math
from constants import *
from resources import Resources
from sprites.sprite import Sprite
from utils.utils import bound


class Dollars(Sprite):
    def __init__(self, res: Resources, *groups):
        super().__init__(*groups)

        self.image = pygame.Surface((300, 100)).convert_alpha()
        self.image_ = res.image_dollar
        self.rect = pygame.Rect(0, 0, *self.image.get_size())
        self.font = res.font36

        self.value = 0

    def render(self):
        self.image.fill((0, 0, 0, 0))
        self.image.blit(self.image_, (20, 20))
        self.image.blit(self.font.render(str(self.value), True, (0, 0, 0)), (125, 26))
