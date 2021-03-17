import pygame


class Sprite(pygame.sprite.Sprite):
    layer = 0

    def __init__(self, *groups):
        super(Sprite, self).__init__(*groups)
        self.init_image = pygame.Surface((0, 0))
        self.image = self.init_image
        self.rect = pygame.Rect(0, 0, 0, 0)

    def update(self, dt: float, events):
        """Updating sprites"""
        ...

    def render(self):
        """Function calling before drawing
        It is not really render, it is just process before drawing"""
        ...

    def dispose(self):
        """Called before removing sprite from the scene"""
        del self.image
        del self.init_image

    def add(self, group: pygame.sprite.LayeredUpdates):
        group.add(self, layer=self.layer)

    def set_init_image(self, image: pygame.Surface):
        self.init_image = image.copy()
        self.image = self.init_image
        self.rect = pygame.Rect((0, 0), self.image.get_size())

    def get_init_image(self):
        return self.init_image

    @staticmethod
    def rotate_image_center(rect, angle, image):
        """Rotates image over center"""
        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(center=rect.center)
        return new_rect, rotated_image


class Group(pygame.sprite.LayeredUpdates):
    def update(self, dt: float, events: list) -> None:
        super().update(dt, events)

    def draw(self, surface: pygame.Surface) -> None:
        self.render_sprites()
        super().draw(surface)

    def render_sprites(self):
        for sprite in self.sprites():
            sprite: Sprite
            sprite.render()

    def add(self, *sprites, layer=None) -> None:
        for i in sprites:
            if not isinstance(i, Sprite):
                print(type(i))
                raise TypeError('Object must be instance of Sprite')
        super(Group, self).add(*sprites, layer=layer)
