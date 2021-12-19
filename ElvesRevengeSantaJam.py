from enum import Enum
from random import randint

import pygame

from AStar import a_star
from Shapes import center_rectangle, corner_rectangle
from World import World, Vector
from Camera import Camera
from Entities import Character, Entity, EntityState, SnowBall, SnowMan, Elf, Building, Item
from Test_World import make_world, building_map


def cap(x, max):
    if x < max:
        return x
    return max


class GameState(Enum):
    WAVE_START = 1
    FORTIFICATION = 2
    ATTACK = 3
    LOSE = 4


class ElvesRevengeSantaJam:
    def __init__(self):

        pygame.init()
        pygame.font.init()

        self.resolution = [800, 600]
        self.window = pygame.display.set_mode(self.resolution)

        pygame.display.set_caption("ElvesRevengeSantaJam")

        self.left = self.right = self.up = self.down = self.snow = self.shovel = self.build = False
        self.mouse = Vector(0, 0)

        self.player = Character(shape=center_rectangle(10, 10), color=(255, 0, 0))  # todo - pass texture
        self.test_elf = Elf(shape=center_rectangle(10, 10), color=(0, 255, 0), loc=Vector(-500, -500), item=Item.TORCH, star=self.a_star)
        self.player.item = Item.TORCH
        self.tile_size = 50
        self.map_size = 18
        self.snow_map = make_world(self.map_size, self.map_size)
        self.width = len(self.snow_map) * self.tile_size // 2
        self.height = len(self.snow_map[0]) * self.tile_size // 2
        self.world = World((-self.width, -self.height, self.width * 2, self.height * 2), (0, 0, 0), [self.player, self.test_elf])
        self.world.gravity = Vector(0, 0)
        self.camera = Camera(True)
        self.camera.target = self.player
        self.camera.zoom = 2
        self.running = True
        self.snowman_op_level = 1
        self.snowfall_remaining = 0
        self.elves_remaining = 0
        self.wave = 0
        self.fortify_period = 1.0
        self.attack_period = 10.0
        self.timer = 0.0
        self.state = GameState.WAVE_START
        self.occupied_tiles = []
        self.test_path = []

    def load_map(self, buildings):
        for building in buildings:

            texture = None
            if building[0] == "santa_house" or building[0] == "store":
                size = (2, 1)
            elif building[0] == "elf_house":
                size = (1, 1)
            elif building[0] == "workshop":
                size = (2, 5)
            elif building[0] == "barn":
                size = (2, 2)
            elif building[0] == "warehouse":
                size = (5, 2)
            else:
                size = (10, 10)

            shape = corner_rectangle(size[0] * self.tile_size, size[1] * self.tile_size)
            cords = self.tile_corner(building[1], building[2])

            for x in range(size[0]):
                for y in range(size[1]):
                    tile = Vector(building[1], building[2]) + Vector(x, y)
                    self.occupied_tiles.append(tile)

            building = Building(shape=shape, texture=texture, color=(165, 42, 42), loc=Vector(*cords), density=0)
            self.world.entities.append(building)

    def a_star(self, start, finish):
        start_cords = Vector(*self.current_cords_v(start))
        target_cords = Vector(*self.current_cords_v(finish))
        print(start, start_cords, finish, target_cords)
        result = a_star(start_cords, target_cords, self.occupied_tiles)
        return [self.tile_center(*z) for z in result]

    def make_wave(self):
        self.snowfall_remaining = self.map_size * self.map_size * 2 - self.wave
        self.elves_remaining = 5 + self.wave
        self.wave += 1

    def place_snow(self):
        x = randint(0, self.map_size - 1)
        y = randint(0, self.map_size - 1)
        self.snow_map[x][y] = cap(1 + self.snow_map[x][y], 20)
        self.snowfall_remaining -= 1

    def place_elf(self):
        if randint(0, 1):
            x = 0 if randint(0, 1) else self.map_size - 1
            y = randint(0, self.map_size - 1)
        else:
            x = randint(0, self.map_size - 1)
            y = 0 if randint(0, 1) else self.map_size - 1

        loc = Vector(*self.tile_center(x, y))
        item = Item.TORCH # Item.NONE if randint(0, 1) else Item.TORCH
        elf = Elf(shape=center_rectangle(10, 10), color=(0, 255, 0), loc=loc, item=item, star=self.a_star)
        self.world.entities.append(elf)
        self.elves_remaining -= 1

    def current_cords(self, entity):
        return self.current_cords_v(entity.loc)

    def current_cords_v(self, v):
        bottom_left = Vector(-self.map_size * self.tile_size // 2, -self.map_size * self.tile_size // 2)
        from_bottom_left = v - bottom_left
        return (from_bottom_left // self.tile_size * Vector(1, -1)).render()

    def tile_center(self, x, y):
        return Vector(x, y) * self.tile_size - Vector(self.width, self.height) + Vector(self.tile_size // 2, self.tile_size // 2)

    def tile_corner(self, x, y):
        return Vector(x, y) * self.tile_size - Vector(self.width, self.height)

    def throw_snow(self, entity, direction):
        if entity.throw_cooldown <= 0.0:
            # if an entity is carrying snow, they are a snowman
            if entity.snow_carried > 0:
                entity.snow_carried -= 1
                entity.state = EntityState.THROWING
                entity.throw_cooldown = entity.throw_speed
                self.world.entities.append(SnowBall(entity, vel=direction * 75, loc=entity.loc + direction * 10))
            else:
                cords = self.current_cords(entity)
                if self.snow_map[cords[0]][cords[1]] > 0:
                    self.snow_map[cords[0]][cords[1]] -= 1
                    entity.state = EntityState.THROWING
                    entity.throw_cooldown = entity.throw_speed
                    total_vel = entity.vel.magnitude() + 75
                    self.world.entities.append(SnowBall(entity, vel=direction * total_vel, loc=entity.loc + direction * 10))

    def shovel_snow(self):
        cords = self.current_cords(self.player)
        if self.player.snow_carried == 0:
            if self.snow_map[cords[0]][cords[1]] > 0:
                self.player.snow_carried = self.snow_map[cords[0]][cords[1]]
                self.snow_map[cords[0]][cords[1]] = 0
                self.player.walk_speed *= 0.75
                self.player.state = EntityState.SHOVELING
        else:
            self.snow_map[cords[0]][cords[1]] += self.player.snow_carried
            self.player.snow_carried = 0
            self.player.state = EntityState.IDLE
            self.player.walk_speed *= 1.33

    def build_snowman(self, entity):
        cords = self.current_cords(entity)
        if self.snow_map[cords[0]][cords[1]] > 0:
            size = 10 + self.snow_map[cords[0]][cords[1]]
            snowman = SnowMan(shape=center_rectangle(size, size), loc=Vector(*self.tile_center(*cords)), throw=self.throw_snow)
            snowman.snow_carried = self.snow_map[cords[0]][cords[1]] * self.snowman_op_level
            snowman.affected_by_forces = False
            snowman.color = (255, 255, 255)
            self.world.entities.append(snowman)
            self.snow_map[cords[0]][cords[1]] = 0
            entity.state = EntityState.BUILDING

    def render(self):
        self.window.fill((0, 0, 0))
        ts = self.tile_size
        w = self.width
        h = self.height
        for x in range(len(self.snow_map)):
            for y in range(len(self.snow_map[0])):
                if self.snow_map[x][y] is not Entity:
                    self.camera.render_aabb(self.window, (x * ts - w, x * ts + ts - w, y * ts - h, y * ts + ts - h))
        for entity in self.world.entities:
            self.camera.render(self.window, entity)
        self.camera.render_quadtree(self.window, self.world.tree, (0, 100, 255))
        pygame.display.update()

    def get_inputs(self):
        events = pygame.event.get()
        self.snow = self.shovel = self.build = False
        h = Vector(*self.window.get_size(), 0) * 0.5
        self.mouse = ((Vector(*pygame.mouse.get_pos()) - h) * Vector(1, -1) / self.camera.zoom) + self.camera.location
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.up = True
                elif event.key == pygame.K_a:
                    self.left = True
                elif event.key == pygame.K_s:
                    self.down = True
                elif event.key == pygame.K_d:
                    self.right = True
                elif event.key == pygame.K_e:
                    self.build = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.up = False
                elif event.key == pygame.K_a:
                    self.left = False
                elif event.key == pygame.K_s:
                    self.down = False
                elif event.key == pygame.K_d:
                    self.right = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    self.snow = True
                elif event.button == pygame.BUTTON_RIGHT:
                    self.shovel = True
                elif event.button == pygame.BUTTON_WHEELUP:
                    self.camera.zoom += 0.5
                elif event.button == pygame.BUTTON_WHEELDOWN and self.camera.zoom > 0.5:
                    self.camera.zoom -= 0.5

    def player_movement(self):
        self.player.vel = Vector(self.right - self.left, self.up - self.down).normalize() * self.player.walk_speed

    def game_logic(self):
        self.timer -= self.world.tick_time
        if self.snow and self.player.snow_carried == 0:
            self.throw_snow(self.player, (self.mouse - self.player.loc).normalize())
        elif self.shovel:
            self.shovel_snow()
        elif self.build:
            self.build_snowman(self.player)

        if self.state == GameState.WAVE_START:
            self.make_wave()
            self.timer = self.fortify_period
            self.state = GameState.FORTIFICATION
            print("Fortification Period Started!")
        elif self.state == GameState.FORTIFICATION:
            if self.timer <= 0.0:
                self.state = GameState.ATTACK
                self.timer = self.attack_period
                print("Wave Started!")
            else:
                snow_per_second = self.snowfall_remaining / (self.timer / 2)
                for i in range(int(snow_per_second)):
                    self.place_snow()
        elif self.state == GameState.ATTACK:
            if self.timer <= 0.0:
                self.state = GameState.WAVE_START
            else:
                elves_per_second = self.elves_remaining / self.timer
                elves_per_second = 0
                if self.world.tick_time % 60 == 0 and 1.0 > elves_per_second > 0.0:
                    elves_per_second = 1
                if len(self.world.entities) < 100:
                    for i in range(int(elves_per_second)):
                        self.place_elf()

    def run(self):
        self.load_map(building_map())
        clock = pygame.time.Clock()
        while self.running:
            if self.test_elf.target_building is not None:
                pass
                # print(self.current_cords(self.test_elf.target_building), self.test_elf.path)
            clock.tick(60)
            self.get_inputs()
            self.player_movement()
            self.world.tick()
            self.game_logic()
            self.camera.tick()
            self.render()


game = ElvesRevengeSantaJam()
game.run()
