from raylib import rl
from raylib.colors import RED, BLACK
import math

class Enemy:
    def __init__(self, x, z, difficulty_tier=1):
        self.pos = [float(x), 0.0, float(z)]
        self.size = [0.6, 1.8, 0.4]
        self.color = RED
        self.speed = 0.05
        self.base_health = 100
        self.health = self.base_health * (1 + 0.5 * (difficulty_tier - 1))
        self.animation_time = 0.0
        self.attack_cooldown = 0.0  # New: Cooldown for attacks
        self.attack_interval = 1.0  # Attack every 1 second when in range
        self.attack_damage = 10  # Damage per attack

    def update(self, player_pos):
        self.animation_time += rl.GetFrameTime()
        self.attack_cooldown -= rl.GetFrameTime()
        
        # Move towards player
        dx = player_pos[0] - self.pos[0]
        dz = player_pos[2] - self.pos[2]
        dist = math.sqrt(dx*dx + dz*dz)
        if dist > 0:
            dx, dz = dx/dist, dz/dist
            self.pos[0] += dx * self.speed
            self.pos[2] += dz * self.speed
        
        # Attack if close enough
        if dist < 1.0 and self.attack_cooldown <= 0:
            self.attack_cooldown = self.attack_interval
            return self.attack_damage  # Return damage to apply to player
        return 0  # No damage if not attacking

    def draw(self):
        sway = math.sin(self.animation_time) * 0.05
        rl.DrawCubeV(
            [self.pos[0], self.pos[1] + 0.9, self.pos[2]],
            self.size,
            self.color
        )
        rl.DrawCubeV(
            [self.pos[0], self.pos[1] + 1.8, self.pos[2]],
            [0.3, 0.3, 0.3],
            BLACK
        )
    
    def hit(self, damage):
        self.health -= damage
        return self.health > 0
