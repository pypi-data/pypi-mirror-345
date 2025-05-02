# ~/Apps/game/scene.py
from raylib import rl
from raylib.colors import GREEN, BLACK, GRAY, BLUE, RED
import random
import math

class Scene:
    def __init__(self):
        self.grid_size = 100
        self.grid_height = 15
        self.digital_rain = []
        self.walls = []
        self.red_pills = []
        self.init_digital_rain()
        self.generate_improved_maze()  # Replaced generate_complex_maze
        self.spawn_red_pills()
    
    def init_digital_rain(self):
        for _ in range(400):
            x = rl.GetRandomValue(-self.grid_size, self.grid_size)
            z = rl.GetRandomValue(-self.grid_size, self.grid_size)
            self.digital_rain.append({
                'pos': [float(x), float(rl.GetRandomValue(0, self.grid_height)), float(z)],
                'speed': rl.GetRandomValue(1, 5) / 10.0
            })
    
    def spawn_red_pills(self):
        for _ in range(3):
            while True:
                x = rl.GetRandomValue(-self.grid_size + 5, self.grid_size - 5)  # Avoid edges
                z = rl.GetRandomValue(-self.grid_size + 5, self.grid_size - 5)
                pos = [float(x), 0.5, float(z)]
                if not self.check_collision(pos, [0.3, 0.3, 0.3]):
                    self.red_pills.append(pos)
                    break
    
    def generate_improved_maze(self):
        # Outer boundaries
        self.walls = [
            {'pos': [0, 0.5, self.grid_size], 'size': [self.grid_size*2, 1, 1]},
            {'pos': [0, 0.5, -self.grid_size], 'size': [self.grid_size*2, 1, 1]},
            {'pos': [self.grid_size, 0.5, 0], 'size': [1, 1, self.grid_size*2]},
            {'pos': [-self.grid_size, 0.5, 0], 'size': [1, 1, self.grid_size*2]}
        ]
        
        def divide(x, z, width, depth, height):
            if width < 20 or depth < 20:  # Increased minimum size for larger rooms
                return
            
            horizontal = random.choice([True, False])
            wall_height = random.uniform(0.5, 2.0)  # Reduced max height for visibility
            
            if horizontal:
                wall_z = z + random.randint(10, depth-10)  # Wider spacing
                self.walls.append({
                    'pos': [x, wall_height/2, wall_z],
                    'size': [width, wall_height, 1]
                })
                # Multiple passages for better connectivity
                num_passages = random.randint(2, 3)  # 2-3 passages
                passage_width = 5  # Wider passages
                step = width // (num_passages + 1)
                for i in range(num_passages):
                    passage_x = x - width/2 + step * (i + 1)
                    self.walls.append({
                        'pos': [passage_x, wall_height/2, wall_z],
                        'size': [passage_width, wall_height, 1]
                    })
                
                divide(x, z, width, wall_z-z, height)
                divide(x, wall_z+1, width, depth-(wall_z-z+1), height)
            else:
                wall_x = x + random.randint(10, width-10)
                self.walls.append({
                    'pos': [wall_x, wall_height/2, z],
                    'size': [1, wall_height, depth]
                })
                num_passages = random.randint(2, 3)
                passage_width = 5
                step = depth // (num_passages + 1)
                for i in range(num_passages):
                    passage_z = z - depth/2 + step * (i + 1)
                    self.walls.append({
                        'pos': [wall_x, wall_height/2, passage_z],
                        'size': [1, wall_height, passage_width]
                    })
                
                divide(x, z, wall_x-x, depth, height)
                divide(wall_x+1, z, width-(wall_x-x+1), depth, height)
        
        # Start with a larger open area
        divide(-self.grid_size+1, -self.grid_size+1, 
               self.grid_size*2-2, self.grid_size*2-2, 1)
        
        # Add fewer random obstacles to keep it open
        for _ in range(30):  # Reduced from 50
            x = rl.GetRandomValue(-self.grid_size+5, self.grid_size-5)
            z = rl.GetRandomValue(-self.grid_size+5, self.grid_size-5)
            self.walls.append({
                'pos': [x, 0.5, z],
                'size': [random.uniform(1, 3), random.uniform(0.5, 2), random.uniform(1, 3)]
            })
    
    def update(self):
        for drop in self.digital_rain:
            drop['pos'][1] -= drop['speed']
            if drop['pos'][1] < -0.5:
                drop['pos'][1] = self.grid_height
                drop['pos'][0] = rl.GetRandomValue(-self.grid_size, self.grid_size)
                drop['pos'][2] = rl.GetRandomValue(-self.grid_size, self.grid_size)
    
    def draw(self):
        rl.DrawGrid(self.grid_size * 2, 1.0)
        for drop in self.digital_rain:
            rl.DrawCubeV(drop['pos'], [0.1, 0.3, 0.1], GREEN)
        for wall in self.walls:
            rl.DrawCubeV(wall['pos'], wall['size'], GRAY)
        for pill in self.red_pills:
            rl.DrawSphere(pill, 0.3, RED)
    
    def check_collision(self, pos, size=[0.3, 0.1, 0.3]):
        for wall in self.walls:
            wall_half = [s/2 for s in wall['size']]
            obj_half = [s/2 for s in size]
            
            if (abs(pos[0] - wall['pos'][0]) < (obj_half[0] + wall_half[0]) and
                abs(pos[1] - wall['pos'][1]) < (obj_half[1] + wall_half[1]) and
                abs(pos[2] - wall['pos'][2]) < (obj_half[2] + wall_half[2])):
                return True
        return False
    
    def check_near_pill(self, pos):
        for pill in self.red_pills[:]:
            dx = pos[0] - pill[0]
            dy = pos[1] - pill[1]
            dz = pos[2] - pill[2]
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            if dist < 1.0:
                self.red_pills.remove(pill)
                return True
        return False
