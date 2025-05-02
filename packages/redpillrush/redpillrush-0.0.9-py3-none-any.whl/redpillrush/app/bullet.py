from raylib import rl
from raylib.colors import GREEN

class Bullet:
    def __init__(self, pos, direction):
        self.pos = pos[:]
        self.dir = direction[:]
        self.life = 2.0
        self.speed = 0.5
        self.size = 0.2
        self.color = GREEN
    
    def update(self):
        self.pos[0] += self.dir[0] * self.speed
        self.pos[1] += self.dir[1] * self.speed
        self.pos[2] += self.dir[2] * self.speed
        self.life -= rl.GetFrameTime()
        return self.life > 0
    
    def draw(self):
        rl.DrawSphere(self.pos, self.size, self.color)
