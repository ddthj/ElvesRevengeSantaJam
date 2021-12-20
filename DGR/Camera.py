from pygame import transform, draw
from math import pi
from Entities import Building
from DGR.LinAlg import Vector
from DGR.Entity import Entity


DEGREES = 180 / pi


def cap(x, low, high):
    if x < low:
        return low
    elif x > high:
        return high
    return x


class Camera:
    def __init__(self, font, debug=False):
        self.location = Vector(0, 0, 0)
        self.target = None
        self.zoom = 1
        self.debug = debug
        self.font = font

    def tick(self):
        if self.target is not None:
            self.location += (self.target.loc + (self.target.vel * Vector(0.5, 0.5, 0)) - self.location) / 8

    def render(self, window, entity: Entity):
        offset = Vector(*window.get_size(), 0) * Vector(0.5, -0.5, 0)
        if entity.texture is not None:
            rotation = entity.rot + entity.texture_rot
            transformed = transform.rotozoom(entity.texture, rotation * DEGREES, self.zoom)
            half = Vector(*transformed.get_size(), 0) / 2
            loc = (entity.loc + entity.texture_loc - self.location) * self.zoom - half + offset
            window.blit(transformed, loc.render())
        elif self.debug:
            for i in range(len(entity.vertices)):
                start = (entity.vertices[i - 1] - self.location) * self.zoom + offset
                end = (entity.vertices[i] - self.location) * self.zoom + offset
                draw.line(window, entity.color, start.render(), end.render(), 2)
            if hasattr(entity, "fire_particles"):
                for p in entity.fire_particles:
                    loc = (p - self.location) * self.zoom + offset
                    draw.circle(window, (255, 0, 0), loc.render(), 3)
        if type(entity) == Building and not entity.dead:
            surface = self.font.render(str(int(entity.health)), True, (255, 255, 255))
            loc = (entity.loc - self.location) * self.zoom + offset
            window.blit(surface, loc.render())

    def render_aabb(self, window, a, color=None):
        offset = Vector(*window.get_size(), 0) * Vector(0.5, -0.5, 0)
        vertices = [Vector(a[0], a[2], 0),
                    Vector(a[1], a[2], 0),
                    Vector(a[1], a[3], 0),
                    Vector(a[0], a[3], 0)]
        for i in range(4):
            start = (vertices[i - 1] - self.location) * self.zoom + offset
            end = (vertices[i] - self.location) * self.zoom + offset
            draw.line(window, [0, 55, 100] if color is None else color, start.render(), end.render(), 2)

    def render_center_rect(self, window, loc, size, color=None):
        half_size = Vector(size / 2, -size / 2)
        offset = Vector(*window.get_size(), 0) * Vector(0.5, -0.5, 0)
        corner = ((loc - self.location - half_size) * self.zoom + offset).render()
        draw.rect(window, [0, 55, 100] if color is None else color, (corner[0], corner[1], size * self.zoom, size * self.zoom), 2)

    def render_quadtree(self, window, tree, color):
        self.render_aabb(window, tree.aabb, color)
        for node in tree.nodes:
            self.render_quadtree(window, node, color)

    def render_circle(self, window, loc, radius):
        offset = Vector(*window.get_size(), 0) * Vector(0.5, -0.5, 0)
        loc = loc * self.zoom + offset
        draw.circle(window, (255, 255, 255), loc.render(), radius)

    def render_line(self, window, start, end, color=None):
        offset = Vector(*window.get_size(), 0) * Vector(0.5, -0.5, 0)
        start = start * self.zoom + offset
        end = end * self.zoom + offset
        draw.line(window, (255, 255, 255) if color is None else color, start.render(), end.render(), 2)

    def mouse_to_world(self, window, mouse):
        offset = Vector(*window.get_size(), 0) * Vector(0.5, -0.5, 0)
        return mouse * Vector(1, -1) - offset
