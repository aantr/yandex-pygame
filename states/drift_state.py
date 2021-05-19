import pygame

from constants import *
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

        pygame.mixer.music.load(self.res.music_bg_menu)
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1, fade_ms=2000)

    def update(self, dt, events):
        super().update(dt, events)
