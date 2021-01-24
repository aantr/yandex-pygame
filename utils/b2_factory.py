from Box2D import b2World, b2Vec2, b2Body, b2BodyDef, b2FixtureDef


class B2Factory:
    @staticmethod
    def create_body(world: b2World, body_type, fixture_def, position=b2Vec2(0, 0)) -> b2Body:
        body_def = b2BodyDef()
        body_def.type = body_type
        body_def.position = position

        body = world.CreateBody(body_def)
        body.CreateFixture(fixture_def)

        return body

    @staticmethod
    def create_fixture(shape, density=0, friction=0.2, restitution=0, is_sensor=False):
        fd = b2FixtureDef()
        fd.shape = shape
        fd.density = density
        fd.friction = friction
        fd.restitution = restitution
        fd.isSensor = is_sensor
        return fd
