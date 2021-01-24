import pygame
from constants import *
from game_objects.car import Car
from sprites.button import Button
from sprites.dollars import Dollars
from sprites.sprite import Group
from states.state import State
from utils.utils import paint_images


class ShopState(State):
    def load(self):
        self.sprite_group = Group()

        self.label_font = self.res.font64
        self.button = Button(self.res, ((WIDTH - 140), HEIGHT - 90),
                             'Назад', self.sprite_group)
        self.dollars = Dollars(self.res, self.sprite_group)

        skins = [i.copy() for i in self.asm.main.skins]
        image_tire = paint_images([self.res.image_tire], lambda x: (61, 67, 71, x[3]))[0]
        self.skins = []
        for i in skins:
            im = image_tire
            margin = 10
            new = pygame.Surface((i.get_width() + margin * 2,
                                  i.get_height() + margin * 2)).convert_alpha()
            new.fill((0, 0, 0, 0))
            for x in [-1, 1]:
                for y in [-1, 1]:
                    new.blit(im, (Car.tire_shift[0] * x + i.get_width() // 2 -
                                  im.get_width() // 2 + margin,
                                  Car.tire_shift[1] * y + i.get_height() // 2 -
                                  im.get_height() // 2 + margin))
            new.blit(i, (margin, margin))
            self.skins.append(new)

        self.buttons = [Button(self.res, ((WIDTH / 2 + 120 * i -
                                           len(self.skins) / 2 * 120), HEIGHT / 2 - 120),
                               '', self.sprite_group, image=el)
                        for i, el in enumerate(self.skins)]

        self.title_font = self.res.font30
        self.cost = [500] * 5 + [10000]
        self.bought = self.asm.main.saved_skins
        self.current = self.asm.main.current_skin
        self.save()

    def save(self):
        self.asm.main.saved_skins = self.bought
        self.asm.main.current_skin = self.current
        self.asm.main.write_save()

        for i in range(len(self.bought)):
            if self.bought[i]:
                self.cost[i] = 0

    def update(self, dt, events):
        self.dollars.value = self.asm.main.dollars
        self.sprite_group.update(dt, events)

        if self.button.is_clicked():
            self.asm.pop()

        for i in range(len(self.buttons)):
            if self.buttons[i].is_clicked():
                if self.bought[i]:
                    if self.current != i:
                        self.current = i
                else:
                    if self.cost[i] <= self.asm.main.dollars:
                        self.bought[i] = 1
                        self.current = i
                        self.asm.main.dollars -= self.cost[i]
                self.save()

    def render(self, sc: pygame.Surface):
        sc.fill((130, 130, 130))
        self.sprite_group.draw(sc)
        for i in range(len(self.cost)):
            title = f'{self.cost[i]} $' if self.cost[i] else \
                'Куплено' if self.current != i else '# # # #'
            render = self.title_font.render(title, True, (0, 0, 0))
            pos = self.buttons[i].pos
            shift = -render.get_width() / 2 + 45, 140
            sc.blit(render, (pos[0] + shift[0], pos[1] + shift[1]))
