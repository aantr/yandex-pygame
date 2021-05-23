import os

import pygame

from configurations import PLAY_SOUNDS


class Resources:
    def __init__(self):
        self.image_button = self.load_image('_res/images/button.png')
        self.image_car_red = self.load_image('_res/images/car/car_red.png')
        self.image_car_green = self.load_image('_res/images/car/car_green.png')
        self.image_car_yellow = self.load_image('_res/images/car/car_yellow.png')
        self.image_car_cyan = self.load_image('_res/images/car/car_cyan.png')
        self.image_car_purple = self.load_image('_res/images/car/car_purple.png')
        self.image_police_car = self.load_image('_res/images/car/police.png')
        self.image_tire = self.load_image('_res/images/car/tire.png')
        self.image_tire_particle = self.load_image('_res/images/car/particle.png')

        self.image_ground = self.load_image('_res/images/ground.png')
        self.image_wall = self.load_image('_res/images/wall.png')
        self.image_revolving_wall = self.load_image('_res/images/revolving_wall.png')
        self.image_breakable_wall = self.load_image('_res/images/breakable_wall.png')
        self.image_loading = self.load_image('_res/images/loading.jpg')
        self.image_bomb = self.load_image('_res/images/bomb2.png')
        self.explosion_particles = [self.load_image(i) for i in [
            '_res/images/explosion1.png',
            '_res/images/explosion2.png',
            '_res/images/explosion3.png']]
        self.image_turret = self.load_image('_res/images/turret.png')
        self.image_turret_base = self.load_image('_res/images/turret_base.png')
        self.image_bullet = self.load_image('_res/images/bullet.png')
        self.image_bank = self.load_image('_res/images/bank.png')
        self.image_dollar = self.load_image('_res/images/dollar.png')

        self.energy_item = self.load_image('_res/images/energy_item.png')
        self.image_energy_line = self.load_image('_res/images/energy_line.png')
        self.image_energy_line_empty = self.load_image('_res/images/energy_line_empty.png')
        self.image_energy_line_full = self.load_image('_res/images/energy_line_full.png')
        self.image_energy_icons = [self.load_image(i) for i in [
            '_res/images/energy1.png',
            '_res/images/energy2.png',
            '_res/images/energy3.png',
            '_res/images/energy4.png',
            '_res/images/energy5.png']]

        self.animation_fireball = self.load_image('_res/images/fireball.png')
        self.animation_fireball_explosion = self.load_image('_res/images/fireball_explosion.png')

        self.font64 = self.load_font(64)
        self.font48 = self.load_font(48)
        self.font40 = self.load_font(40)
        self.font36 = self.load_font(36)
        self.font30 = self.load_font(30)
        self.font24 = self.load_font(24)
        self.font20 = self.load_font(20)
        self.font16 = self.load_font(16)
        self.font14 = self.load_font(14)

        self.sound_drift = self.load_sound('_res/sound/drift-car.wav')
        self.sound_drive = self.load_sound('_res/sound/drive_car.wav')
        self.sound_start_car = self.load_sound('_res/sound/start_car.wav', 0.3)

        self.sound_boom = self.load_sound('_res/sound/boom.wav')
        self.sound_lazer = self.load_sound('_res/sound/lazer.wav')
        self.sound_lose = self.path('_res/sound/lose.wav')

        self.music_bg_game = self.path('_res/sound/background_game.wav')
        self.music_bg_menu = self.path('_res/sound/background_menu.wav')

        self.drift_map_path = self.path('_res/maps/drift.svg')

    def load_sound(self, relative_path, volume=None):
        if not PLAY_SOUNDS:
            return
        sound = pygame.mixer.Sound(self.path(relative_path))
        if volume is not None:
            sound.set_volume(volume)
        return sound

    def load_font(self, size):
        return pygame.font.Font(self.path('_res/font/3454344.ttf'), size)

    def load_image(self, relative_path, alpha=True):
        path = self.path(relative_path)
        if alpha:
            return pygame.image.load(path).convert_alpha()
        return pygame.image.load(path).convert()

    @staticmethod
    def path(relative_path):
        directory = os.path.split(__file__)[0]
        return os.path.join(directory, relative_path)
