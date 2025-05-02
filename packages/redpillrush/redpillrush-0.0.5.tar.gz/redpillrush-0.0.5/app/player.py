# ~/Apps/game/player.py
from raylib import rl
from raylib.colors import RAYWHITE, RED, BLACK, GRAY
import math

class Player:
    def __init__(self):
        self.pos = [0.0, 0.0, 0.0]
        self.rotation = 0.0
        self.move_speed = 0.2
        self.rotate_speed = 3.0
        self.radius = 0.3
        self.thickness = 0.1
        self.body_color = GRAY
        self.accent_color = RED
        self.animation_time = 0.0
        self.shoot_sources = 1
        self.max_sources = 8
        self.source_positions = []
        self.health = 100  # New: Player health
        self.max_health = 100  # Maximum health for reference
        self.update_shoot_sources()

    def update_shoot_sources(self):
        self.source_positions.clear()
        if self.shoot_sources == 1:
            self.source_positions.append([0.2, 0.4, 0.0])
        else:
            angle_step = 360.0 / self.shoot_sources
            for i in range(self.shoot_sources):
                angle = math.radians(angle_step * i)
                x = math.cos(angle) * 0.2
                z = math.sin(angle) * 0.2
                self.source_positions.append([x, 0.4, z])

    def add_shoot_source(self):
        if self.shoot_sources < self.max_sources:
            self.shoot_sources += 1
            self.update_shoot_sources()

    def take_damage(self, damage):
        self.health -= damage
        return self.health > 0  # Return True if still alive

    def update(self):
        self.animation_time += rl.GetFrameTime()

    def draw(self):
        self.update()
        rot_rad = math.radians(self.rotation)
        
        rl.DrawCylinder(
            [self.pos[0], self.pos[1] + self.thickness/2, self.pos[2]],
            self.radius, self.radius, self.thickness,
            32, self.body_color
        )
        rl.DrawCylinder(
            [self.pos[0], self.pos[1] + self.thickness/2, self.pos[2]],
            self.radius, self.radius * 0.8, self.thickness * 0.1,
            32, self.accent_color
        )
        rl.DrawSphere(
            [self.pos[0], self.pos[1] + 0.05, self.pos[2]], 
            self.radius * 0.5,
            (self.accent_color[0], self.accent_color[1], 
             self.accent_color[2], 100)
        )
        rl.DrawSphere(
            [self.pos[0], self.pos[1] + self.thickness/2, self.pos[2]],
            self.radius * 0.2,
            self.body_color
        )
        for src in self.source_positions:
            src_rot_x = src[0] * math.cos(rot_rad) - src[2] * math.sin(rot_rad)
            src_rot_z = src[0] * math.sin(rot_rad) + src[2] * math.cos(rot_rad)
            rl.DrawSphere(
                [self.pos[0] + src_rot_x, self.pos[1] + src[1], self.pos[2] + src_rot_z],
                0.05, RED
            )
