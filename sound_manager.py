import pygame

from configurations import PLAY_SOUNDS
from sprites.sprite import Sprite


class SoundManager(Sprite):
    def __init__(self, conversation,
                 player_car,
                 *groups):
        super().__init__(*groups)
        self.conversation = conversation
        self.player_car = player_car
        self.enabled = True
        if PLAY_SOUNDS:
            pygame.mixer.set_num_channels(20)
            self.free_channels = [pygame.mixer.Channel(i) for i in range(20)]
        self.playing_sounds = {}

    def get_enabled(self):
        return ((not self.conversation.is_showing) if self.conversation is not None else False) and \
               ((not self.player_car.is_broken) if self.player_car is not None else False) and \
               self.enabled

    def update(self, dt: float, events):
        if not self.get_enabled():
            for k, v in self.playing_sounds.items():
                v.fadeout(500)

    def set_playing(self, sound: pygame.mixer.Sound, fade_ms=0):
        if not PLAY_SOUNDS:
            return
        if sound not in self.playing_sounds:
            self.playing_sounds[sound] = self.free_channels[0]
            self.free_channels = self.free_channels[1:]
        if self.get_enabled() and not self.playing_sounds[sound].get_busy():
            sound.play(loops=-1, fade_ms=fade_ms)

    def stop_playing(self, sound: pygame.mixer.Sound, fade_ms=0):
        if not PLAY_SOUNDS:
            return
        if sound not in self.playing_sounds:
            return
        if self.playing_sounds[sound].get_busy():
            if fade_ms:
                sound.fadeout(fade_ms)
            else:
                sound.stop()

    def play(self, sound: pygame.mixer.Sound):
        if not PLAY_SOUNDS:
            return
        if self.get_enabled():
            sound.play()

    def set_background(self, path, volume):
        if not PLAY_SOUNDS:
            return
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1, fade_ms=2000)
