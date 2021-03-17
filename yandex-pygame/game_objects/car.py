import math

import pygame
from Box2D import *

from game_objects.explosion import Explosion
from game_objects.player_car.skin import CarSkin
from game_objects.game_object import GameObject
from utils.utils import b2_coords, paint_images
from utils.b2_factory import B2Factory
from constants import *
from game_objects.ground import Ground
from game_objects.tire import Tire, C_RIGHT, C_LEFT, C_UP, C_DOWN


class Car(GameObject):
    layer = 2
    size = 58, 96
    tire_shift = 28.8, 27.2

    def __init__(self, world, cl, res, skin: CarSkin, pos, angle,
                 game_object_group, *groups):
        super().__init__(world, cl, game_object_group, *groups)

        self.res = res
        self.set_init_image(skin.image_car)
        self.rect = pygame.Rect(pos, self.size)

        self.control_state = 0
        self.color_particles = 50, 50, 50

        # Default characteristics
        # Power characteristics
        self.max_forward_speed = 30
        self.max_backward_speed = -12
        self.max_drive_force = 30
        # Control characteristics
        self.max_lateral_impulse = 0.5
        self.angular_friction_impulse = 0.2
        self.linear_friction_impulse = 0.3

        self.lock_angle = math.radians(35)
        self.speed_tire_rotate = math.radians(180)

        # Body characteristics
        self.density = 1
        self.restitution = 0.02
        self.friction = 0.2

        self.tire_density = 3
        self.tire_restitution = 0.1
        self.tire_friction = 1

        s = b2Vec2(self.rect.size) / 2 / PPM
        box_vert = [
            (-s[0], -s[1]),
            (-s[0] / 2, s[1]),
            (s[0] / 2, s[1]),
            (s[0], -s[1])
        ]

        shape = b2PolygonShape()
        shape.vertices = box_vert
        fd = B2Factory.create_fixture(shape, self.density, self.restitution, self.friction)
        self.body = B2Factory.create_body(world, b2_dynamicBody, fd, b2_coords(pos) / PPM)
        self.body.userData = self
        self.body.angle = math.radians(angle)
        self.body.angularDamping = 0.3

        # Add tires
        def _create_tire(delta, jd):
            tire = Tire(world, self.cl, skin.image_tire, self,
                        self.max_forward_speed, self.max_backward_speed,
                        self.max_drive_force, self.max_lateral_impulse,
                        self.angular_friction_impulse, self.linear_friction_impulse,
                        self.tire_density, self.tire_restitution, self.tire_friction,
                        self.game_object_group)
            tire.body.position = self.body.GetWorldPoint(delta)
            tire.body.angle = self.body.angle
            jd.bodyB = tire.body
            jd.localAnchorA = delta
            return tire, jd

        jd = b2RevoluteJointDef()
        jd.bodyA = self.body
        jd.enableLimit = True
        jd.lowerAngle = 0
        jd.upperAngle = 0
        jd.localAnchorA.SetZero()
        shift = b2Vec2(self.tire_shift) / PPM

        # ForwardLeft, ForwardRight, BackwardLeft, BackwardRight
        self.tires = []
        self.joints = []

        for i in [(-shift.x, shift.y), (shift.x, shift.y),
                  (-shift.x, -shift.y), (shift.x, -shift.y)]:
            tire, jd = _create_tire(b2Vec2(i), jd)
            self.tires.append(tire)
            self.joints.append(world.CreateJoint(jd))

        self.is_broken = False
        self.broken_timer = 0
        self.dispose_timeout = 5

    def set_characteristics(self, max_forward_speed, max_backward_speed,
                            max_drive_force, max_lateral_impulse,
                            angular_friction_impulse, linear_friction_impulse):
        self.max_forward_speed = max_forward_speed
        self.max_backward_speed = max_backward_speed
        self.max_drive_force = max_drive_force
        self.max_lateral_impulse = max_lateral_impulse
        self.angular_friction_impulse = angular_friction_impulse
        self.linear_friction_impulse = linear_friction_impulse
        for i in self.tires:
            i.set_characteristics(max_forward_speed, max_backward_speed,
                                  max_drive_force, max_lateral_impulse,
                                  angular_friction_impulse, linear_friction_impulse)

    def set_acceleration(self, acceleration_time, min_acc):
        for i in self.tires:
            i.set_acceleration(acceleration_time, min_acc)

    def get_position(self):
        return b2_coords(self.body.position) * PPM

    def set_position(self, position):
        self.body.position = b2_coords(position) / PPM
        for i in self.tires:
            i.body.position = b2_coords(position) / PPM

    def get_velocity(self):
        return b2_coords(self.body.linearVelocity) * PPM

    def get_angle(self):
        return math.degrees(self.body.angle)

    def get_vector(self):
        angle = math.radians(self.get_angle())
        return pygame.Vector2(math.sin(angle), math.cos(angle)) * -1

    def get_left_right_control(self):
        return self.control_state & (C_LEFT | C_RIGHT)

    def get_up_down_control(self):
        return self.control_state & (C_UP | C_DOWN)

    def tire_contact(self, contact: b2Contact, begin):
        data_a = contact.fixtureA.body.userData
        data_b = contact.fixtureB.body.userData

        if type(data_a) == Tire and type(data_b) == Ground:
            ...
        elif type(data_b) == Tire and type(data_a) == Ground:
            data_a, data_b = data_b, data_a
        else:
            return
        tire = data_a
        ground = data_b
        if begin:
            tire.add_ground(ground)
        else:
            tire.remove_ground(ground)

    def begin_contact(self, contact: b2Contact):
        self.tire_contact(contact, True)

    def end_contact(self, contact: b2Contact):
        self.tire_contact(contact, False)

    def update(self, dt: float, events):
        if self.is_broken:
            self.broken_timer += dt
            if self.broken_timer > self.dispose_timeout:
                for i in self.tires:
                    particles = paint_images(
                        self.res.explosion_particles, lambda x: (0, 0, 0, x[3]))
                    Explosion.spawn_particles(self.world, self.cl, self.res,
                                              b2_coords(i.body.position) * PPM, particles, 3, 2,
                                              self.game_object_group)
                    i.dispose()
                particles = paint_images(
                    self.res.explosion_particles, lambda x: (*self.color_particles, x[3]))
                Explosion.spawn_particles(self.world, self.cl, self.res,
                                          b2_coords(self.body.position) * PPM, particles, 7, 10,
                                          self.game_object_group)
                self.dispose()
            return

        # Update turn
        curr_angle = self.joints[0].angle

        v = self.control_state & (C_LEFT | C_RIGHT)
        desired_angle = 0
        if v == C_LEFT:
            desired_angle = self.lock_angle
        elif v == C_RIGHT:
            desired_angle = -self.lock_angle
        turn = desired_angle - curr_angle
        if abs(turn) > self.speed_tire_rotate / 2 * dt:
            if turn > 0:
                turn = self.speed_tire_rotate * dt
            else:
                turn = -self.speed_tire_rotate * dt
        else:
            turn = 0

        new_angle = curr_angle + turn
        if new_angle > self.lock_angle * 2:
            new_angle = 0
        self.joints[0].SetLimits(new_angle, new_angle)
        self.joints[1].SetLimits(new_angle, new_angle)

    def render(self):
        self.set_rotated_sprite(self.body, self.get_init_image())

    def break_down(self):
        if self.is_broken:
            return
        self.is_broken = True
        for i in self.joints:
            self.world.DestroyJoint(i)
        for i in self.tires:
            i: Tire
            i.body.linearDamping = 2
            i.body.angularDamping = 2
            i.control_state = 0
            i.ignore_ray_casting = True
            impulse = pygame.Vector2(i.body.position - self.body.position)
            impulse = impulse.normalize() * 2
            i.body.ApplyLinearImpulse(impulse, i.body.GetWorldPoint((0, 0)), True)
        self.body.linearDamping = 5
        self.body.angularDamping = 5
        # Более темное изображение после уничтожения
        self.init_image = paint_images([self.init_image], lambda x:
        (*map(lambda a: max(0, a - 50), x[:3]), x[3]))[0]

    def dispose(self):
        super().dispose()
        self.world.DestroyBody(self.body)
