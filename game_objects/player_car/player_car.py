import pygame
from Box2D import *

from constants import *
from game_objects.bank import LootArea
from game_objects.energy_item import EnergyItem
from game_objects.turret.bullet import Bullet
from resources import Resources
from game_objects.fireball import Fireball, FireballExplosion
from game_objects.bomb import Bomb, BombExplosion
from game_objects.car import Car
from game_objects.player_car.popup_line import PopupLine
from game_objects.player_car.tire_particle import TireParticle
from game_objects.police import Police
from game_objects.tire import Tire, C_LEFT, C_RIGHT, C_UP, C_DOWN
from game_objects.wall.base_wall import BaseWall
from sound_manager import SoundManager
from utils.utils import b2_coords, get_data
from utils.utils import bound


class PlayerCar(Car):
    def __init__(self, world, cl, res: Resources, sm: SoundManager,
                 skin, pos, angle, camera,
                 game_object_group, *groups):

        super().__init__(world, cl, res, skin, pos, angle,
                         game_object_group, *groups)

        self.res = res
        self.sm = sm
        self.camera = camera

        max_forward_speed = 25
        max_backward_speed = -12
        max_drive_force = 30
        max_lateral_impulse = 0.45
        angular_friction_impulse = 0.3
        linear_friction_impulse = 0.2

        self.set_characteristics(
            max_forward_speed, max_backward_speed,
            max_drive_force, max_lateral_impulse,
            angular_friction_impulse, linear_friction_impulse)
        for i in self.tires:
            i.ignore_ray_casting = True

        # Drifting and particles config
        self.draw_particles = True
        self.particles_timer = 0
        self.default_particles_timeout = 0.2
        self.particles_timeout = self.default_particles_timeout
        self.timeout_coeff = 3
        self.min_lateral_v_drifting = 100
        self.drifting_timer = 0
        self.drifting_timeout = 0.65
        self.multiply_drifting = 0
        self.is_on_police_chase = False

        # Bank
        self.bank_timer = 0
        self.bank_timeout = 10
        self.bank_timeout_timers = [3, 5, 7, 9]
        self.bank_timeout_messages = ['30%...', '50%...', '70%...', '90%...']
        self.bank_timeout_state = 0
        self.is_bank_loot = False
        self.looted = False
        self.dollars = 0

        # Popup line delay
        self.queue_lines = []
        self.lines_timer = 0
        self.lines_timeout = 0.3

        # Энергия
        self.energy = 1
        self.drift_energy = 0.1
        self.item_energy = 0.2

    def update(self, dt: float, events):
        super().update(dt, events)

        # Всплывающие надписи
        if len(self.queue_lines) >= 5:
            self.queue_lines = self.queue_lines[-5:]
        if not self.lines_timer and self.queue_lines:
            PopupLine(self.world, self.cl, self.res,
                      self, self.queue_lines.pop(0), self.game_object_group)
        self.lines_timer += dt
        if self.lines_timer >= self.lines_timeout:
            self.lines_timer = 0

        if self.is_broken:
            return

        if self.get_velocity().length > 30 and \
                self.get_up_down_control() == C_UP:
            self.sm.set_playing(self.res.sound_drive, fade_ms=1000)
        else:
            self.sm.stop_playing(self.res.sound_drive, fade_ms=1000)

        # Timers update
        self.drifting_timer = bound(self.drifting_timer, 0, self.drifting_timeout)
        if self.drifting_timer >= self.drifting_timeout:
            self.drifting_timer = 0
            self.on_drift()

        # Spawn particles
        self.particles_timer += dt
        self.particles_timer = bound(self.particles_timer, 0, self.particles_timeout)
        if self.particles_timer >= self.particles_timeout:
            self.particles_timer = 0
            lateral_v = 0
            for tire in self.tires[2:]:
                lateral_v = tire.get_lateral_velocity().length * PPM
                if lateral_v > self.min_lateral_v_drifting:
                    if self.draw_particles:
                        self.spawn_particle(tire)
                        self.particles_timeout = self.timeout_coeff / lateral_v
                else:
                    self.particles_timeout = self.default_particles_timeout
                    self.drifting_timer = 0
                    self.multiply_drifting = 0

            if lateral_v > self.min_lateral_v_drifting:
                if self.get_up_down_control() != C_DOWN:
                    self.sm.set_playing(self.res.sound_drift, fade_ms=1000)
                    self.drifting_timer += dt
            else:
                self.sm.stop_playing(self.res.sound_drift, fade_ms=1000)

        self.energy = bound(self.energy, 0, 1)
        if self.is_bank_loot:
            self.bank_timer += dt
            if not self.looted and self.bank_timer > self.bank_timeout:
                self.looted = True
                self.dollars += 500
                self.queue_lines.append('Банк ограблен :)')
                self.queue_lines.append('+ 500 $')
                self.queue_lines.append(f'Итог: {self.dollars} $')
            if self.bank_timeout_state < len(self.bank_timeout_timers) and \
                    self.bank_timer > self.bank_timeout_timers[self.bank_timeout_state]:
                self.queue_lines.append(self.bank_timeout_messages[self.bank_timeout_state])
                self.bank_timeout_state += 1

    def set_police_chase(self, value):
        self.is_on_police_chase = value

    def spawn_fireball(self, vector):
        if self.waste_energy(0.03):
            fb = Fireball(self.world, self.cl, self.res,
                          self, vector, self.fireball_callback, self.game_object_group)

            self.sm.play(self.res.sound_lazer)

    def fireball_callback(self):
        self.camera.shake(0.5, 60)
        self.sm.play(self.res.sound_boom)

    def spawn_bomb(self):
        if self.waste_energy(0.1):
            bomb = Bomb(self.world, self.cl, self.res, self,
                        self.bomb_explosion_callback, self.game_object_group)

    def bomb_explosion_callback(self):
        self.camera.shake(0.6, 90)
        self.sm.play(self.res.sound_boom)

    def teleport(self, distance):
        teleport_shift = pygame.Vector2(0, -distance).rotate(-self.get_angle())
        self.set_position(self.get_position() + teleport_shift)

    def spawn_particle(self, tire):
        p = TireParticle(self.world, self.cl,
                         self.res, b2_coords(tire.body.position) * PPM, self.game_object_group)
        p.body.ApplyLinearImpulse(tire.get_lateral_velocity() * -1 * 0.1,
                                  tire.body.GetWorldPoint((0, 0)), True)

    def on_drift(self):
        if self.is_on_police_chase:
            self.multiply_drifting += 1
            self.energy += self.drift_energy + 0.05 * self.multiply_drifting
            self.queue_lines.append(f'Дрифт {self.multiply_drifting}Х!')

    def on_wall_collide(self):
        self.energy -= 0.05
        self.queue_lines.append('Стена')

    def on_police_collide(self):
        self.energy -= 0.1
        self.queue_lines.append('Полиция')
        self.bank_timer = 0

    def on_fireball_damage(self):
        # self.energy -= 0.1
        # self.queue_lines.append('Урон от фаерболла')
        ...

    def on_bomb_damage(self):
        self.energy -= 0.2
        self.queue_lines.append('Урон от бомбы')

    def on_turret_damage(self):
        self.energy -= 0.1
        self.queue_lines.append('Урон от турели')

    def on_energy_collect(self):
        self.energy += self.item_energy
        self.queue_lines.append('Энерия')

    def waste_energy(self, energy):
        if energy >= self.energy:
            self.queue_lines.append('Недостаточно энергии')
            return False
        self.energy -= energy
        return True

    def on_police_break(self):
        self.queue_lines.append('+ 100 $')
        self.dollars += 100

    def begin_contact(self, contact: b2Contact):
        super().begin_contact(contact)
        data_a, data_b = get_data(contact)

        if type(data_a) == EnergyItem or type(data_b) == EnergyItem:
            if type(data_b) == EnergyItem:
                data_a, data_b = data_b, data_a
            if data_a.collect():
                self.on_energy_collect()
        elif type(data_a) == LootArea or type(data_b) == LootArea:
            if (data_a == self or data_b == self) and not self.is_bank_loot:
                self.is_bank_loot = True
                self.queue_lines.append('Начинаем грабить банк :)')

    def end_contact(self, contact: b2Contact):
        super().end_contact(contact)
        data_a, data_b = get_data(contact)

        if type(data_a) == LootArea or type(data_b) == LootArea:
            if (data_a == self or data_b == self) and \
                    self.is_bank_loot and not self.looted:
                self.is_bank_loot = False
                self.bank_timeout_state = 0
                self.bank_timer = 0
                self.queue_lines.append('Вы вышли из зоны грабежа :(')

    def post_solve(self, contact: b2Contact, impulse: b2ContactImpulse):
        super().post_solve(contact, impulse)
        data_a, data_b = get_data(contact)

        impulse = abs(sum(impulse.normalImpulses))
        if isinstance(data_b, BaseWall) or isinstance(data_a, BaseWall):
            if impulse > 60:
                self.on_wall_collide()
        elif (type(data_a) == Police and not data_a.is_broken) or \
                (type(data_b) == Police and not data_b.is_broken) or \
                (type(data_a) == Tire and type(data_a.car) == Police
                 and not data_a.car.is_broken) or \
                (type(data_b) == Tire and type(data_b.car) == Police
                 and not data_b.car.is_broken):
            if impulse > 20:
                self.on_police_collide()

    def on_explosion(self, obj_from, power):
        if type(obj_from) == FireballExplosion:
            if power > 100:
                self.on_fireball_damage()
        elif type(obj_from) == BombExplosion:
            if power > 75:
                self.on_bomb_damage()
        elif type(obj_from) == Bullet:
            self.on_turret_damage()

    def update_control(self, events, only_move=False):
        for i in events:
            if i.type == pygame.KEYDOWN:
                if i.key == pygame.K_a:
                    self.control_state |= C_LEFT
                elif i.key == pygame.K_d:
                    self.control_state |= C_RIGHT
                elif i.key == pygame.K_w:
                    self.control_state |= C_UP

                    if self.get_velocity().length < 30:
                        self.sm.play(self.res.sound_start_car)

                elif i.key == pygame.K_s:
                    self.control_state |= C_DOWN
            elif i.type == pygame.KEYUP:
                if i.key == pygame.K_a:
                    self.control_state &= ~C_LEFT
                elif i.key == pygame.K_d:
                    self.control_state &= ~C_RIGHT
                elif i.key == pygame.K_w:
                    self.control_state &= ~C_UP
                elif i.key == pygame.K_s:
                    self.control_state &= ~C_DOWN

        for tire in self.tires:
            tire.set_control_state(self.control_state)

        if not only_move:
            for i in events:
                if i.type == pygame.KEYDOWN:
                    if i.key == pygame.K_t:
                        # self.teleport(150)
                        ...
                    elif i.key == pygame.K_b:
                        self.spawn_bomb()
                    elif i.key == pygame.K_f:
                        self.spawn_fireball(self.get_vector())
                elif i.type == pygame.MOUSEBUTTONDOWN:
                    if i.button == pygame.BUTTON_LEFT:
                        self.spawn_fireball(pygame.Vector2(i.pos) - pygame.Vector2(WIDTH, HEIGHT) / 2)
