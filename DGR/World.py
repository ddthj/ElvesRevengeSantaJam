from typing import List

from DGR.Entity import Entity
from DGR.LinAlg import Vector
from DGR.Physics import aabb_collision, sat, Collision


class QuadTree:
    def __init__(self, depth, rect):
        self.max_depth = 4
        self.max_entities = 10
        self.depth = depth
        self.rect = rect
        self.aabb = (rect[0], rect[0] + rect[2], rect[1], rect[1] + rect[3])
        self.entities: List[Entity] = []
        self.nodes = []

    def clear(self):
        self.entities = []
        self.nodes = []

    def split(self):
        width = self.rect[2] / 2
        height = self.rect[3] / 2
        self.nodes.append(QuadTree(self.depth + 1, (self.rect[0], self.rect[1], width, height)))
        self.nodes.append(QuadTree(self.depth + 1, (self.rect[0] + width, self.rect[1], width, height)))
        self.nodes.append(QuadTree(self.depth + 1, (self.rect[0], self.rect[1] + height, width, height)))
        self.nodes.append(QuadTree(self.depth + 1, (self.rect[0] + width, self.rect[1] + height, width, height)))
        for entity in self.entities:
            self.insert(entity)
        self.entities = []

    def insert(self, entity):
        child = True
        for node in self.nodes:
            child = False
            node.insert(entity)
        if child and aabb_collision(self.aabb, entity.aabb):
            self.entities.append(entity)
            if len(self.entities) > self.max_entities and self.depth < self.max_depth:
                self.split()

    def get_child_nodes(self):
        child = True
        temp = []
        for node in self.nodes:
            child = False
            temp += node.get_child_nodes()
        if child:
            return [self.entities]
        return temp


class World:
    def __init__(self, rect, background_color, entities):
        self.gravity = Vector(0, -10.0)
        self.tick_time = 0.0333333333333334
        self.tree = QuadTree(0, rect)
        self.entities: List[Entity] = entities
        self.groups = {}
        self.background_color = background_color
        self.tick_number = 0

    def tick(self):
        self.tick_number += 1
        self.tree.clear()
        temp = []
        for entity in self.entities:
            if entity.alive:
                temp.append(entity)
                entity.tick(self)
                if entity.layer > 0:
                    self.tree.insert(entity)
        self.entities = temp

        potential_collisions = []
        cull_tracker = {x: [] for x in self.entities}
        for node in self.tree.get_child_nodes():
            for a in node:
                for b in node:
                    if type(a) != type(b) and a.layer & b.layer and b not in cull_tracker[a]:
                        if aabb_collision(a.aabb, b.aabb):
                            potential_collisions.append(Collision(a, b, None, None))
                            cull_tracker[a].append(b)
                            cull_tracker[b].append(a)
        for collision in potential_collisions:
            if sat(collision) and collision.a.mass + collision.b.mass > 0:
                collision.resolve()
