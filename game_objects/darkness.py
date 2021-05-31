import math
import pygame
from Box2D import *
from PIL import Image, ImageFilter

from configurations import *
from game_objects.game_object import GameObject
from game_objects.player_car.player_car import PlayerCar
from resources import Resources
from sprites.camera import Camera
from sprites.sprite import Group
from utils.contact_listener import ContactListener
from utils.ray_cast_callback import RayCastCallback, RayFixtureReport
from utils.utils import bound, image2pil, pil2image, b2_coords


class Darkness(GameObject):
    layer = 2

    def __init__(self, world: b2World, cl: ContactListener, res: Resources,
                 player_car: PlayerCar, camera: Camera, game_object_group: Group, *groups):
        super().__init__(world, cl, game_object_group, *groups, connects=False)
        self.ignore_ray_casting = True
        self.draw_shadow = False
        self.is_ui = True
        self.player_car = player_car
        self.camera = camera

        self.rect = pygame.Rect((0, 0, WIDTH, HEIGHT))
        self.image = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
        self.image.fill((0, 0, 0, 0))

        self.color = 50, 50, 50
        self.max_alpha = 220
        self.value = 0
        self.enabled = False
        self.timeout = 1.5

        # create circle
        width = 250
        border = 50
        circle = pygame.Surface((width, width)).convert_alpha()
        circle.fill((0, 0, 0, 0))
        pygame.draw.circle(circle, (0, 0, 0, 255), (width // 2, width // 2), width // 2)
        pil_im = image2pil(circle)
        new = Image.new('RGBA', (pil_im.width + 2 * border, pil_im.height + 2 * border),
                        color=(0, 0, 0, 0))
        new.paste(pil_im, (border, border))
        image_filter: ImageFilter = ImageFilter.GaussianBlur(12)
        new = new.filter(image_filter)
        self.circle = pil2image(new)

        self.center = self.image.get_width() / 2 - self.circle.get_width() / 2, \
                      self.image.get_height() / 2 - self.circle.get_height() / 2

        self.ray_cast_timer = 0
        self.ray_cast_timeout = 1 / 3
        self.count_rays = 25
        self.ray_cast_radius = int(((WIDTH // 2) ** 2 + (HEIGHT // 2) ** 2) ** 0.5) + 200
        self.rays = [None for _ in range(self.count_rays)]
        self.previous_camera_pos = None

    def set_center(self):
        cx, cy = self.camera.get_position() - self.player_car.get_position()
        self.center = self.image.get_width() / 2 - cx, \
                      self.image.get_height() / 2 - cy

    def get_rays(self):
        pos = self.player_car.get_position()
        rays = []
        direction = pygame.Vector2(1, 0)
        rotate_angle = 360 / self.count_rays
        for i in range(self.count_rays):
            start_point = b2_coords(pos) / PPM
            end_point = b2_coords(direction * self.ray_cast_radius) / PPM + start_point
            ray = RayCastCallback(start_point, end_point)
            self.world.RayCast(ray, start_point, end_point)
            rays.append(ray)
            direction = direction.rotate(rotate_angle)
        k = 0
        for i in rays:
            if not i.reports:
                self.rays[k] = b2_coords(i.start) * PPM, b2_coords(i.end) * PPM
            else:
                last_report: RayFixtureReport = i.reports[-1]
                self.rays[k] = b2_coords(i.start) * PPM, b2_coords(last_report.point) * PPM
            k += 1

    def set_enabled(self, value):
        self.enabled = value
        if value:
            self.get_rays()

    def update(self, dt: float, events):

        for i in events:
            if i.type == pygame.KEYDOWN:
                if i.key == pygame.K_F10:
                    self.set_enabled(not self.enabled)

        self.value += dt / self.timeout * (int(self.enabled) * 2 - 1)
        self.value = bound(self.value, 0, 1)

        if self.value:
            self.ray_cast_timer += dt
        if self.ray_cast_timer >= self.ray_cast_timeout:
            self.ray_cast_timer -= self.ray_cast_timeout
            self.get_rays()

    def render(self):
        self.image.fill((*self.color, self.value * self.max_alpha))
        self.image.blit(self.circle, (self.center[0] - self.circle.get_width() / 2,
                                      self.center[1] - self.circle.get_height() / 2),
                        None, pygame.BLEND_RGBA_SUB)
        if self.value:
            points = []
            for i in self.rays:
                if i is None:
                    continue
                start, end = self.camera.camera_shift * -1 + pygame.Vector2(
                    *i[0]), self.camera.camera_shift * -1 + pygame.Vector2(*i[1])
                # pygame.draw.line(self.image, (0, 0, 0, 0), start, end, width=3)
                points.append(end)
            if len(points) > 2:
                pygame.draw.polygon(self.image, (0, 0, 0, 0), points)
