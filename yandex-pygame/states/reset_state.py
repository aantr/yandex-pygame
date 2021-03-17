import pygame
from constants import *
from sprites.button import Button
from sprites.sprite import Group
from states.state import State


class ResetState(State):
    def load(self):
        self.sprite_group = Group()

        self.label_font = self.res.font48
        self.label = 'Вы точно хотите сбросить свой игровой прогресс?'
        self.reset_button = Button(self.res, (WIDTH / 2 - 100, HEIGHT / 2),
                                   'Да', self.sprite_group)
        self.exit = Button(self.res, (WIDTH / 2 + 50, HEIGHT / 2),
                           'Назад', self.sprite_group)

    def reset(self):
        self.asm.main.reset_save()

    def update(self, dt, events):
        self.sprite_group.update(dt, events)

        if self.reset_button.is_clicked():
            self.reset()
            self.asm.pop()
        if self.exit.is_clicked():
            self.asm.pop()

    def render(self, sc: pygame.Surface):
        sc.fill((130, 130, 130))
        self.sprite_group.draw(sc)

        render = self.label_font.render(self.label, True, (0, 0, 0))
        sc.blit(render, (WIDTH / 2 - render.get_width() / 2, HEIGHT / 4))
