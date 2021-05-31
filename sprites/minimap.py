import pygame

from configurations import *
from sprites.sprite import Sprite


class Minimap(Sprite):
    def __init__(self, width, height, *groups):
        super().__init__(*groups)

        self.width = width
        self.height = height

        self.image = pygame.Surface((width, height))
        self.image.set_alpha(150)

        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.bottomleft = 0, HEIGHT

        self.scale = 8
        self.shift = pygame.Vector2()

    def clear(self):
        self.image.fill((50, 50, 50))

    def set_shift(self, shift):
        self.shift = shift - pygame.Vector2(self.image.get_size()) / 2 * self.scale

    def coords(self, pos):
        return (pygame.Vector2(pos) - self.shift) / self.scale

    def add_line(self, start, end, color):
        pygame.draw.line(self.image, color,
                         self.coords(start),
                         self.coords(end), 4)

    def add_point(self, pos, color):
        rect = pygame.Rect(0, 0, 8, 8)
        rect.center = self.coords(pos)
        pygame.draw.rect(self.image, color,
                         rect)

    def add_rect(self, rect, color):
        rect = pygame.Rect(rect)
        rect = self.coords(rect.topleft), pygame.Vector2(rect.size) / self.scale
        pygame.draw.rect(self.image, color, rect)
