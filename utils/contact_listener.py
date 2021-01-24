from collections import defaultdict
from Box2D import b2ContactListener

from utils.utils import get_data


class ContactListener(b2ContactListener):
    """Для столкновений в библеотеке Box2D"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connects_begin = defaultdict(list)
        self.connects_end = defaultdict(list)
        self.connects_pre = defaultdict(list)
        self.connects_post = defaultdict(list)

    def connect_begin_contact(self, game_object):
        self.connects_begin[game_object].append(game_object.begin_contact)

    def connect_end_contact(self, game_object):
        self.connects_end[game_object].append(game_object.end_contact)

    def connect_pre_solve(self, game_object):
        self.connects_pre[game_object].append(game_object.pre_solve)

    def connect_post_solve(self, game_object):
        self.connects_post[game_object].append(game_object.post_solve)

    def BeginContact(self, contact):
        for body in get_data(contact):
            for i in self.connects_begin[body]:
                i(contact)

    def EndContact(self, contact):
        for body in get_data(contact):
            for i in self.connects_end[body]:
                i(contact)

    def PreSolve(self, contact, manifold):
        for body in get_data(contact):
            for i in self.connects_pre[body]:
                i(contact, manifold)

    def PostSolve(self, contact, impulse):
        for body in get_data(contact):
            for i in self.connects_post[body]:
                i(contact, impulse)
