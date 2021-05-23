import pygame
import math
from configurations import *
from resources import Resources
from sprites.sprite import Sprite
from utils.utils import bound


class EnergyLine(Sprite):
    def __init__(self, res: Resources, *groups):
        super().__init__(*groups)

        self.image = pygame.Surface((300, 100)).convert_alpha()
        self.image_line = res.image_energy_line
        self.image_empty = res.image_energy_line_empty
        self.image_full = res.image_energy_line_full
        self.image_icons = res.image_energy_icons

        self.rect = pygame.Rect(WIDTH - 300, 0, *self.image.get_size())

        self.energy = 0
        self.energy_parts = 20

    def set_energy(self, value):
        self.energy = value

    def render(self):
        self.energy = bound(self.energy, 0, 1)
        energy = math.ceil(self.energy * self.energy_parts) / self.energy_parts
        self.image.fill((0, 0, 0, 0))
        sf = pygame.Surface(self.image_empty.get_size()).convert_alpha()
        sf.fill((0, 0, 0, 0))
        sf.blit(self.image_empty, (0, 0))
        sf.blit(self.image_full, (sf.get_width() * (energy - 1), 0),
                None, pygame.BLEND_RGBA_MIN)
        self.image.blit(self.image_line, (50, 25))
        self.image.blit(sf, (90, 31))
        icon = math.ceil((1 - energy) * (len(self.image_icons) - 2))
        if not self.energy:
            icon = -1
        self.image.blit(self.image_icons[icon], (35, 12))
