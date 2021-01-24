import pygame
from pygame.constants import *
from app_state_manager import AppStateManager
from resources import Resources
from constants import *
from states.menu_state import MenuState
from states.game_state import GameState


class Main:
    def __init__(self):
        pygame.init()
        pygame.mouse.set_system_cursor(SYSTEM_CURSOR_ARROW)
        self.screen: pygame.Surface = pygame.display.set_mode(
            (WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        # Скины
        self.res = Resources()
        self.skins = [self.res.image_car_red, self.res.image_car_cyan,
                      self.res.image_car_yellow, self.res.image_car_purple,
                      self.res.image_car_green, self.res.image_police_car]

        # Игровой прогресс
        self.completed_levels = 0
        self.dollars = 0
        self.saved_skins = [0] * len(self.skins)
        self.saved_skins[0] = 1
        self.current_skin = 0
        self.get_save()

        self.asm = AppStateManager(self)
        self.asm.push_first(MenuState(self.asm, self.res))
        self.running = True

    def get_save(self):
        try:
            with open('save.bin', 'br') as f:
                fields = list(map(lambda x: int.from_bytes(x, 'big'),
                                  f.read().strip().split(b'\n')))
                self.completed_levels, \
                self.dollars, \
                self.current_skin, \
                *saved_skins = fields
                for i in range(len(self.saved_skins)):
                    self.saved_skins[i] = saved_skins[i]
        except Exception as e:
            self.write_save()
            self.get_save()

    def write_save(self):
        with open('save.bin', 'bw') as f:
            fields = self.completed_levels, self.dollars, self.current_skin, *self.saved_skins
            for i in fields:
                f.write(i.to_bytes(10, 'big') + b'\n')

    def update(self):
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                self.write_save()
                self.running = False

        self.asm.update(1 / self.get_fps(), events)
        self.asm.render(self.screen)

        pygame.display.update()
        self.clock.tick(FPS)

    def get_fps(self):
        clock_fps = self.clock.get_fps()
        if clock_fps > FPS // 2:
            return self.clock.get_fps()
        return FPS


if __name__ == '__main__':
    main = Main()
    while main.running:
        main.update()

    pygame.quit()
