from LinAlg import Vector, Matrix3, det
from Shapes import circle


def find_mass_inertia(entity):
    area = 0
    mass = 0
    inertia = 0
    triangles = [(Vector(0, 0), entity.shape[i - 1], entity.shape[i]) for i in range(len(entity.shape))]
    for tri in triangles:
        tri_area = 0.5 * abs(det(tri[1] - tri[0], tri[2] - tri[0]))
        tri_area_moment = (1/12) * (tri[0].x**2 + tri[0].y**2 + tri[1].x**2 + tri[1].y**2 + (tri[1].x * tri[2].x) + tri[2].x**2 + tri[0].x * (tri[1].x + tri[2].x) + (tri[1].y * tri[2].y) + tri[2].y**2 + tri[0].y * (tri[1].y + tri[2].y)) * abs((tri[0].y * tri[1].x) - (tri[0].x * tri[1].y) - (tri[0].y * tri[2].x) + (tri[1].y * tri[2].x) + (tri[0].x * tri[2].y) - (tri[1].x * tri[2].y))
        area += tri_area
        mass += tri_area * entity.density
        inertia += tri_area_moment * entity.density
    return mass, inertia


# Entities are for anything that exist within the World.
class Entity:
    def __init__(self, **kwargs):
        self.alive = True
        self.name = kwargs.get("name", "")

        self.density = kwargs.get("density", 0.5)
        self.friction = kwargs.get("friction", 0.0)
        self.restitution = kwargs.get("restitution", 0.0)

        self.texture = kwargs.get("texture", None)
        self.texture_loc = kwargs.get("texture_loc", Vector(0, 0))
        self.texture_rot = kwargs.get("texture_rot", 0)

        self.shape = kwargs.get("shape", circle(10))
        self.color = kwargs.get("color", (255, 255, 255))

        self.loc = kwargs.get("loc", Vector(0, 0))
        self.vel = kwargs.get("vel", Vector(0, 0))
        self.rot = kwargs.get("rot", 0)
        self.rot_vel = kwargs.get("rot_vel", 0)

        self.layer = kwargs.get("layer", 1)

        self.vertices = []
        self.aabb = []
        self.update_hitbox()
        self.radius = None if len(self.vertices) > 1 else self.vertices[0].z
        self.mass, self.inertia = find_mass_inertia(self)
        self.mass_inv = 0 if self.mass == 0.0 else 1 / self.mass
        self.inertia_inv = 0 if self.inertia == 0.0 else 1 / self.inertia
        self.affected_by_gravity = kwargs.get("affected_by_gravity", True if self.density > 0 else False)
        self.affected_by_torque = kwargs.get("affected_by_torque", True if self.density > 0 else False)
        self.affected_by_forces = True

        self.force = Vector(0, 0)
        self.collisions = []
        self.torque = 0

    def update_hitbox(self):
        delta = Matrix3(self.rot)
        self.vertices = [self.loc + delta.dot(point) for point in self.shape]
        if len(self.vertices) > 1:
            x = sorted([vertex.dot((1, 0, 0)) for vertex in self.vertices])
            y = sorted([vertex.dot((0, 1, 0)) for vertex in self.vertices])
            self.aabb = [x[0], x[-1], y[0], y[-1]]
        else:
            radius = self.vertices[0].z
            self.aabb = [self.loc.x - radius, self.loc.x + radius, self.loc.y - radius, self.loc.y + radius]

    def update_physics(self, world):
        if self.density > 0.0:
            self.vel += world.gravity + (self.force * self.mass_inv)
            if self.affected_by_torque:
                self.rot_vel += self.torque * self.inertia_inv
        self.loc += self.vel * world.tick_time
        self.rot += self.rot_vel * world.tick_time
        self.update_hitbox()

        self.collisions = []
        self.force = Vector(0.0, 0.0)
        self.torque = 0.0

    def tick(self, world):
        self.update_physics(world)

    def on_collide(self, collision):
        self.collisions.append(collision)
