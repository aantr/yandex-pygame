import pygame
from Box2D import *
from PIL import Image


def paint_images(images, pixel_func):
    res = []
    for im in images:
        str_format = 'RGBA'
        # image2pil
        raw_str = pygame.image.tostring(im, str_format)
        pil_im = Image.frombytes(str_format, im.get_size(), raw_str)
        pix = pil_im.load()
        w, h = pil_im.size
        for i in range(w):
            for j in range(h):
                pix[i, j] = pixel_func(pix[i, j])
        # pil2image
        raw_str = pil_im.tobytes('raw', str_format)
        res.append(pygame.image.fromstring(
            raw_str, pil_im.size, str_format).convert_alpha())
    return res


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
