from Box2D import b2RayCastCallback
from game_objects.game_object import GameObject


class RayCastCallback(b2RayCastCallback):
    def __init__(self, start, end):
        super().__init__()
        self.start = start
        self.end = end
        self.reports = []

    def ReportFixture(self, fixture, point, normal, fraction):
        if not isinstance(fixture.body.userData, GameObject) or \
                fixture.body.userData.ignore_ray_casting:
            # If ray collide not GameObject or ignore_ray_casting, then ignore
            return -1
        self.reports.append(RayFixtureReport(fixture, point, normal, fraction))
        return fraction


class RayFixtureReport:
    def __init__(self, fixture, point, normal, fraction):
        self.fixture = fixture
        self.point = point
        self.normal = normal
        self.fraction = fraction
