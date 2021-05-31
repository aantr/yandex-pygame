import pygame

from configurations import *
from sound_manager import SoundManager
from sprites.button import Button
from sprites.conversation import Conversation
from sprites.dollars import Dollars
from sprites.energy_line import EnergyLine
from sprites.minimap import Minimap
from sprites.police_effect import PoliceEffect
from states.game_state import GameState
from states.levels import Level


class LevelState(GameState):
    def load(self):
        self.levels = Level.levels
        self.level = self.levels[self.asm.main.completed_levels]
        self.is_over = False
        self.saved = False
        self.over_timer = 0
        self.over_timeout = 1
        self.text = self.level[1]

        super().load()

        self.button = Button(self.res, (WIDTH - 120, HEIGHT - 70), 'Меню', self.sprite_group)
        self.minimap = Minimap(300, 240, self.sprite_group)
        self.conversation = Conversation(self.res, self.sprite_group)
        self.police_effect = PoliceEffect(self.sprite_group)
        self.energy_line = EnergyLine(self.res, self.sprite_group)
        self.dollars = Dollars(self.res, self.sprite_group, level=True)

        self.sm = SoundManager(self.conversation, self.car, self.sprite_group)
        self.load_map(self.level[0])
        self.sm.player_car = self.car
        self.sm.set_background(self.res.music_bg_game, 0.1)

    def update(self, dt, events):
        self.dollars.value = self.car.dollars
        self.dollars.set_darkness_value(self.darkness.value)

        if self.is_over:
            self.over_timer += dt
        if self.over_timer >= self.over_timeout and not self.saved:
            self.saved = True
            if self.car.looted:
                self.asm.main.dollars += self.car.dollars
                self.asm.main.completed_levels = min(
                    self.asm.main.completed_levels + 1,
                    len(self.levels) - 1)
                self.asm.main.write_save()
                self.conversation.show(['Esc - выход, Space - следующий уровень'],
                                       event_listener=self.end_event_listener)
            else:
                self.conversation.show(['Esc - выход, Space - начать заново'],
                                       event_listener=self.end_event_listener)

        if super().update(dt, events) is False:
            return
        self.energy_line.set_energy(self.car.energy)

        if not self.is_over and self.car.looted and not self.conversation.is_showing:
            self.conversation.show(['Вы победили'], lambda: self.__setattr__('is_over', True))

        if not self.is_over and not self.car.energy and not self.conversation.is_showing:
            self.sm.set_background(self.res.sound_lose, 1)
            self.conversation.show(['Вы потеряли энергию, игра окончена'],
                                   lambda: self.__setattr__('is_over', True))
            self.car.break_down()
