import pygame

from resources import Resources
from sprites.sprite import Sprite
from utils.utils import bound, paint_images


class Button(Sprite):
    def __init__(self, res: Resources, pos, text, *groups, image=None):
        super().__init__(*groups)
        if image is None:
            image = paint_images([res.image_button], lambda x: (255, 255, 255, x[3]))[0]
        self.pos = pos
        self.set_init_image(image)

        render = res.font24.render(text, True, (0, 0, 0))
        self.image.blit(render, ((self.image.get_width() - render.get_width()) / 2, 12))

        self.init_rect = pygame.Rect(self.pos, self.image.get_size())
        self.rect = self.init_rect.copy()

        self.mouse_down = False
        self.clicked = False
        self.pressed = False
        self.animation_state = 0
        self._connected = lambda: None

        self.hover = False
        self.hover_state = 0

        self.TIME_ANIMATION = 0.3
        self.BACK_ANIMATION_COEFFICIENT = 2
        self.SCALE_COEFFICIENT = 0.2

        self.HOVER_TIME = 0.15
        self.HOVER_COEFFICIENT = 0.15

    def is_clicked(self):
        return self.clicked

    def clicked_connect(self, f):
        self._connected = f

    @staticmethod
    def _scale_rect(rect, scale):
        scaled_size = int(rect.width * scale), int(rect.height * scale)
        rect = pygame.Rect((rect.x + (rect.width - scaled_size[0]) // 2,
                            rect.y + (rect.height - scaled_size[1]) // 2),
                           scaled_size)
        return rect

    @staticmethod
    def _animation_function(x):
        if x == 1:
            return 1
        return -2 ** (-5 * x) + 1

    def update(self, dt, events):
        if self.clicked:
            self.clicked = False
        for i in events:
            if i.type == pygame.MOUSEBUTTONUP:
                self.mouse_down = False
                if self.init_rect.collidepoint(i.pos) and self.pressed:
                    self.clicked = True
                    self.pressed = False
                    self.hover = False
                    self._connected()
            elif i.type == pygame.MOUSEBUTTONDOWN:
                if i.button == pygame.BUTTON_LEFT:
                    self.mouse_down = True
                    if self.init_rect.collidepoint(i.pos):
                        self.pressed = True

            elif i.type == pygame.MOUSEMOTION:
                if self.init_rect.collidepoint(i.pos):
                    self.hover = True
                else:
                    self.pressed = False
                    self.hover = False

        if self.pressed:
            self.animation_state += dt / self.TIME_ANIMATION
        else:
            self.animation_state -= dt / self.TIME_ANIMATION * self.BACK_ANIMATION_COEFFICIENT
        self.animation_state = bound(self.animation_state, 0, 1)

        self.hover_state += dt / self.HOVER_TIME * (int(self.hover) * 2 - 1)
        self.hover_state = bound(self.hover_state, 0, 1)

    def render(self):
        # Displaying
        state = self._animation_function(self.animation_state)
        scale = 1 - state * self.SCALE_COEFFICIENT - self.hover_state * self.HOVER_COEFFICIENT
        scaled_rect = self._scale_rect(self.init_rect, scale)
        scaled_image = pygame.transform.scale(self.init_image, scaled_rect.size)
        self.rect = scaled_rect
        self.image = scaled_image
