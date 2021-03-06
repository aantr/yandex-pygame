import math
import pygame
import svgelements

from game_objects.bank import Bank
from game_objects.conversation_barrier import ConversationBarrier
from game_objects.darkness import Darkness
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
from sprites.camera import Camera
from sprites.sprite import Group, Sprite

from states.state import State
from Box2D import *
from utils.contact_listener import ContactListener

try:
    from Box2D.examples.framework import Framework
except ModuleNotFoundError:
    class Framework:
        ...

BOX2D_DEBUG = 0


class GameState(State, Framework):
    def __init__(self, asm, res):
        super().__init__(asm, res)

        self.button = None
        self.sm = None
        self.conversation = None
        self.police_effect = None
        self.minimap = None
        if BOX2D_DEBUG:
            Framework.__init__(self)
            self.load()
            self.run()

    def load(self):
        if not BOX2D_DEBUG:
            self.world = b2World()
        self.world.gravity = 0, 0
        self.contact_listener = ContactListener()
        self.world.contactListener = self.contact_listener
        # Аргументы при создании игрового объекта
        self.obj_args = self.world, self.contact_listener, self.res

        # ############# Other sprites
        self.sprite_group = Group()

        # ############# Игровые объекты
        self.camera_group = Group()
        self.camera = Camera(self.camera_group)
        self.camera_shift = b2Vec2()

        self.walls = Group()
        self.barriers = Group()
        self.grounds = Group()
        self.polices = Group()
        self.energy_items = Group()
        self.turrets = Group()

        self.darkness = None
        self.car = None
        self.bank = None

    def load_map(self, map_path):
        svg = svgelements.SVG.parse(map_path)
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

        self.darkness = Darkness(*self.obj_args, self.car, self.camera, self.camera_group)

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
                Turret(*self.obj_args, center, self.camera_group, self.turrets)
            else:
                if not self.bank:
                    self.bank = Bank(*self.obj_args, center, self.camera_group)
                else:
                    raise MapError('2 банка на карте')

    def pause_event_listener(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                return True
            if event.key == pygame.K_ESCAPE:
                self.asm.pop()
            elif event.key == pygame.K_BACKSPACE:
                self.asm.set(self.__class__(self.asm, self.res))

    def end_event_listener(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.asm.pop()
            if event.key == pygame.K_SPACE:
                self.asm.set(self.__class__(self.asm, self.res))

    def update(self, dt, events):

        self.sprite_group.update(dt, events)

        if self.button.is_clicked():
            self.conversation.show(['Esc - выход, Space - продолжить игру, Backspace - начать заново'],
                                   event_listener=self.pause_event_listener)

        dt *= self.conversation.get_pause_modifier()

        capture_input = (self.conversation.is_updating or
                         self.button.hover)

        ###############
        # Обновляем контроль не в зависимости от dt
        self.car.update_control(events, only_move=capture_input)
        if not dt:
            return False

        self.world.Step(dt, 6, 2)
        self.camera.chase_sprite(self.car, dt, self.camera.get_camera_shift_car(self.car))
        self.camera.update(dt, events)
        self.darkness.set_center()

        is_chasing = any([i.is_chasing for i in self.polices])
        self.car.set_police_chase(is_chasing)
        for i in self.polices:
            i: Police
            i.detect_car(self.car)
        self.police_effect.set_enabled(is_chasing)

        if self.car.is_bank_loot:
            for i in self.polices:
                if not i.is_chasing:
                    i.set_chasing(self.car)

        for i in self.barriers:
            i: ConversationBarrier
            if i.collided:
                i.dispose()
                self.conversation.show(self.text[0])
                self.text = self.text[1:]

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
