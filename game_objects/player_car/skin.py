from resources import Resources
from utils.utils import paint_images


class CarSkin:
    def __init__(self, res: Resources, image_car):
        self.image_tire = paint_images([res.image_tire], lambda x: (61, 67, 71, x[3]))[0]
        self.image_car = image_car
