import math
import pygame
import svgelements

from game_objects.bank import Bank
from game_objects.conversation_barrier import ConversationBarrier
from game_objects.energy_item import EnergyItem
from game_objects.game_object import GameObject
from game_objects.player_car.skin import CarSkin
from game_objects.turret.turret import Turret
from game_objects.wall.base_wall import BaseWall
from game_objects.wall.breakable_wall import BreakableWall
from game_objects.police import Police
from game_objects.wall.revolving_wall import RevolvingWall
from game_objects.player_car.player_car import PlayerCar
from game_objects.ground import Ground
from game_objects.wall.wall import Wall
from sound_manager import SoundManager

from sprites.button import Button
from sprites.camera import Camera
from sprites.conversation import Conversation
from sprites.dollars import Dollars
from sprites.energy_line import EnergyLine
from sprites.police_effect import PoliceEffect
from sprites.minimap import Minimap
from sprites.sprite import Group, Sprite
from states.levels import Level

from states.state import State
from Box2D import *
from Box2D.examples.framework import Framework
from constants import *
from utils.contact_listener import ContactListener


class GameState(State, Framework):
    BOX2D_DEBUG = 0

    def __init__(self, asm, res):
        super().__init__(asm, res)

        if self.BOX2D_DEBUG:
            Framework.__init__(self)
            self.load()
            self.run()

    def load(self):
        self.levels = Level.levels
        self.level = self.levels[self.asm.main.completed_levels]

        if not self.BOX2D_DEBUG:
            self.world = b2World()
        self.world.gravity = 0, 0
        self.contact_listener = ContactListener()
        self.world.contactListener = self.contact_listener
        # Аргументы при создании игрового объекта
        self.obj_args = self.world, self.contact_listener, self.res

        self.is_over = False
        self.saved = False
        self.over_timer = 0
        self.over_timeout = 1

        # ############# Игровые объекты
        self.camera_group = Group()
        self.camera = Camera(self.camera_group)
        self.camera_shift = b2Vec2()

        self.walls = Group()
        self.barriers = Group()
        self.grounds = Group()
        self.polices = Group()
        self.energy_items = Group()
        self.bank = Group()
        self.turret = Group()
        self.car = None

        # ############# Other sprites
        self.sprite_group = Group()

        self.button = Button(self.res, (WIDTH - 120, HEIGHT - 70), 'Меню', self.sprite_group)
        self.minimap = Minimap(200, 200, self.sprite_group)
        self.conversation = Conversation(self.res, self.sprite_group)
        self.police_effect = PoliceEffect(self.sprite_group)
        self.energy_line = EnergyLine(self.res, self.sprite_group)
        self.dollars = Dollars(self.res, self.sprite_group, level=True)

        self.text = self.level[1]

        self.sm = SoundManager(self.conversation, self.car, self.sprite_group)
        self.load_map()
        self.sm.player_car = self.car

        pygame.mixer.music.load(self.res.music_bg_game)
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1, fade_ms=2000)

    def load_map(self):
        svg = svgelements.SVG.parse(self.level[0])
        scale_map = 25

        for el in svg.elements():
            if type(el) == svgelements.Polyline:
                el: svgelements.Polyline
                for i in range(len(el.points) - 1):
                    p1 = el.points[i] * scale_map
                    p2 = el.points[i + 1] * scale_map
                    self.add_line(p1, p2, el)
            elif type(el) == svgelements.SimpleLine:
                el: svgelements.SimpleLine
                self.add_line(pygame.Vector2(el.x1, el.y1) * scale_map,
                              pygame.Vector2(el.x2, el.y2) * scale_map, el)
            elif type(el) == svgelements.Line:
                el: svgelements.Line
                self.add_line(pygame.Vector2(el.start) * scale_map,
                              pygame.Vector2(el.end) * scale_map, el)
            elif type(el) == svgelements.Polygon:
                el: svgelements.Polygon
                for i in range(len(el.points)):
                    p1 = el.points[i] * scale_map
                    p2 = el.points[i - 1] * scale_map
                    self.add_line(p1, p2, el)
            elif type(el) == svgelements.Rect:
                el: svgelements.Rect
                self.add_rect(tuple(map(lambda x: x * scale_map,
                                        (el.x, el.y, el.width, el.height))), el)

    def add_line(self, p1, p2, el):
        if p1 == p2:
            return
        color = el.stroke
        if color == '#7f7f7f':
            Wall(*self.obj_args, p1, p2, self.camera_group, self.walls)
        elif color == '#00000':
            BreakableWall(*self.obj_args, p1, p2, self.camera_group, self.walls)
        elif color == '#ff0000':
            ConversationBarrier(*self.obj_args, p1, p2, self.camera_group, self.barriers)

    def add_rect(self, rect, el: svgelements.Rect):
        color = el.fill
        center = pygame.rect.Rect(rect).center
        angle = math.degrees(el.rotation)
        if color == '#ff0000':
            if not self.car:
                self.car = PlayerCar(*self.obj_args, self.sm, CarSkin(
                    self.res, self.asm.main.skins[self.asm.main.current_skin]),
                                     center, angle, self.camera, self.camera_group)
                self.camera.set_position(self.car.get_position())
            else:
                raise MapError('2 игрока на карте')
        elif color == '#0000ff':
            Police(*self.obj_args, CarSkin(self.res, self.res.image_police_car), center, angle, self.car,
                   self.camera_group, self.polices)
        elif color == '#7f7f7f':
            Ground(*self.obj_args, rect, 0.15, self.camera_group, self.grounds)
        elif color == '#000000':
            RevolvingWall(*self.obj_args, center, 100, 0, 15, self.camera_group, self.walls)
        elif color == '#ffff00':
            EnergyItem(*self.obj_args, center, self.camera_group, self.energy_items)
        elif color == '#00ff00':
            if rect[2] == rect[3]:
                Turret(*self.obj_args, center, self.camera_group, self.turret)
            else:
                Bank(*self.obj_args, center, self.camera_group, self.bank)

    def pause_event_listener(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                return True
            if event.key == pygame.K_ESCAPE:
                self.asm.pop()
            elif event.key == pygame.K_BACKSPACE:
                self.asm.set(GameState(self.asm, self.res))

    def end_event_listener(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.asm.pop()
            if event.key == pygame.K_SPACE:
                self.asm.set(GameState(self.asm, self.res))

    def update(self, dt, events):
        for i in events:
            if i.type == pygame.KEYDOWN:
                ...

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

        ###############

        self.sprite_group.update(dt, events)

        if self.button.is_clicked():
            self.conversation.show(['Esc - выход, Space - продолжить игру, Backspace - начать заново'],
                                   event_listener=self.pause_event_listener)
        self.dollars.value = self.car.dollars

        dt *= self.conversation.get_pause_modifier()

        capture_input = (self.conversation.is_updating or
                         self.button.hover)

        ###############
        # Обновляем контроль не в зависимости от dt
        self.car.update_control(events, only_move=capture_input)
        if not dt:
            return

        self.world.Step(dt, 6, 2)
        self.camera.chase_sprite(self.car, dt, self.camera.get_camera_shift_car(self.car))
        self.camera.update(dt, events)

        is_chasing = any([i.is_chasing for i in self.polices])
        self.car.set_police_chase(is_chasing)
        for i in self.polices:
            i: Police
            i.detect_car(self.car)
        self.police_effect.set_enabled(is_chasing)
        self.energy_line.set_energy(self.car.energy)

        if self.car.is_bank_loot:
            for i in self.polices:
                if not i.is_chasing:
                    i.set_chasing(self.car)

        if not self.is_over and self.car.looted and not self.conversation.is_showing:
            self.conversation.show(['Вы победили'], lambda: self.__setattr__('is_over', True))

        if not self.is_over and not self.car.energy and not self.conversation.is_showing:
            pygame.mixer.music.load(self.res.sound_lose)
            pygame.mixer.music.set_volume(1)
            pygame.mixer.music.play()

            self.conversation.show(['Вы потеряли энергию, игра окончена'],
                                   lambda: self.__setattr__('is_over', True))
            self.car.break_down()

        for i in self.barriers:
            i: ConversationBarrier
            if i.collided:
                i.dispose()
                self.conversation.show(self.text[0])
                self.text = self.text[1:]

        ###############

        # print(f'--- {round(self.car.get_speed(), 1)} ---')
        # print(f'--- {(*self.car.get_position(),)} ---')
        ...

    def render(self, screen: pygame.Surface):
        screen.fill((185, 185, 185))

        self.camera.draw(screen)
        self.sprite_group.draw(screen)

        self.minimap.clear()
        self.minimap.set_shift(self.camera.get_position())
        for i in self.grounds:
            self.minimap.add_rect(i.rect, (128, 128, 128))
        for i in self.walls:
            i: BaseWall
            self.minimap.add_line(i.start, i.end, (255, 255, 255))
        for i in self.polices:
            i: Police
            color = (0, 0, 0) if i.is_broken else (255, 0, 0) if i.is_chasing else (200, 200, 200)
            self.minimap.add_point(i.get_position(), color)
        for i in self.energy_items:
            self.minimap.add_point(i.rect.center, (255, 255, 0))
        self.minimap.add_point(self.car.get_position(), (0, 255, 0))

    def dispose(self):
        for i in self.camera_group:
            i: GameObject
            i.dispose()
        for i in self.sprite_group:
            i: Sprite
            i.dispose()

    def Step(self, *args):
        super().Step(*args)
        self.update(1 / 60, [])


class MapError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
