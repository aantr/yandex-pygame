import pygame

from resources import Resources


class State:
    def __init__(self, asm, res):
        self.asm = asm
        self.res: Resources = res

    def update(self, dt, events):
        ...

    def render(self, sc: pygame.Surface):
        ...

    def load(self):
        """Called on transitions between states,
        when we need long time loading"""
        ...

    def dispose(self):
        ...
