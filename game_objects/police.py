import math
import random

import pygame
from Box2D import b2Vec2

from game_objects.fireball import FireballExplosion
from resources import Resources
from utils.utils import b2_coords
from configurations import *
from game_objects.car import Car
from utils.utils import triangle_area
from utils.ray_cast_callback import RayCastCallback, RayFixtureReport
from game_objects.tire import C_RIGHT, C_LEFT, C_UP, C_DOWN


class Police(Car):
    def __init__(self, world, cl, res: Resources, skin, pos, angle, player,
                 game_object_group, *groups):
        super().__init__(world, cl, res, skin, pos, angle,
                         game_object_group, *groups)

        self.res = res
        max_forward_speed = 5
        max_backward_speed = -12
        max_drive_force = 20
        max_lateral_impulse = 1.7
        angular_friction_impulse = 0.1
        linear_friction_impulse = 0
        self.max_forward_speed_random = 5
        self.max_forward_speed_chasing = 18
        self.speed_tire_rotate = math.radians(270)
        self.set_characteristics(
            max_forward_speed, max_backward_speed,
            max_drive_force, max_lateral_impulse,
            angular_friction_impulse, linear_friction_impulse)
        self.color_particles = 50, 50, 200
        self.player = player

        self.prev_pos = None
        self.prev_pos_timer = 0

        self.reverse = False
        self.timer_reverse = 0

        self.way = []
        self.way_timer = 0
        self.way_timeout = 0.3
        self.detected_timer = 0
        self.ray_cast_timer = 0
        self.chase_point_timer = 0

        self.max_detect_radius = 700
        self.is_chasing = False
        self.detect_timeout = 20

        self.hits = set()

    def set_chasing(self, car):
        self.way = [car.get_position()]
        self.is_chasing = True
        self.detected_timer = 0
        self.set_max_forward_speed(self.max_forward_speed_chasing)

    def detect_car(self, car):
        if self.is_broken:
            return
        if self.ray_cast_timer > 0.5:
            self.ray_cast_timer = 0
            point = self.is_near(car)
            if point:
                # If police car detected car near, then
                # delete all points on ways and add car pos
                self.set_chasing(car)

        if self.is_chasing and self.detected_timer >= self.detect_timeout:
            self.is_chasing = False
            self.way = []
            self.detected_timer = 0
            self.set_max_forward_speed(self.max_forward_speed_random)

        if self.is_chasing:
            self.chase_car(car)
        else:
            self.chase_random_point()

    def is_near(self, car):
        point1 = self.get_position()
        point2 = car.get_position()
        if pygame.Vector2(point1).distance_to(point2) > self.max_detect_radius:
            return False
        ray = RayCastCallback(b2_coords(point1) / PPM, b2_coords(point2) / PPM)
        self.world.RayCast(ray, b2_coords(point1) / PPM, b2_coords(point2) / PPM)
        ray_report = ray.reports[-1]
        ray_report: RayFixtureReport

        if ray_report:
            data = ray_report.fixture.body.userData
            if data == car:
                return b2_coords(ray_report.point) * PPM
        return False

    def reached_point(self, point):
        return pygame.Vector2(self.get_position()).distance_to(point) < 100

    def chase_car(self, car):
        point = car.get_position()
        if self.way_timer > self.way_timeout:
            self.way_timer = 0
            self.way.append(point)
        for i in range(len(self.way) - 2, -1, -1):
            if self.reached_point(self.way[i]):
                self.way = self.way[i + 1:]
                break
        if self.way:
            self.chase_point(self.way[0])

    def chase_random_point(self):
        if not self.way or self.reached_point(self.way[0]):
            self.way = self.way[1:]
            self.way.append(self.get_random_point())
        self.chase_point(self.way[0])

    def get_random_point(self):
        rand_vec = pygame.Vector2(random.uniform(-1, 1),
                                  random.uniform(-1, 1))
        rand_vec *= 300

        point1: b2Vec2 = b2_coords(self.get_position()) / PPM
        point2 = point1 + b2_coords(rand_vec) / PPM
        ray = RayCastCallback(point1, point2)
        self.world.RayCast(ray, point1, point2)
        if ray.reports:
            ray_report = ray.reports[-1]
            point2 = ray_report.point
        return b2_coords(point2) * PPM

    def chase_point(self, point):
        up, down = C_UP, C_DOWN
        if self.reverse:
            up, down = down, up

        self.control_state &= ~down
        self.control_state |= up

        if self.get_velocity().length > 3:
            point1 = self.get_position() + self.get_velocity()
            point2 = self.get_position()
            turn = triangle_area(*point, *point1, *point2)
            angle = (pygame.Vector2(point1) - pygame.Vector2(point2)).angle_to(
                (pygame.Vector2(point) - pygame.Vector2(point2)))
            angle = min(angle, angle - 360, 360 - angle, key=abs)

            if pygame.Vector2(point).distance_to(self.get_position()) < 50:
                self.control_state &= ~C_RIGHT
                self.control_state &= ~C_LEFT
                self.control_state &= ~C_UP
                self.control_state &= ~C_DOWN
            elif turn > 0 and abs(angle) > 5:
                self.control_state |= C_LEFT
                self.control_state &= ~C_RIGHT
            elif abs(angle) > 5:
                self.control_state |= C_RIGHT
                self.control_state &= ~C_LEFT

        for tire in self.tires:
            tire.set_control_state(self.control_state)

    def set_max_forward_speed(self, value):
        self.max_forward_speed = value
        for i in self.tires:
            i.max_forward_speed = value

    def update(self, dt: float, events):
        super().update(dt, events)

        self.prev_pos_timer += dt
        if self.prev_pos_timer > 0.5:
            self.prev_pos_timer = 0
            if self.prev_pos:
                dist = pygame.Vector2(self.get_position()).distance_to(self.prev_pos)
                if dist < 5:
                    self.reverse = True
            self.prev_pos = self.get_position()

        if self.reverse:
            self.timer_reverse += dt
            if self.timer_reverse > 1:
                self.timer_reverse = 0
                self.reverse = False

        self.way_timer += dt
        self.detected_timer += dt
        self.ray_cast_timer += dt
        self.chase_point_timer += dt

    def break_down(self):
        super().break_down()
        self.is_chasing = False
        self.player.on_police_break()

    def on_explosion(self, obj_from, power):
        if not self.is_broken and type(obj_from) == FireballExplosion:
            if power > 65:
                self.hits.add(obj_from)
                if len(self.hits) >= 3:
                    self.break_down()
