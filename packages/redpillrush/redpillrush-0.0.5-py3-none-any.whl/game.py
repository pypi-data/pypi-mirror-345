# ~/Apps/red-pill-push/game.py
from raylib import rl, ffi
from raylib.colors import BLACK, GREEN, RED
from scene import Scene
from player import Player
from bullet import Bullet
from enemy import Enemy
import math

class GameOrchestrator:
    def __init__(self):
        self.title = "Matrix Maze Shooter"
        
        # Initialize window in fullscreen mode
        rl.SetConfigFlags(rl.FLAG_FULLSCREEN_MODE)
        rl.InitWindow(0, 0, self.title.encode('utf-8'))  # 0,0 uses desktop resolution
        rl.SetTargetFPS(60)
        
        # Get actual screen dimensions after fullscreen initialization
        self.window_width = rl.GetScreenWidth()
        self.window_height = rl.GetScreenHeight()
        
        self.camera = ffi.new("struct Camera3D *")
        self.camera.position.x = 0.0
        self.camera.position.y = 2.0
        self.camera.position.z = 4.0
        self.camera.target.x = 0.0
        self.camera.target.y = 0.5
        self.camera.up.x = 0.0
        self.camera.up.y = 1.0
        self.camera.up.z = 0.0
        self.camera.fovy = 45.0
        self.camera.projection = rl.CAMERA_PERSPECTIVE
        
        self.scene = Scene()
        self.player = Player()
        # Start player at a known open position near center
        self.player.pos = [0.0, 0.0, 0.0]  # Center of maze
        # Ensure no collision at spawn, adjust if needed
        while self.scene.check_collision(self.player.pos):
            self.player.pos[0] += 5.0  # Move right until clear
            if abs(self.player.pos[0]) > self.scene.grid_size:
                self.player.pos[0] = 0.0
                self.player.pos[2] += 5.0  # Move forward if still trapped
        self.bullets = []
        self.enemies = []
        self.shoot_cooldown = 0.0
        self.base_shoot_delay = 0.5
        self.shoot_delay = self.base_shoot_delay
        self.enemy_spawn_timer = 0.0
        self.ENEMY_SPAWN_RATE = 1.0
        self.score = 0
        self.game_time = 0.0
        self.difficulty_timer = 0.0
        self.difficulty_tier = 1
        self.difficulty_interval = 30.0
        self.base_enemy_spawn_count = 5
        self.game_over = False
        self.time_limit = 180.0
        self.pills_collected = 0
        self.last_kill_time = 0.0
        self.kill_penalty_interval = 10.0
        
        for _ in range(self.base_enemy_spawn_count):
            self.spawn_enemy()

    def spawn_enemy(self):
        while True:
            x = rl.GetRandomValue(-99, 99)
            z = rl.GetRandomValue(-99, 99)
            enemy = Enemy(x, z, self.difficulty_tier)
            if not self.scene.check_collision(enemy.pos, enemy.size):
                self.enemies.append(enemy)
                break

    def handle_input(self):
        if self.game_over:
            return
        
        rot_rad = math.radians(self.player.rotation)
        forward = [math.sin(rot_rad) * self.player.move_speed, 0.0, math.cos(rot_rad) * self.player.move_speed]
        
        if rl.IsKeyDown(rl.KEY_UP):
            self.move_player(forward)
        if rl.IsKeyDown(rl.KEY_DOWN):
            self.move_player([-f for f in forward])
        if rl.IsKeyDown(rl.KEY_LEFT):
            self.player.rotation += self.player.rotate_speed
        if rl.IsKeyDown(rl.KEY_RIGHT):
            self.player.rotation -= self.player.rotate_speed
        
        # Collect pill with 'E' key
        if rl.IsKeyPressed(rl.KEY_E) and self.scene.check_near_pill(self.player.pos):
            self.pills_collected += 1
            if self.pills_collected == 3:
                self.game_over = True
        
        self.camera.position.x = self.player.pos[0] - math.sin(rot_rad) * 4.0
        self.camera.position.z = self.player.pos[2] - math.cos(rot_rad) * 4.0
        self.camera.position.y = self.player.pos[1] + 2.0
        self.camera.target.x = self.player.pos[0]
        self.camera.target.y = self.player.pos[1] + 0.5
        self.camera.target.z = self.player.pos[2]
        
        self.shoot_cooldown -= rl.GetFrameTime()
        if rl.IsKeyDown(rl.KEY_SPACE) and self.shoot_cooldown <= 0:
            for src in self.player.source_positions:
                src_rot_x = src[0] * math.cos(rot_rad) - src[2] * math.sin(rot_rad)
                src_rot_z = src[0] * math.sin(rot_rad) + src[2] * math.cos(rot_rad)
                gun_pos = [
                    self.player.pos[0] + src_rot_x,
                    self.player.pos[1] + src[1],
                    self.player.pos[2] + src_rot_z
                ]
                src_angle = math.atan2(src[2], src[0]) + rot_rad
                direction = [math.sin(src_angle), 0.0, math.cos(src_angle)]
                self.bullets.append(Bullet(gun_pos, direction))
            self.shoot_cooldown = self.shoot_delay
    
    def move_player(self, direction):
        new_pos = [
            self.player.pos[0] + direction[0],
            self.player.pos[1],
            self.player.pos[2] + direction[2]
        ]
        player_size = [self.player.radius * 2, self.player.thickness, self.player.radius * 2]
        if not self.scene.check_collision(new_pos, player_size):
            self.player.pos = new_pos
    
    def downgrade_weapon(self):
        if self.player.shoot_sources > 1:
            self.player.shoot_sources -= 1
            self.player.update_shoot_sources()
            self.shoot_delay = min(self.base_shoot_delay, self.shoot_delay / 0.9)
        elif self.shoot_delay < self.base_shoot_delay:
            self.shoot_delay = min(self.base_shoot_delay, self.shoot_delay / 0.9)

    def update(self):
        if self.game_over:
            return
        
        self.game_time += rl.GetFrameTime()
        
        if self.game_time >= self.time_limit:
            self.game_over = True
        
        if self.game_time - self.last_kill_time >= self.kill_penalty_interval:
            self.downgrade_weapon()
            self.last_kill_time += self.kill_penalty_interval
        
        self.difficulty_timer += rl.GetFrameTime()
        if self.difficulty_timer >= self.difficulty_interval:
            self.difficulty_tier += 1
            self.difficulty_timer = 0.0
        
        spawn_factor = math.pow(1.1, self.game_time / 10)
        enemies_to_spawn = int(self.base_enemy_spawn_count * spawn_factor) - len(self.enemies)
        if enemies_to_spawn > 0:
            for _ in range(min(enemies_to_spawn, 5)):
                self.spawn_enemy()
        
        self.scene.update()
        self.player.update()
        self.bullets = [b for b in self.bullets if b.update()]
        
        for enemy in self.enemies[:]:
            damage = enemy.update(self.player.pos)
            if damage > 0:
                if not self.player.take_damage(damage):
                    self.game_over = True
                    break
        
        self.enemy_spawn_timer -= rl.GetFrameTime()
        if self.enemy_spawn_timer <= 0:
            self.spawn_enemy()
            self.enemy_spawn_timer = self.ENEMY_SPAWN_RATE
        
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                dx = bullet.pos[0] - enemy.pos[0]
                dy = bullet.pos[1] - (enemy.pos[1] + 0.9)
                dz = bullet.pos[2] - enemy.pos[2]
                dist = (dx*dx + dy*dy + dz*dz)**0.5
                if dist < 1.0:
                    if not enemy.hit(50):
                        self.enemies.remove(enemy)
                        self.score += 100
                        self.last_kill_time = self.game_time
                        if self.player.shoot_sources < 8:
                            self.shoot_delay = max(0.1, self.shoot_delay * 0.9)
                            self.player.add_shoot_source()
                        else:
                            self.shoot_delay = max(0.05, self.shoot_delay * 0.9)
                    self.bullets.remove(bullet)
                    break
    
    def draw(self):
        rl.BeginDrawing()
        rl.ClearBackground(BLACK)
        
        rl.BeginMode3D(self.camera[0])
        self.scene.draw()
        self.player.draw()
        for bullet in self.bullets:
            bullet.draw()
        for enemy in self.enemies:
            enemy.draw()
        rl.EndMode3D()
        
        rl.DrawFPS(10, 10)
        rl.DrawText(f"Score: {self.score}".encode('utf-8'), 10, 30, 20, GREEN)
        rl.DrawText(f"Shoot Sources: {self.player.shoot_sources}".encode('utf-8'), 10, 50, 20, GREEN)
        rl.DrawText(f"Difficulty Tier: {self.difficulty_tier}".encode('utf-8'), 10, 70, 20, GREEN)
        rl.DrawText(f"Time Left: {int(self.time_limit - self.game_time)}s".encode('utf-8'), 10, 90, 20, GREEN)
        rl.DrawText(f"Enemies: {len(self.enemies)}".encode('utf-8'), 10, 110, 20, GREEN)
        rl.DrawText(f"Health: {self.player.health}/{self.player.max_health}".encode('utf-8'), 10, 130, 20, GREEN if self.player.health > 20 else RED)
        rl.DrawText(f"Pills: {self.pills_collected}/3".encode('utf-8'), 10, 150, 20, GREEN)
        rl.DrawText("Press E to collect red pills".encode('utf-8'), 10, self.window_height - 20, 20, GREEN)
        
        if self.game_over:
            if self.pills_collected == 3:
                rl.DrawText("You Win!".encode('utf-8'), self.window_width//2 - 50, self.window_height//2, 30, GREEN)
            else:
                rl.DrawText("Game Over".encode('utf-8'), self.window_width//2 - 50, self.window_height//2, 30, RED)
        
        rl.EndDrawing()
    
    def run(self):
        while not rl.WindowShouldClose():
            self.handle_input()
            self.update()
            self.draw()
        rl.CloseWindow()
