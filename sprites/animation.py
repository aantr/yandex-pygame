import pygame

from sprites.sprite import Sprite


class Animation:
    def __init__(self, sheet: pygame.Surface, count_frames, fps):
        super().__init__()

        self.timer = 0
        self.sheet = sheet
        self.count_frames = count_frames
        self.fps = fps

    def update(self, dt: float):
        self.timer += dt

    def get_frame(self):
        width = self.sheet.get_width() / self.count_frames
        rect = (int(width * self.get_current_frame_index()), 0,
                int(width), self.sheet.get_height())
        return self.sheet.subsurface(rect)

    def get_current_frame_index(self):
        return int(self.timer * self.fps) % self.count_frames

    def is_first_loop_passed(self):
        return self.timer > self.count_frames / self.fps
