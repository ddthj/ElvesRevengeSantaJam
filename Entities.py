from enum import Enum
from DGR.Entity import Entity
from DGR.Shapes import center_rectangle
from random import randint

from LinAlg import Vector


def cap(x, m):
    if x < m:
        return x
    return m


class EntityState(Enum):
    IDLE = 0
    STUNNED = 1
    WALKING = 2
    THROWING = 3
    SHOVELING = 4
    BUILDING = 5
    KICKING = 6


class Item(Enum):
    NONE = 0
    TORCH = 1
    SHOVEL = 2


class Character(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state = kwargs.get("state", EntityState.IDLE)
        self.item = kwargs.get("item", Item.NONE)
        self.snow_carried = 0
        self.op_level = 2
        self.health = kwargs.get("health", 5.0)
        self.walk_speed = kwargs.get("speed", 50.0)
        self.throw_speed = kwargs.get("throw_speed", 1.5)
        self.throw_cooldown = 0.0
        self.affected_by_torque = False
        self.throw_snow = kwargs.get("throw", None)
        self.target_building = None
        self.target_character = None
        self.torched_buildings = []
        self.path = None
        self.a_star = kwargs.get("star", None)

    def tick(self, world):
        self.update_physics(world)
        self.throw_cooldown -= world.tick_time
        if self.health <= 0:
            self.alive = False


class SnowMan(Character):
    def tick(self, world):
        size = 10 + cap(self.snow_carried, 46)
        self.throw_speed = 1.5 - 0.03 * cap(self.snow_carried, 46)
        self.shape = center_rectangle(size / self.op_level, size / self.op_level)

        if self.snow_carried == 0:
            self.alive = False

        self.update_physics(world)
        self.throw_cooldown -= world.tick_time

        elves = []

        for entity in world.entities:
            if type(entity) == Elf:
                # todo - pick better distance
                elf_distance = (entity.loc - self.loc).magnitude()
                if elf_distance < 150:
                    elves.append([entity, elf_distance])
        if len(elves) > 0:
            elves = sorted(elves, key=lambda x: x[1])
            future_elf = elves[0][0].loc + elves[0][0].vel * 0.75 * (elves[0][1] / 75)
            self.throw_snow(self, (future_elf - self.loc).normalize())
        else:
            buildings = []
            for e in world.entities:
                if type(e) is Building and len(e.fire_particles) > 0 and not e.dead:
                    building_loc = Vector((e.aabb[0] + e.aabb[1]) / 2, (e.aabb[2] + e.aabb[3]) / 2)
                    building_distance = (self.loc - building_loc).magnitude()
                    if building_distance < 200:
                        buildings.append([e, building_distance])
            if len(buildings) > 0:
                e = sorted(buildings, key=lambda x: x[1])[0][0]
                building_loc = Vector((e.aabb[0] + e.aabb[1]) / 2, (e.aabb[2] + e.aabb[3]) / 2)
                self.throw_snow(self, (building_loc - self.loc).normalize())


class Elf(Character):
    def tick(self, world):
        self.update_physics(world)
        if self.health <= 0:
            self.alive = False

        if self.item == Item.TORCH:
            if self.target_building is None:
                buildings = []
                for e in world.entities:
                    if type(e) is Building and not e.dead and e not in self.torched_buildings:
                        building_loc = Vector((e.aabb[0] + e.aabb[1]) / 2, (e.aabb[2] + e.aabb[3]) / 2)
                        buildings.append([e, (self.loc - building_loc).magnitude()])
                if len(buildings) > 0:
                    buildings = sorted(buildings, key=lambda x: x[1])
                    self.target_building = buildings[0][0]
                else:
                    self.torched_buildings = []

            elif self.path is None:
                e = self.target_building
                building_loc = Vector((e.aabb[0] + e.aabb[1]) / 2, (e.aabb[2] + e.aabb[3]) / 2)
                self.path = self.a_star(self.loc, building_loc)

            else:
                if len(self.path) > 0 and self.target_building not in self.torched_buildings:
                    direction, dist = (self.path[-1] - self.loc).normalize(True)
                    if dist < 10:
                        self.path.pop()
                    self.vel = direction * self.walk_speed
                else:
                    self.target_building = None
                    self.path = None

    def on_collide(self, collision):
        other = collision.other(self)
        if collision.contact_point is not None:
            if self.item == Item.TORCH and type(other) == Building and other not in self.torched_buildings:
                other.fire_particles.append(collision.contact_point)
                self.torched_buildings.append(other)


class Building(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.health = 100
        self.snow = 0
        self.fire_particles = []
        self.dead = False

    def tick(self, world):
        self.update_physics(world)
        self.health -= len(self.fire_particles) * world.tick_time
        if self.health <= 0:
            self.color = (10, 10, 10)
            self.dead = True
        if world.tick_number % 10 == 0:
            for i in range(len(self.fire_particles)):
                if len(self.fire_particles) < 50:
                    if randint(0, 30) == 5:
                        x = randint(self.aabb[0], self.aabb[1])
                        y = randint(self.aabb[2], self.aabb[3])
                        self.fire_particles.append(Vector(x, y))
                else:
                    break


class SnowBall(Entity):
    def __init__(self, parent, **kwargs):
        super().__init__(shape=center_rectangle(5, 5), color=(255, 255, 255), **kwargs)
        self.airtime = 3.0
        self.radius = 10
        self.parent = parent
        self.affected_by_forces = False

    def tick(self, world):
        self.update_physics(world)
        self.airtime -= world.tick_time
        if self.airtime <= 0.0:
            self.alive = False

    def on_collide(self, collision):
        self.collisions.append(collision)
        other = collision.other(self)
        if other is not self.parent:

            if type(other) == Building:
                self.alive = False
                if len(other.fire_particles) > 0:
                    other.fire_particles.pop()
            if type(other) == Elf:
                self.alive = False
                other.health -= 1
                other.state = EntityState.STUNNED


class SnowWall(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.health = 100
