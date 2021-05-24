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


class DriftState(GameState):
    def load(self):
        super().load()

        self.button = Button(self.res, (WIDTH - 120, HEIGHT - 70), 'Меню', self.sprite_group)
        self.minimap = Minimap(200, 200, self.sprite_group)
        self.conversation = Conversation(self.res, self.sprite_group)
        self.police_effect = PoliceEffect(self.sprite_group)

        self.sm = SoundManager(self.conversation, self.car, self.sprite_group)
        self.load_map(self.res.drift_map_path)
        self.sm.player_car = self.car
        self.sm.set_background(self.res.music_bg_menu, 0.1)

    def update(self, dt, events):
        super().update(dt, events)
