import pygame
from Box2D import *
from game_objects.game_object import GameObject
from utils.utils import b2_coords
from utils.b2_factory import B2Factory
from constants import *

# Tire control
C_LEFT = 0x1
C_RIGHT = 0x2
C_UP = 0x4
C_DOWN = 0x8


class Tire(GameObject):
    """Car wheel with characteristics"""
    layer = 1

    def __init__(self, world, cl,
                 image, car, max_forward_speed, max_backward_speed,
                 max_drive_force, max_lateral_impulse,
                 angular_friction_impulse, linear_friction_impulse,
                 density, restitution, friction, game_object_group, *groups):
        super().__init__(world, cl, game_object_group, *groups)

        size = 10, 24
        self.car = car
        self.set_init_image(image)
        self.rect = pygame.Rect((0, 0), size)

        shape = b2PolygonShape()
        shape.SetAsBox(*b2Vec2(*self.rect.size) / 2 / PPM)
        fd = B2Factory.create_fixture(shape, density, restitution, friction)
        self.body = B2Factory.create_body(world, b2_dynamicBody, fd,
                                          b2_coords(self.rect.center) / PPM)
        self.body.userData = self

        self.control_state = 0
        self.current_traction = 1
        self.grounds = []

        self.acceleration_time = 1
        self.min_acc = 0.3
        self.acceleration = self.min_acc

        self.set_characteristics(max_forward_speed, max_backward_speed,
                                 max_drive_force, max_lateral_impulse,
                                 angular_friction_impulse, linear_friction_impulse)

    def set_characteristics(self, max_forward_speed, max_backward_speed,
                            max_drive_force, max_lateral_impulse,
                            angular_friction_impulse, linear_friction_impulse):
        self.max_forward_speed = max_forward_speed
        self.max_backward_speed = max_backward_speed
        self.max_drive_force = max_drive_force

        self.max_lateral_impulse = max_lateral_impulse
        self.angular_friction_impulse = angular_friction_impulse
        self.linear_friction_impulse = linear_friction_impulse

    def set_acceleration(self, acceleration_time, min_acc):
        self.acceleration_time = acceleration_time
        self.min_acc = min_acc
        self.acceleration = self.min_acc

    def add_ground(self, g):
        self.grounds.append(g)
        self.update_traction()

    def remove_ground(self, g):
        self.grounds.remove(g)
        self.update_traction()

    def update_traction(self):
        if not self.grounds:
            self.current_traction = 1
        else:
            # find area with highest traction
            self.current_traction = 0
            for g in self.grounds:
                if g.friction_modifier > self.current_traction:
                    self.current_traction = g.friction_modifier

    def get_lateral_velocity(self):
        normal = self.body.GetWorldVector(b2Vec2(1, 0))
        return b2Dot(normal, self.body.linearVelocity) * normal

    def get_forward_velocity(self):
        normal = self.body.GetWorldVector(b2Vec2(0, 1))
        return b2Dot(normal, self.body.linearVelocity) * normal

    def update_friction(self, dt):
        # lateral linear velocity
        max_lateral_impulse = self.max_lateral_impulse
        impulse = self.body.mass * -self.get_lateral_velocity()
        if impulse.length > max_lateral_impulse:
            impulse *= max_lateral_impulse / impulse.length
        self.body.ApplyLinearImpulse(self.current_traction * impulse
                                     * dt * 80,
                                     self.body.GetWorldPoint((0, 0)), True)
        # angular velocity
        self.body.ApplyAngularImpulse(self.current_traction * self.angular_friction_impulse
                                      * dt * 80 * self.body.inertia *
                                      -self.body.angularVelocity, True)
        # forward linear velocity
        current_forward_normal = self.get_forward_velocity()
        current_forward_speed = current_forward_normal.Normalize()
        dragForceMagnitude = -2 * current_forward_speed
        self.body.ApplyForce(self.current_traction * dragForceMagnitude * self.linear_friction_impulse *
                             current_forward_normal, self.body.GetWorldPoint((0, 0)), True)

    def update_drive(self, dt):
        # find desired speed
        desired_speed = 0
        v = self.control_state & (C_UP | C_DOWN)
        if v == C_UP:
            desired_speed = self.max_forward_speed
            self.acceleration += dt / self.acceleration_time
        elif v == C_DOWN:
            desired_speed = self.max_backward_speed
            self.acceleration += dt / self.acceleration_time
        else:
            if self.acceleration > self.min_acc:
                self.acceleration -= dt / self.acceleration_time
            else:
                self.acceleration = self.min_acc
        if self.acceleration > 1:
            self.acceleration = 1

        # find current speed in forward direction
        current_forward_normal = self.body.GetWorldVector(b2Vec2(0, 1))
        current_speed = b2Dot(self.get_forward_velocity(), current_forward_normal)

        force = 0
        if desired_speed > current_speed:
            force = self.max_drive_force
        elif desired_speed < current_speed:
            force = -self.max_drive_force

        self.body.ApplyForce(self.current_traction * force * current_forward_normal *
                             self.acceleration,
                             self.body.GetWorldPoint((0, 0)), True)

    def set_control_state(self, cs):
        self.control_state = cs

    def update(self, dt: float, events):
        if self.car.is_broken:
            return
        self.update_friction(dt)
        self.update_drive(dt)

    def render(self):
        self.set_rotated_sprite(self.body, self.get_init_image())

    def begin_contact(self, contact: b2Contact):
        self.car.begin_contact(contact)

    def end_contact(self, contact: b2Contact):
        self.car.end_contact(contact)

    def pre_solve(self, contact: b2Contact, old_manifold: b2Manifold):
        self.car.pre_solve(contact, old_manifold)

    def post_solve(self, contact: b2Contact, impulse: b2ContactImpulse):
        self.car.post_solve(contact, impulse)

    def on_explosion(self, obj_from, power):
        self.car.on_explosion(obj_from, power)

    def dispose(self):
        super().dispose()
        self.world.DestroyBody(self.body)
