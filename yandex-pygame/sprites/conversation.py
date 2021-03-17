import pygame

from constants import *
from resources import Resources
from sprites.sprite import Sprite
from utils.utils import bound


class Conversation(Sprite):
    layer = 1

    def __init__(self, res: Resources, *groups):
        super().__init__(*groups)

        self.font = res.font40
        self.image = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.height = 55

        self.is_showing = False
        self.state = 0
        self.animation_duration = 1
        self.is_updating = False
        self.texts = []
        self.callback = None
        self.event_listener = None

        self.char_timeout = 0.01
        self.showed_chars = 0
        self.char_animation_timer = 0

    def get_pause_modifier(self):
        return 1 - self.state

    def set_enabled(self, value):
        self.is_showing = value
        self.is_updating = True

    def show(self, texts, callback=None, event_listener=None):
        if self.is_updating:
            return
        self.set_enabled(True)
        self.texts = texts
        self.callback = callback
        self.event_listener = event_listener

    def update(self, dt: float, events):
        if not self.is_updating:
            return
        self.state += dt / self.animation_duration * (int(self.is_showing) * 2 - 1)
        self.state = bound(self.state, 0, 1)
        if not self.is_showing and self.state <= 0:
            self.image.fill((0, 0, 0, 0))
            self.is_updating = False
            if self.callback:
                self.callback()
                self.callback = None

        if self.state == 1:
            self.char_animation_timer += dt
            if self.char_animation_timer >= self.char_timeout:
                self.char_animation_timer = 0
                self.showed_chars += 1

        for i in events:
            listener = self.default_listener if not \
                self.event_listener else self.event_listener
            if listener(i):
                if self.texts and len(self.texts[0]) <= self.showed_chars:
                    if len(self.texts) == 1:
                        self.set_enabled(False)
                    self.texts = self.texts[1:]
                    self.showed_chars = 0

    def render(self):
        if not self.is_updating:
            return
        self.image.fill((0, 0, 0, 0))
        frame = pygame.Surface((WIDTH, int(self.state * self.height))).convert_alpha()
        frame.fill((0, 0, 0, 180))
        self.image.blit(frame, (0, 0))  # Top frame
        if self.texts:
            render_font = self.font.render(self.texts[0], True, (255, 255, 255))
            render_chars = self.font.render(self.texts[0][:self.showed_chars], True, (255, 255, 255))
            frame.blit(render_chars, ((WIDTH - render_font.get_width()) / 2,
                                      (frame.get_height() - render_font.get_height()) / 2))
        self.image.blit(frame, (0, HEIGHT - frame.get_height()))  # Bottom frame

    def default_listener(self, event):
        if event.type == pygame.KEYDOWN:
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            return True

    def dispose(self):
        # Не нужно хранить ссылки на GameState тк
        # он может не удалится из памяти питон
        del self.callback
        del self.event_listener
