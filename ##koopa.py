import pygame
import sys
import math  # ← as requested for rendering/animation timing
import random
from pygame.locals import *

# Constants - True NES Resolution scaled up
NES_W = 256
NES_H = 240
SCALE = 3
WIDTH = NES_W * SCALE
HEIGHT = NES_H * SCALE
FPS = 60
TILE = 16

# Colors mapping for the sprite generator
C = {
    ' ': (0, 0, 0, 0),          # Transparent
    'R': (216, 40, 0, 255),     # Mario Red
    'S': (252, 152, 56, 255),   # Skin
    'B': (200, 76, 12, 255),    # Brown (Shoes/Hair/Goomba/Brick)
    'O': (0, 120, 248, 255),    # Overalls Blue
    'Y': (248, 184, 0, 255),    # Coin Yellow / Buttons
    'y': (248, 184, 0, 255),    # Highlight
    'G': (0, 168, 0, 255),      # Green (Pipe/Koopa)
    'g': (184, 248, 24, 255),   # Light Green
    'W': (255, 255, 255, 255),  # White
    'K': (0, 0, 0, 255),        # Black
    'c': (252, 152, 56, 255),   # Highlight/Coin block
    'D': (184, 92, 0, 255),     # Dark Brown
    'U': (92, 148, 252, 255),   # Sky Blue
    'L': (0, 0, 0, 100),        # Shadow
}

# Raw Pixel Art Data (16x16 frames) - PRE-BAKED SMA2 / SUPER MARIO WORLD GBA STYLE
# No PNGs loaded. Everything is string data. Hand is now perfectly attached
# on Mario's correct side in BOTH directions (right when facing right, left when flipped).
# Added mario_run2 for smooth running animation.
SPRITE_STRINGS = {
    'mario_idle': [
        "    RRRRR       ", "   RRRRRRRRR    ", "   BBBSSBS      ", "  BSBSSSBS      ",
        "  BSBSSSBS      ", "  BSSSSS        ", "    SSSSSSS     ", "   RRBRRR       ",
        "  RRRBRRBRRR    ", " RRRRBBBBRRRR   ", " OO RBBYBBRO    ", # SMA2-style hand on right side
        " OOOYYYYYOOO    ", " OO OOOOO OO    ", " BBB     BBB    ",
        "BBBB    BBBB    ", "                "
    ],
    'mario_run1': [
        "    RRRRR       ", "   RRRRRRRRR    ", "   BBBSSBS      ", "  BSBSSSBS      ",
        "  BSBSSSBS      ", "  BSSSSS        ", "    SSSSSSS     ", "   RRBRRR       ",
        "  RRRBRRBRRR    ", " RRRRBBBBRRRR   ", "  O RBBYBBRO    ", # Forward swing (SMA2 arm pose)
        "  OOYYYYYOO     ", "  O OOOOO O     ", " BB      BB     ",
        "BBB      BBB    ", "                "
    ],
    'mario_run2': [
        "    RRRRR       ", "   RRRRRRRRR    ", "   BBBSSBS      ", "  BSBSSSBS      ",
        "  BSBSSSBS      ", "  BSSSSS        ", "    SSSSSSS     ", "   RRBRRR       ",
        "  RRRBRRBRRR    ", " RRRRBBBBRRRR   ", "   ORBBYBBRO    ", # Back swing (SMA2 arm pose)
        "  OOYYYYYOO     ", "  O OOOOO O     ", " BB      BB     ",
        "BBB      BBB    ", "                "
    ],
    'mario_jump': [
        "    RRRRR       ", "   RRRRRRRRR    ", "   BBBSSBS      ", "  BSBSSSBS      ",
        "  BSBSSSBS      ", "  BSSSSS        ", "    SSSSSSS     ", "   RRBRRR     BB",
        "  RRRBRRBRRR BBB", " RRRRBBBBRRRRBBB", " OO RBBYBBRO    ", # SMA2 jump hand
        " OOOYYYYYOOO    ", " OO OOOOO OO    ", "  B      BBB    ",
        " BB             ", "                "
    ],
    'goomba_walk1': [
        "                ", "                ", "                ", "       WW       ",
        "      WWWW      ", "     BBBBBB     ", "    BKKBBKKB    ", "   BBKKBKKBKKB  ",
        "   BBBWWWBBB    ", "  BBBBWWBWBBBB  ", "  BBBBBBBBBBBB  ", "  BBBBBBBBBBBB  ",
        "   BBBBBBBBBB   ", " KKBBBBBBBBBBKK ", " KKK        KKK ", "                "
    ],
    'goomba_walk2': [
        "                ", "                ", "                ", "       WW       ",
        "      WWWW      ", "     BBBBBB     ", "    BKKBBKKB    ", "   BBKKBKKBKKB  ",
        "   BBBWWWBBB    ", "  BBBBWWBWBBBB  ", "  BBBBBBBBBBBB  ", "  BBBBBBBBBBBB  ",
        "   BBBBBBBBBB   ", "  KBBBBBBBBBBK  ", "  KK        KK  ", "                "
    ],
    'goomba_dead': [
        "                ", "                ", "                ", "                ",
        "                ", "                ", "                ", "       WW       ",
        "      WWWW      ", "     BBBBBB     ", "    BKKBBKKB    ", "   BBKKBKKBKKB  ",
        "   BBBWWWBBB    ", "  BBBBBBBBBBBB  ", "  KBBBBBBBBBBK  ", "  K          K  "
    ],
    'koopa_walk1': [
        "    GG        WW", "   GGGG      WWK", "  GGGGGG     WW ", " GGGGWWGG    W  ",
        " GGWWWWWWG WW   ", " GWWKKWWWW W    ", " GWWKKWWWW W    ", " GWWWWWWWW W    ",
        " GWWWWWWWW      ", "  WWWWWWWW      ", "    GGGGGG      ", "   GGYYYYGG     ",
        "   GYYYYYYG     ", "   GYYYYYYG     ", "    GG  GG      ", "                "
    ],
    'koopa_shell': [
        "                ", "                ", "                ", "                ",
        "                ", "     GGGGGG     ", "   GGGGGGGGGG   ", "  GGGGGGGGGGGG  ",
        " GGGGGWWWWGGGGG ", " GGWWWWWWWWWWGG ", " GGWWKKWWKKWWGG ", " GGWKKWKKWKKWGG ",
        "  GWWWWWWWWWWG  ", "  WWWWWWWWWWWW  ", "                ", "                "
    ],
    'brick': [
        "BBBBBBBBBBBBBBBB", "BccccccccccccccB", "BcBBBBBBcBBBBBBc", "BcBBBBBBcBBBBBBc",
        "BcBBBBBBcBBBBBBc", "BccccccccccccccB", "BcBBcBBBBBBcBBBB", "BcBBcBBBBBBcBBBB",
        "BcBBcBBBBBBcBBBB", "BccccccccccccccB", "BBBBBBcBBBBBBcBB", "BBBBBBcBBBBBBcBB",
        "BBBBBBcBBBBBBcBB", "BccccccccccccccB", "BcBBBBBBcBBBBBBc", "BcBBBBBBcBBBBBBc"
    ],
    'question': [
        "cccccccccccccccc", "cDDDDDDDDDDDDDDc", "cDYYYYYYYYYYYYDc", "cDYcYYYYYYYYcYDc",
        "cDYcYYYDDYYYcYDc", "cDYYYYDDDDYYYyDc", "cDYYYDYYYYDYYyDc", "cDYYYyYYYDDYYyDc",
        "cDYYYYYYDDYYYyDc", "cDYYYYYDDYYYYyDc", "cDYYYYYyYYYYYyDc", "cDYYYYYDDYYYYyDc",
        "cDYcYYYDDYYYcYDc", "cDYcYYYYYYYYcYDc", "cDyyyyyyyyyyyyDc", "cccccccccccccccc"
    ],
    'ground': [
        "cccccccccccccccc", "cDDDDDDDDDDDDDDc", "cDcDcDcDcDcDcDcc", "cDcDcDcDcDcDcDcc",
        "cDcDcDcDcDcDcDcc", "cDcDcDcDcDcDcDcc", "cDDDDDDDDDDDDDDc", "ccDcDcDcDcDcDcDc",
        "ccDcDcDcDcDcDcDc", "ccDcDcDcDcDcDcDc", "ccDcDcDcDcDcDcDc", "cDDDDDDDDDDDDDDc",
        "cDcDcDcDcDcDcDcc", "cDcDcDcDcDcDcDcc", "cDcDcDcDcDcDcDcc", "cccccccccccccccc"
    ],
    'pipe_tl': [
        "KKKKKKKKKKKKKKKK", "KggggggggggggggK", "KgGGGGGGgGGGGGGK", "KgGGGGGGgGGGGGGK",
        "KgGGGGGGgGGGGGGK", "KgGGGGGGgGGGGGGK", "KgGGGGGGgGGGGGGK", "KgGGGGGGgGGGGGGK",
        "KgGGGGGGgGGGGGGK", "KgGGGGGGgGGGGGGK", "KgGGGGGGgGGGGGGK", "KgGGGGGGgGGGGGGK",
        "KgGGGGGGgGGGGGGK", "KgGGGGGGgGGGGGGK", "KgGGGGGGgGGGGGGK", "KKKKKKKKKKKKKKKK"
    ],
    'pipe_tr': [
        "KKKKKKKKKKKKKKKK", "ggggggggggggggGK", "GGGGGGgGGGGGGGGK", "GGGGGGgGGGGGGGGK",
        "GGGGGGgGGGGGGGGK", "GGGGGGgGGGGGGGGK", "GGGGGGgGGGGGGGGK", "GGGGGGgGGGGGGGGK",
        "GGGGGGgGGGGGGGGK", "GGGGGGgGGGGGGGGK", "GGGGGGgGGGGGGGGK", "GGGGGGgGGGGGGGGK",
        "GGGGGGgGGGGGGGGK", "GGGGGGgGGGGGGGGK", "GGGGGGgGGGGGGGGK", "KKKKKKKKKKKKKKKK"
    ],
    'pipe_bl': [
        "KKKKKKKKKKKKKKKK", "KggggggggggggggK", "KgGGGGGGgGGGGGGK", "KgGGGGGGgGGGGGGK",
        "KgGGGGGGgGGGGGGK", "KgGGGGGGgGGGGGGK", "KgGGGGGGgGGGGGGK", "KgGGGGGGgGGGGGGK",
        "KgGGGGGGgGGGGGGK", "KgGGGGGGgGGGGGGK", "KgGGGGGGgGGGGGGK", "KgGGGGGGgGGGGGGK",
        "KgGGGGGGgGGGGGGK", "KgGGGGGGgGGGGGGK", "KgGGGGGGgGGGGGGK", "KgGGGGGGgGGGGGGK"
    ],
    'pipe_br': [
        "KKKKKKKKKKKKKKKK", "ggggggggggggggGK", "GGGGGGgGGGGGGGGK", "GGGGGGgGGGGGGGGK",
        "GGGGGGgGGGGGGGGK", "GGGGGGgGGGGGGGGK", "GGGGGGgGGGGGGGGK", "GGGGGGgGGGGGGGGK",
        "GGGGGGgGGGGGGGGK", "GGGGGGgGGGGGGGGK", "GGGGGGgGGGGGGGGK", "GGGGGGgGGGGGGGGK",
        "GGGGGGgGGGGGGGGK", "GGGGGGgGGGGGGGGK", "GGGGGGgGGGGGGGGK", "GGGGGGgGGGGGGGGK"
    ]
}

# Generate Pygame surfaces from strings
SPRITES = {}
def build_sprites():
    for name, data in SPRITE_STRINGS.items():
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        for y, row in enumerate(data):
            for x, char in enumerate(row):
                if char != ' ':
                    col = C.get(char)
                    if col is not None:
                        surf.set_at((x, y), col)
        SPRITES[name] = surf

# Level Data: Faithfully approximating World 1-1 structure
LEVEL_MAP = [
    "                                                                                                                                                                                ",
    "                                                                                                                                                                                ",
    "                                                                                                                                                                                ",
    "                                                                                                                                                                                ",
    "                                                                                                                                                                                ",
    "                                                                                                                                                                                ",
    "                                                                                                                                                                                ",
    "                                                                                                                                                                                ",
    "                                                                                                                                                                                ",
    "                ?         B?B?B                                                      ?                                                                                          ",
    "                                                                                                                                                                                ",
    "                                                                             12                        12                                                                       ",
    "                                          12                                 34                        34                                                                       ",
    "             E                  E         34     K             E    E        34      E                 34        K                                                              ",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG"
]

class GameState:
    def __init__(self):
        self.score = 0
        self.coins = 0
        self.lives = 3
        self.time = 400
        self.world = "1-1"

state = GameState()
SCENES = []

def push(scene): SCENES.append(scene)
def pop(): SCENES.pop()

class Scene:
    def handle(self, events, keys): pass
    def update(self, dt): pass
    def draw(self, surf): pass

class Entity:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.width = TILE
        self.height = TILE
        self.on_ground = False
        self.facing_right = True
        self.active = True
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.jump_power = -5.0
        self.max_speed = 2.0
        self.accel = 0.1
        self.friction = 0.05
        self.gravity = 0.2
        self.invincible = 0
        self.anim_timer = 0
        self.anim_frame = 0
        self.dead = False
        self.dead_timer = 0
        
    def update(self, colliders, dt, keys, enemies):
        if self.dead:
            self.vy += self.gravity
            self.y += self.vy
            self.dead_timer -= dt
            if self.dead_timer <= 0:
                state.lives -= 1
                if state.lives <= 0:
                    push(GameOverScreen())
                else:
                    pop()
                    push(LevelScene(state.world))
            return

        if self.invincible > 0:
            self.invincible -= dt

        # Horizontal movement
        target_speed = 0
        if keys[K_LEFT]:
            target_speed = -self.max_speed
            self.facing_right = False
        if keys[K_RIGHT]:
            target_speed = self.max_speed
            self.facing_right = True

        if target_speed != 0:
            self.vx += (target_speed - self.vx) * self.accel
        else:
            self.vx *= (1 - self.friction)

        if abs(self.vx) < 0.1: self.vx = 0

        self.x += self.vx
        self.handle_collisions(colliders, axis='x')

        # Vertical movement and Jump logic
        if not self.on_ground:
            grav = self.gravity if keys[K_SPACE] and self.vy < 0 else self.gravity * 2.5
            self.vy += grav
        else:
            if keys[K_SPACE]:
                self.vy = self.jump_power
                self.on_ground = False

        self.y += self.vy
        self.on_ground = False
        self.handle_collisions(colliders, axis='y')

        # Animation (SMA2-style with math for timing)
        if not self.on_ground:
            self.anim_frame = 'jump'
        elif abs(self.vx) > 0.1:
            self.anim_timer += dt * abs(self.vx) * 8
            # Use math.sin for a tiny bit of organic timing feel (as requested)
            frame = int(self.anim_timer + math.sin(self.anim_timer) * 0.5) % 4
            if frame == 0 or frame == 2:
                self.anim_frame = 'run1'
            else:
                self.anim_frame = 'run2'
        else:
            self.anim_frame = 'idle'
            self.anim_timer = 0

        # Enemy Collisions
        for enemy in enemies:
            if not enemy.active or self.dead: continue
            if self.get_rect().colliderect(enemy.get_rect()):
                if self.vy > 0 and self.y + self.height - 8 < enemy.y + 8:
                    self.vy = -3.0
                    enemy.stomp(self)
                elif self.invincible <= 0:
                    if hasattr(enemy, 'state') and enemy.state == 'shell_idle':
                        enemy.stomp(self)
                    else:
                        self.die()

        if self.y > NES_H + 32:
            self.die()

    def die(self):
        self.dead = True
        self.vy = -5.0
        self.dead_timer = 2.0
        self.anim_frame = 'jump'

    def handle_collisions(self, colliders, axis):
        rect = self.get_rect()
        for c in colliders:
            c_rect = c['rect']
            if rect.colliderect(c_rect):
                if axis == 'x':
                    if self.vx > 0: self.x = c_rect.left - self.width
                    if self.vx < 0: self.x = c_rect.right
                    self.vx = 0
                elif axis == 'y':
                    if self.vy > 0:
                        self.y = c_rect.top - self.height
                        self.vy = 0
                        self.on_ground = True
                    if self.vy < 0:
                        self.y = c_rect.bottom
                        self.vy = 0
                        if c['type'] == '?':
                            c['type'] = 'B'
                            state.coins += 1
                            state.score += 100
                rect = self.get_rect()

    def draw(self, surf, cam_x):
        if self.invincible > 0 and int(self.invincible * 20) % 2 == 0:
            return
            
        sprite_name = f"mario_{self.anim_frame}"
        sprite = SPRITES.get(sprite_name, SPRITES['mario_idle'])
        # SPRITE_STRINGS art has the hand/arm positioned for facing-right.
        # Flip only when Mario is facing left.
        if not self.facing_right:
            sprite = pygame.transform.flip(sprite, True, False)
        
        draw_x = int(self.x - cam_x + 0.5)
        draw_y = int(self.y + 0.5)
        surf.blit(sprite, (draw_x, draw_y))

class Enemy(Entity):
    def update_physics(self, colliders):
        self.vy += 0.2
        
        self.x += self.vx
        rect = self.get_rect()
        for c in colliders:
            if rect.colliderect(c['rect']):
                if self.vx > 0: self.x = c['rect'].left - self.width
                if self.vx < 0: self.x = c['rect'].right
                self.vx *= -1
                rect = self.get_rect()
                
        self.y += self.vy
        self.on_ground = False
        rect = self.get_rect()
        for c in colliders:
            if rect.colliderect(c['rect']):
                if self.vy > 0:
                    self.y = c['rect'].top - self.height
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.y = c['rect'].bottom
                    self.vy = 0
                rect = self.get_rect()

class Goomba(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.vx = -0.5
        self.anim_timer = 0
        self.state = 'walk'
        self.dead_timer = 0
        
    def stomp(self, player):
        self.state = 'dead'
        self.vx = 0
        self.active = False
        state.score += 100
        
    def update(self, colliders, dt, enemies):
        if self.state == 'dead':
            self.dead_timer += dt
            return
            
        self.update_physics(colliders)
        self.anim_timer += dt
        
        for e in enemies:
            if e != self and isinstance(e, Koopa) and e.state == 'shell_moving':
                if self.get_rect().colliderect(e.get_rect()):
                    self.stomp(None)
        
    def draw(self, surf, cam_x):
        if self.state == 'dead' and self.dead_timer > 0.5: return
        
        frame = 'goomba_dead' if self.state == 'dead' else ('goomba_walk1' if int(self.anim_timer * 5) % 2 == 0 else 'goomba_walk2')
        surf.blit(SPRITES[frame], (int(self.x - cam_x), int(self.y)))

class Koopa(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.vx = -0.5
        self.anim_timer = 0
        self.state = 'walk'
        
    def stomp(self, player):
        if self.state == 'walk':
            self.state = 'shell_idle'
            self.vx = 0
            self.y += 8
            self.height = 14
            state.score += 100
        elif self.state == 'shell_idle':
            self.state = 'shell_moving'
            if player and player.x < self.x:
                self.vx = 3.5
            else:
                self.vx = -3.5
            state.score += 400
        elif self.state == 'shell_moving':
            self.state = 'shell_idle'
            self.vx = 0
            
    def update(self, colliders, dt, enemies):
        self.update_physics(colliders)
        if self.state == 'walk':
            self.anim_timer += dt
            
    def draw(self, surf, cam_x):
        if not self.active: return
        
        if self.state == 'walk':
            sprite = SPRITES['koopa_walk1']
            if self.vx > 0: sprite = pygame.transform.flip(sprite, True, False)
        else:
            sprite = SPRITES['koopa_shell']
            
        surf.blit(sprite, (int(self.x - cam_x), int(self.y)))

class TitleScreen(Scene):
    def __init__(self):
        self.timer = 0
        self.mario_x = -32
        
    def handle(self, events, keys):
        for e in events:
            if e.type == KEYDOWN and e.key == K_RETURN:
                state.lives = 3
                state.score = 0
                state.coins = 0
                push(LevelScene(state.world))
                
    def update(self, dt):
        self.timer += dt
        self.mario_x += 1
        if self.mario_x > NES_W + 32:
            self.mario_x = -32
            
    def draw(self, surf):
        surf.fill(C['U'])
        
        for x in range(0, NES_W, 16):
            surf.blit(SPRITES['ground'], (x, NES_H - 16))
            surf.blit(SPRITES['ground'], (x, NES_H - 32))
            
        font_large = pygame.font.SysFont('arial', 24, bold=True)
        font_small = pygame.font.SysFont('arial', 12, bold=True)
        
        title_sh = font_large.render("KOOPA ENGINE 1.1a", True, C['K'])
        title = font_large.render("KOOPA ENGINE 1.1a", True, C['Y'])
        surf.blit(title_sh, (NES_W//2 - title.get_width()//2 + 2, 52))
        surf.blit(title, (NES_W//2 - title.get_width()//2, 50))
        
        prompt = font_small.render("PRESS ENTER TO START", True, C['W'])
        if int(self.timer * 2) % 2 == 0:
            surf.blit(prompt, (NES_W//2 - prompt.get_width()//2, 140))
            
        credits = font_small.render("1985 NINTENDO - PYTHON PORT", True, C['W'])
        surf.blit(credits, (NES_W//2 - credits.get_width()//2, NES_H - 50))
        
        surf.blit(SPRITES['koopa_walk1'], (180, NES_H - 48))
        surf.blit(SPRITES['koopa_shell'], (200, NES_H - 48))
        
        frame = 'mario_run1' if int(self.timer * 10) % 2 == 0 else 'mario_idle'
        surf.blit(SPRITES[frame], (int(self.mario_x), NES_H - 48))

class LevelScene(Scene):
    def __init__(self, level_id):
        self.player = Player(40, 40)
        self.cam_x = 0
        self.colliders = []
        self.enemies = []
        self.level_width = len(LEVEL_MAP[0]) * TILE
        state.time = 400
        
        for y, row in enumerate(LEVEL_MAP):
            for x, char in enumerate(row):
                if char in ('G', 'B', '?', '1', '2', '3', '4'):
                    self.colliders.append({'rect': pygame.Rect(x*TILE, y*TILE, TILE, TILE), 'type': char, 'x': x, 'y': y})
                elif char == 'E':
                    self.enemies.append(Goomba(x*TILE, y*TILE))
                elif char == 'K':
                    self.enemies.append(Koopa(x*TILE, y*TILE))
                    
    def handle(self, events, keys):
        for e in events:
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                pop()
                push(TitleScreen())

    def update(self, dt):
        if self.player.active and state.time is not None and state.time > 0 and not self.player.dead:
            state.time -= dt
            if state.time <= 0:
                state.time = 0
                self.player.die()
                self.player.dead_timer = 0.0

        self.player.update(self.colliders, dt, pygame.key.get_pressed(), self.enemies)
        
        for enemy in self.enemies:
            if enemy.active and enemy.x < self.cam_x + NES_W + 32:
                enemy.update(self.colliders, dt, self.enemies)
                
        target_cam = self.player.x - NES_W // 2
        if target_cam > self.cam_x:
            self.cam_x = target_cam
        self.cam_x = max(0, min(self.cam_x, self.level_width - NES_W))
        
    def draw_hud(self, surf):
        font = pygame.font.SysFont('arial', 12, bold=True)
        s_title = font.render("MARIO", True, C['W'])
        s_val = font.render(f"{state.score:06d}", True, C['W'])
        surf.blit(s_title, (20, 10))
        surf.blit(s_val, (20, 25))
        
        # Replace the leading "x" in the coin counter with a small Mario-head icon.
        surf.blit(SPRITES['question'], (100, 22), area=(0,0,10,10))
        surf.blit(SPRITES['mario_idle'], (114, 20), area=(2, 0, 12, 12))
        c_val = font.render(f"{state.coins:02d}", True, C['W'])
        surf.blit(c_val, (128, 25))
        
        w_title = font.render("WORLD", True, C['W'])
        w_val = font.render(state.world, True, C['W'])
        surf.blit(w_title, (160, 10))
        surf.blit(w_val, (168, 25))
        
        t_title = font.render("TIME", True, C['W'])
        t_val = font.render(f"{int(state.time):03d}", True, C['W'])
        surf.blit(t_title, (210, 10))
        surf.blit(t_val, (215, 25))

    def draw(self, surf):
        surf.fill(C['U'])
        
        for c in self.colliders:
            cx, cy = c['x'] * TILE, c['y'] * TILE
            if cx < self.cam_x - TILE or cx > self.cam_x + NES_W:
                continue
                
            char = c['type']
            sprite = None
            if char == 'G': sprite = SPRITES['ground']
            elif char == 'B': sprite = SPRITES['brick']
            elif char == '?': sprite = SPRITES['question']
            elif char == '1': sprite = SPRITES['pipe_tl']
            elif char == '2': sprite = SPRITES['pipe_tr']
            elif char == '3': sprite = SPRITES['pipe_bl']
            elif char == '4': sprite = SPRITES['pipe_br']
            
            if sprite:
                surf.blit(sprite, (int(cx - self.cam_x), int(cy)))
                
        for enemy in self.enemies:
            enemy.draw(surf, self.cam_x)
            
        self.player.draw(surf, self.cam_x)
        self.draw_hud(surf)

class GameOverScreen(Scene):
    def __init__(self):
        self.timer = 4.0
    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            pop()
            push(TitleScreen())
    def draw(self, surf):
        surf.fill(C['K'])
        font = pygame.font.SysFont('arial', 16, bold=True)
        text = font.render("GAME OVER", True, C['W'])
        surf.blit(text, (NES_W//2 - text.get_width()//2, NES_H//2))


# --- Main Application Execution ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("KOOPA ENGINE 1.1a - SMA2 Sprites")
    
    display_surf = pygame.Surface((NES_W, NES_H))
    
    clock = pygame.time.Clock()
    build_sprites()
    push(TitleScreen())

    while True:
        dt = clock.tick(FPS) / 1000.0
        events = pygame.event.get()
        keys = pygame.key.get_pressed()
        
        for e in events:
            if e.type == QUIT:
                pygame.quit()
                sys.exit()

        if not SCENES:
            break

        scene = SCENES[-1]
        scene.handle(events, keys)
        scene.update(dt)
        
        scene.draw(display_surf)
        
        scaled = pygame.transform.scale(display_surf, (WIDTH, HEIGHT))
        screen.blit(scaled, (0, 0))
        
        pygame.display.flip()

if __name__ == "__main__":
    main()
