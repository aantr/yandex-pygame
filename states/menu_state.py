import random

import pygame
from Box2D import *
from constants import *
from game_objects.explosion import Explosion
from game_objects.player_car.player_car import PlayerCar
from game_objects.player_car.skin import CarSkin
from game_objects.tire import C_UP
from sprites.button import Button
from sprites.dollars import Dollars
from sprites.sprite import Group
from states.game_state import GameState
from states.reset_state import ResetState
from states.shop_state import ShopState
from states.state import State
from utils.contact_listener import ContactListener
from utils.utils import paint_images


class MenuState(State):
    def load(self):
        self.sprite_group = Group()

        self.label_font = self.res.font64
        self.button_play = Button(self.res, ((WIDTH - self.res.image_button.get_width()) / 2, 300),
                                  'Играть', self.sprite_group)
        self.button_shop = Button(self.res, ((WIDTH - self.res.image_button.get_width()) / 2, 370),
                                  'Магазин', self.sprite_group)
        self.button_reset = Button(self.res, ((WIDTH - self.res.image_button.get_width()) / 2, 440),
                                   'Сброс', self.sprite_group)
        self.button_exit = Button(self.res, ((WIDTH - self.res.image_button.get_width()) / 2, 510),
                                  'Выход', self.sprite_group)

        self.dollars = Dollars(self.res, self.sprite_group)

        # Задний фон для меню
        self.world = b2World()
        self.world.gravity = 0, 0
        self.contact_listener = ContactListener()
        self.world.contactListener = self.contact_listener
        self.obj_args = self.world, self.contact_listener, self.res
        self.animation_background = pygame.Surface((500, 300)).convert_alpha()
        self.animation_background.fill((0, 0, 0, 0))
        self.background_group = Group()
        self.spawn_random_car()
        self.spawn_timer = 0
        self.spawn_timeout = 1

    def spawn_random_car(self):
        r = random.randint(0, 1)
        car = PlayerCar(*self.obj_args, CarSkin(
            self.res, self.asm.main.skins[self.asm.main.current_skin]),
                        (random.randint(100, WIDTH - 100), r * HEIGHT + (r * 2 - 1) * 100),
                        random.randint(-20, 20) + 180 * (r - 1), None, self.background_group)
        car.control_state |= C_UP
        car.dispose_timeout = 1
        for tire in car.tires:
            tire.set_control_state(car.control_state)

    def update(self, dt, events):
        self.dollars.value = self.asm.main.dollars
        self.sprite_group.update(dt, events)

        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_timeout:
            self.spawn_timer = 0
            self.spawn_random_car()
        self.world.Step(dt, 6, 2)
        self.background_group.update(dt, events)
        for i in self.background_group:
            if type(i) == PlayerCar:
                i.energy -= dt * 0.3
                if i.energy <= 0:
                    i.break_down()
        for i in events:
            if i.type == pygame.MOUSEBUTTONDOWN:
                if i.button == pygame.BUTTON_RIGHT:
                    Explosion.apply_impulses(self.world, pygame.mouse.get_pos(), 1500, 500, 15, self)
                    particles = paint_images(
                        self.res.explosion_particles, lambda x: (0, 0, 0, x[3]))
                    Explosion.spawn_particles(*self.obj_args, pygame.mouse.get_pos(), particles, 10, 10,
                                              self.background_group)
            if i.type == pygame.KEYDOWN:
                if i.key == pygame.K_SPACE:
                    self.spawn_random_car()

        if self.button_play.is_clicked():
            self.asm.push(GameState(self.asm, self.res))
        if self.button_shop.is_clicked():
            self.asm.push(ShopState(self.asm, self.res))
        if self.button_reset.is_clicked():
            self.asm.push(ResetState(self.asm, self.res))
        if self.button_exit.is_clicked():
            self.asm.pop()

    def render(self, sc: pygame.Surface):
        sc.fill((130, 130, 130))

        self.background_group.draw(sc)
        render = self.label_font.render('Ограбление банка', True, (0, 0, 0))
        sc.blit(render, ((WIDTH - render.get_width()) / 2, 100))
        self.sprite_group.draw(sc)
        render = self.res.font36.render(f'Уровень: {self.asm.main.completed_levels + 1}', True, (0, 0, 0))
        sc.blit(render, (20, 80))
