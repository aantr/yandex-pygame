import pygame
from resources import Resources
from sprites.sprite import Sprite


class Dollars(Sprite):
    def __init__(self, res: Resources, *groups, level=False):
        super().__init__(*groups)

        self.image = pygame.Surface((300, 300)).convert_alpha()
        self.image_ = res.image_dollar
        self.rect = pygame.Rect(0, 0, *self.image.get_size())
        self.font = res.font36
        self.font20 = res.font20
        self.level = level
        self.text_color = 0, 0, 0
        self.value = 0

    def set_darkness_value(self, value):
        v = value * 255
        self.text_color = v, v, v

    def render(self):
        self.image.fill((0, 0, 0, 0))
        shift = 0, 0
        if self.level:
            shift = 0, 30
        self.image.blit(self.image_, (20 + shift[0], 20 + shift[1]))
        self.image.blit(self.font.render(str(self.value), True, self.text_color), (125 + shift[0], 26 + shift[1]))
        if self.level:
            self.image.blit(self.font20.render('На этом уровне:', True, self.text_color), (20, 20))
