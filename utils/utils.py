import pygame
from Box2D import *
from PIL import Image


def paint_images(images, pixel_func):
    res = []
    for im in images:
        pil_im = image2pil(im)
        pix = pil_im.load()
        w, h = pil_im.size
        for i in range(w):
            for j in range(h):
                pix[i, j] = pixel_func(pix[i, j])
        res.append(pil2image(pil_im))
    return res


def pil2image(pil_im):
    raw_str = pil_im.tobytes('raw', 'RGBA')
    return pygame.image.fromstring(
        raw_str, pil_im.size, 'RGBA').convert_alpha()


def image2pil(im):
    raw_str = pygame.image.tostring(im, 'RGBA')
    return Image.frombytes('RGBA', im.get_size(), raw_str)


def get_data(contact: b2Contact):
    data_a = contact.fixtureA.body.userData
    data_b = contact.fixtureB.body.userData
    return data_a, data_b


def b2_coords(b2_pos):
    b2_pos = b2Vec2(b2_pos)
    return b2Vec2(b2_pos.x, -b2_pos.y)


def bound(value, a, b):
    return min(max(value, a), b)


def triangle_area(x1, y1, x2, y2, x3, y3):
    return (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)
