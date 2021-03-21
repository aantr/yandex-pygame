import pygame
import gc

from constants import *


class StateError(Exception):
    ...


class AppStateManager:
    def __init__(self, main):
        self.main = main

        self.states = []

        # Black fade transition between states
        self.FADE_TIME = 0.5
        self.fade = True
        self.fade_transition = 0
        self.on_transition = False  # True when state end
        self.transition_func = None

        self.black_rect = pygame.Surface((WIDTH, HEIGHT))
        self.loading_image = self.main.res.image_loading

    def set(self, state):
        self.transition(self._set, state)

    def push(self, state):
        self.transition(self._push, state)

    def pop(self):
        self.transition(self._pop)
        if len(self.states) == 1:
            self._pop()
            exit()

    def push_first(self, state):
        self._push(state)

    def _reset_transition(self):
        self.fade = True
        self.on_transition = True

    def transition(self, func, *args):
        self._reset_transition()
        self.transition_func = self.add_arguments(func, *args)

    def _push(self, state):
        self.states.append(state)
        pygame.mixer.music.fadeout(1000)
        state.load()

    def _pop(self):
        state = self.states.pop()
        state.dispose()
        if gc.get_referrers(state):
            print(StateError(f'Warning: State "{type(state)}" is not '
                             f'disposed\nReferrers: {gc.get_referrers(state)}'))
        new_state = self.states[-1].reset()

    def _set(self, state):
        self._pop()
        self._push(state)

    def update(self, dt, events):
        self.states[-1].update(dt, events)

        if self.fade:
            if self.on_transition:
                self.fade_transition -= dt
                if self.fade_transition <= 0:
                    # On transition to black finished
                    self.fade_transition = 0
                    self.on_transition = False
                    self.transition_func()
            else:
                self.fade_transition += dt
                if self.fade_transition >= self.FADE_TIME:
                    # On transition from black finished
                    self.fade = False
                    self.fade_transition = self.FADE_TIME

    def render(self, sc: pygame.Surface):
        self.states[-1].render(sc)

        if self.fade:
            self.render_loading_screen(sc)

    def dispose(self):
        for i in self.states:
            i.dispose()

    def render_loading_screen(self, sc):
        alpha = 255 - self.fade_transition / self.FADE_TIME * 255
        self.black_rect.set_alpha(alpha)
        sc.blit(self.black_rect, (0, 0))

        self.loading_image.set_alpha(alpha)
        sc.blit(self.loading_image, (WIDTH // 2 - self.loading_image.get_size()[0] // 2,
                                     HEIGHT // 2 - self.loading_image.get_size()[1] // 2))

    @staticmethod
    def add_arguments(f, *args):
        def decorated():
            return f(*args)

        return decorated
