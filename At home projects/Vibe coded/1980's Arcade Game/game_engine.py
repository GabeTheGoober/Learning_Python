import pygame
import random
import sys
import math
import json
import os
import time
from datetime import datetime

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# --- Config ---
class Config:
    WIDTH = 800
    HEIGHT = 600
    FPS = 60
    COLORS = {
        "WHITE": (255, 255, 255),
        "BLACK": (0, 0, 0),
        "RED": (255, 0, 0),
        "GREEN": (0, 255, 0),
        "BLUE": (0, 0, 255),
        "YELLOW": (255, 255, 0),
        "PURPLE": (128, 0, 128),
        "CYAN": (0, 255, 255),
        "ORANGE": (255, 165, 0),
        "PINK": (255, 192, 203),
        "BROWN": (165, 42, 42),
        "GRAY": (128, 128, 128)
    }
    GAME_STATES = {
        "MAIN_MENU": 0,
        "PONG": 1,
        "SNAKE": 2,
        "BREAKOUT": 3,
        "SPACE_INVADERS": 4,
        "TETRIS": 5,
        "ASTEROIDS": 6,
        "PLATFORMER": 7,
        "POKEMON": 8,
        "HIGH_SCORES": 9,
        "GAME_OVER": 10,
        "PLAYER_SELECT": 11
    }

# Save System
class SaveSystem:
    def __init__(self):
        self.save_file = "arcade_save.json"
        self.data = self.load_data()
    
    def load_data(self):
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "players": {},
            "high_scores": {
                "PONG": [], "SNAKE": [], "BREAKOUT": [], "SPACE_INVADERS": [],
                "TETRIS": [], "ASTEROIDS": [], "PLATFORMER": [], "POKEMON": []
            },
            "settings": {"sound": True, "music": True}
        }
    
    def save_data(self):
        try:
            with open(self.save_file, 'w') as f:
                json.dump(self.data, f, indent=2)
            return True
        except:
            return False
    
    def add_high_score(self, game, name, score):
        if game not in self.data["high_scores"]:
            self.data["high_scores"][game] = []
        
        self.data["high_scores"][game].append({
            "name": name,
            "score": score,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        
        # Sort and keep top 10
        self.data["high_scores"][game].sort(key=lambda x: x["score"], reverse=True)
        self.data["high_scores"][game] = self.data["high_scores"][game][:10]
        self.save_data()
    
    def get_player_data(self, name):
        if name not in self.data["players"]:
            self.data["players"][name] = {
                "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "games_played": 0,
                "total_score": 0,
                "unlocked_games": ["PONG", "SNAKE", "BREAKOUT"],
                "pokemon_collection": []
            }
        return self.data["players"][name]
    
    def update_player_stats(self, name, score):
        player = self.get_player_data(name)
        player["games_played"] += 1
        player["total_score"] += score
        
        # Unlock games based on total score
        if player["total_score"] >= 5000 and "SPACE_INVADERS" not in player["unlocked_games"]:
            player["unlocked_games"].append("SPACE_INVADERS")
        if player["total_score"] >= 10000 and "TETRIS" not in player["unlocked_games"]:
            player["unlocked_games"].append("TETRIS")
        if player["total_score"] >= 20000 and "ASTEROIDS" not in player["unlocked_games"]:
            player["unlocked_games"].append("ASTEROIDS")
        if player["total_score"] >= 50000 and "PLATFORMER" not in player["unlocked_games"]:
            player["unlocked_games"].append("PLATFORMER")
        if player["total_score"] >= 100000 and "POKEMON" not in player["unlocked_games"]:
            player["unlocked_games"].append("POKEMON")
        
        self.save_data()

# Sound System
class SoundSystem:
    def __init__(self):
        self.sounds = {}
        self.create_sounds()
    
    def create_sounds(self):
        # Create simple beep sounds programmatically
        try:
            import numpy
            self.sounds["beep1"] = self.generate_beep(440, 100)  # A
            self.sounds["beep2"] = self.generate_beep(523, 100)  # C
            self.sounds["beep3"] = self.generate_beep(659, 100)  # E
            self.sounds["explosion"] = self.generate_explosion()
            self.sounds["powerup"] = self.generate_powerup()
        except:
            # Fallback silent sounds if numpy not available
            silent_sound = pygame.mixer.Sound(buffer=bytearray([]))
            for sound_name in ["beep1", "beep2", "beep3", "explosion", "powerup"]:
                self.sounds[sound_name] = silent_sound
    
    def generate_beep(self, frequency, duration):
        sample_rate = 22050
        n_samples = int(round(duration * 0.001 * sample_rate))
        import numpy
        buf = numpy.zeros((n_samples, 2), dtype=numpy.int16)
        max_sample = 2**(16 - 1) - 1
        for s in range(n_samples):
            t = float(s) / sample_rate
            buf[s][0] = int(round(max_sample * math.sin(2 * math.pi * frequency * t)))
            buf[s][1] = int(round(max_sample * math.sin(2 * math.pi * frequency * t)))
        return pygame.sndarray.make_sound(buf)
    
    def generate_explosion(self):
        # Simple explosion-like sound
        sample_rate = 22050
        duration = 500
        n_samples = int(round(duration * 0.001 * sample_rate))
        import numpy
        buf = numpy.zeros((n_samples, 2), dtype=numpy.int16)
        max_sample = 2**(16 - 1) - 1
        for s in range(n_samples):
            t = float(s) / sample_rate
            freq = 100 + 900 * math.exp(-5 * t)
            buf[s][0] = int(round(max_sample * math.exp(-3 * t) * math.sin(2 * math.pi * freq * t)))
            buf[s][1] = int(round(max_sample * math.exp(-3 * t) * math.sin(2 * math.pi * freq * t)))
        return pygame.sndarray.make_sound(buf)
    
    def generate_powerup(self):
        sample_rate = 22050
        duration = 300
        n_samples = int(round(duration * 0.001 * sample_rate))
        import numpy
        buf = numpy.zeros((n_samples, 2), dtype=numpy.int16)
        max_sample = 2**(16 - 1) - 1
        for s in range(n_samples):
            t = float(s) / sample_rate
            freq = 200 + 600 * t
            buf[s][0] = int(round(max_sample * math.exp(-2 * t) * math.sin(2 * math.pi * freq * t)))
            buf[s][1] = int(round(max_sample * math.exp(-2 * t) * math.sin(2 * math.pi * freq * t)))
        return pygame.sndarray.make_sound(buf)
    
    def play(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

# Create sound system
sound_system = SoundSystem()

# Enhanced Button with 80s style
class RetroButton:
    def __init__(self, x, y, width, height, text, color, hover_color, font_size=24, bevel=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = Config.COLORS[color] if isinstance(color, str) else color
        self.hover_color = Config.COLORS[hover_color] if isinstance(hover_color, str) else hover_color
        self.is_hovered = False
        self.bevel = bevel
        self.font = pygame.font.Font(None, font_size)
        self.clicked = False
        
    def draw(self, surface):
        # Draw button with 80s style bevel
        if self.bevel:
            # Main button
            pygame.draw.rect(surface, self.hover_color if self.is_hovered else self.color, self.rect)
            
            # Bevel effect
            if self.is_hovered:
                # Pressed look
                pygame.draw.line(surface, Config.COLORS["BLACK"], self.rect.topleft, self.rect.topright, 2)
                pygame.draw.line(surface, Config.COLORS["BLACK"], self.rect.topleft, self.rect.bottomleft, 2)
                pygame.draw.line(surface, Config.COLORS["WHITE"], self.rect.bottomleft, self.rect.bottomright, 2)
                pygame.draw.line(surface, Config.COLORS["WHITE"], self.rect.topright, self.rect.bottomright, 2)
            else:
                # Raised look
                pygame.draw.line(surface, Config.COLORS["WHITE"], self.rect.topleft, self.rect.topright, 2)
                pygame.draw.line(surface, Config.COLORS["WHITE"], self.rect.topleft, self.rect.bottomleft, 2)
                pygame.draw.line(surface, Config.COLORS["BLACK"], self.rect.bottomleft, self.rect.bottomright, 2)
                pygame.draw.line(surface, Config.COLORS["BLACK"], self.rect.topright, self.rect.bottomright, 2)
        else:
            # Simple button
            color = self.hover_color if self.is_hovered else self.color
            pygame.draw.rect(surface, color, self.rect)
            pygame.draw.rect(surface, Config.COLORS["WHITE"], self.rect, 2)
        
        # Draw text
        text_color = Config.COLORS["BLACK"] if self.color in [Config.COLORS["YELLOW"], Config.COLORS["WHITE"]] else Config.COLORS["WHITE"]
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos, click):
        if self.rect.collidepoint(pos) and click:
            sound_system.play("beep1")
            return True
        return False

# Base game objects
class GameObject:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = Config.COLORS[color] if isinstance(color, str) else color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

class MovableObject(GameObject):
    def __init__(self, x, y, width, height, color, speed):
        super().__init__(x, y, width, height, color)
        self.speed = speed
        self.velocity = pygame.math.Vector2(0, 0)

    def move(self, direction, boundaries):
        if direction == "UP" and self.rect.top > boundaries.top:
            self.rect.y -= self.speed
        elif direction == "DOWN" and self.rect.bottom < boundaries.bottom:
            self.rect.y += self.speed
        elif direction == "LEFT" and self.rect.left > boundaries.left:
            self.rect.x -= self.speed
        elif direction == "RIGHT" and self.rect.right < boundaries.right:
            self.rect.x += self.speed

    def update(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

class Paddle(MovableObject):
    def __init__(self, x, y, width, height, color, speed):
        super().__init__(x, y, width, height, color, speed)
        self.score = 0
        
    def ai_move(self, ball, boundaries):
        if ball.rect.centery < self.rect.centery and self.rect.top > boundaries.top:
            self.rect.y -= self.speed
        elif ball.rect.centery > self.rect.centery and self.rect.bottom < boundaries.bottom:
            self.rect.y += self.speed

class RoundBall:
    def __init__(self, x, y, radius, color, speed):
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        self.radius = radius
        self.color = Config.COLORS[color] if isinstance(color, str) else color
        self.speed_x = speed * random.choice([-1, 1])
        self.speed_y = random.uniform(-speed/2, speed/2)
        self.base_speed = speed

    def reset(self):
        self.rect.center = (Config.WIDTH // 2, Config.HEIGHT // 2)
        self.speed_x = self.base_speed * random.choice([-1, 1])
        self.speed_y = random.uniform(-self.base_speed/2, self.base_speed/2)

    def update(self, paddles, boundaries):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Boundary collision
        if self.rect.top <= boundaries.top or self.rect.bottom >= boundaries.bottom:
            self.speed_y *= -1
            sound_system.play("beep1")

        # Paddle collision with speed increase
        for paddle in paddles:
            if self.rect.colliderect(paddle.rect):
                self.speed_x *= -1.1  # Increase speed by 10% with each bounce
                # Adjust angle based on where ball hits paddle
                relative_intersect_y = (paddle.rect.centery - self.rect.centery) / (paddle.rect.height / 2)
                self.speed_y = -relative_intersect_y * 5
                sound_system.play("beep2")

        # Score
        if self.rect.left <= boundaries.left:
            paddles[1].score += 1
            self.reset()
            return True
        elif self.rect.right >= boundaries.right:
            paddles[0].score += 1
            self.reset()
            return True
        return False

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.rect.center, self.radius)

class BreakoutBall:
    def __init__(self, x, y, radius, color, speed):
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        self.radius = radius
        self.color = Config.COLORS[color] if isinstance(color, str) else color
        self.speed_x = 0
        self.speed_y = -speed  # Start moving upward
        self.base_speed = speed

    def reset(self):
        self.rect.center = (Config.WIDTH // 2, Config.HEIGHT // 2 + 100)
        self.speed_x = random.choice([-self.base_speed, self.base_speed])
        self.speed_y = -self.base_speed  # Always start moving up

    def update(self, paddle, bricks, boundaries):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Boundary collision
        if self.rect.left <= boundaries.left or self.rect.right >= boundaries.right:
            self.speed_x *= -1
            sound_system.play("beep1")

        if self.rect.top <= boundaries.top:
            self.speed_y *= -1
            sound_system.play("beep1")

        # Paddle collision
        if self.rect.colliderect(paddle.rect):
            self.speed_y = -abs(self.speed_y)  # Always bounce upward
            # Adjust angle based on where ball hits paddle
            relative_intersect_x = (paddle.rect.centerx - self.rect.centerx) / (paddle.rect.width / 2)
            self.speed_x = -relative_intersect_x * 5
            sound_system.play("beep2")

        # Brick collision
        brick_hit = False
        for brick in bricks[:]:
            if not brick.destroyed and self.rect.colliderect(brick.rect):
                brick.destroyed = True
                self.speed_y *= -1
                brick_hit = True
                sound_system.play("beep3")
                break
                
        return brick_hit

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.rect.center, self.radius)

class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.body = [pygame.Rect(100, 100, 20, 20)]
        self.direction = "RIGHT"
        self.grow = False
        self.score = 0

    def move(self):
        head = self.body[0].copy()

        if self.direction == "UP":
            head.y -= 20
        elif self.direction == "DOWN":
            head.y += 20
        elif self.direction == "LEFT":
            head.x -= 20
        elif self.direction == "RIGHT":
            head.x += 20

        self.body.insert(0, head)

        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def check_collision(self, boundaries):
        # Wall collision
        if (self.body[0].left < boundaries.left or
            self.body[0].right > boundaries.right or
            self.body[0].top < boundaries.top or
            self.body[0].bottom > boundaries.bottom):
            return True

        # Self collision
        for segment in self.body[1:]:
            if self.body[0].colliderect(segment):
                return True

        return False

    def check_food(self, food):
        if self.body[0].colliderect(food.rect):
            self.grow = True
            self.score += 10
            return True
        return False

    def draw(self, surface):
        for i, segment in enumerate(self.body):
            color = Config.COLORS["GREEN"] if i == 0 else Config.COLORS["BLUE"]
            pygame.draw.rect(surface, color, segment)
            pygame.draw.rect(surface, Config.COLORS["WHITE"], segment, 1)

class Food:
    def __init__(self, boundaries):
        self.boundaries = boundaries
        self.rect = pygame.Rect(0, 0, 20, 20)
        self.respawn()

    def respawn(self):
        x = random.randrange(self.boundaries.left, self.boundaries.right - 20, 20)
        y = random.randrange(self.boundaries.top, self.boundaries.bottom - 20, 20)
        self.rect.topleft = (x, y)

    def draw(self, surface):
        pygame.draw.rect(surface, Config.COLORS["RED"], self.rect)

class Brick:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = Config.COLORS[color] if isinstance(color, str) else color
        self.destroyed = False

    def draw(self, surface):
        if not self.destroyed:
            pygame.draw.rect(surface, self.color, self.rect)
            pygame.draw.rect(surface, Config.COLORS["WHITE"], self.rect, 1)

class Invader:
    def __init__(self, x, y, size, color):
        self.rect = pygame.Rect(x, y, size, size)
        self.color = Config.COLORS[color] if isinstance(color, str) else color
        self.alive = True

    def draw(self, surface):
        if self.alive:
            pygame.draw.rect(surface, self.color, self.rect)

class PlayerShip:
    def __init__(self, x, y, width, height, color, speed):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = Config.COLORS[color] if isinstance(color, str) else color
        self.speed = speed
        self.lives = 3
        self.score = 0

    def move(self, direction, boundaries):
        if direction == "LEFT" and self.rect.left > boundaries.left:
            self.rect.x -= self.speed
        if direction == "RIGHT" and self.rect.right < boundaries.right:
            self.rect.x += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

class Bullet:
    def __init__(self, x, y, width, height, color, speed):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = Config.COLORS[color] if isinstance(color, str) else color
        self.speed = speed
        self.active = True

    def update(self, boundaries):
        self.rect.y += self.speed
        if self.rect.bottom < boundaries.top or self.rect.top > boundaries.bottom:
            self.active = False

    def draw(self, surface):
        if self.active:
            pygame.draw.rect(surface, self.color, self.rect)

# Tetris Game Implementation
class TetrisPiece:
    def __init__(self, shape, x, y):
        self.shape = shape
        self.x = x
        self.y = y
        self.color = random.choice(["RED", "GREEN", "BLUE", "YELLOW", "PURPLE", "CYAN", "ORANGE"])

    def rotate(self):
        # Transpose the shape matrix and reverse each row to rotate 90 degrees
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

    def get_positions(self):
        positions = []
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    positions.append((self.x + x, self.y + y))
        return positions

class TetrisGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = [[None for _ in range(10)] for _ in range(20)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.game_over = False
        self.fall_time = 0
        self.fall_speed = 500  # milliseconds

    def new_piece(self):
        shapes = [
            [[1, 1, 1, 1]],  # I
            [[1, 1], [1, 1]],  # O
            [[1, 1, 1], [0, 1, 0]],  # T
            [[1, 1, 1], [1, 0, 0]],  # L
            [[1, 1, 1], [0, 0, 1]],  # J
            [[0, 1, 1], [1, 1, 0]],  # S
            [[1, 1, 0], [0, 1, 1]]   # Z
        ]
        shape = random.choice(shapes)
        return TetrisPiece(shape, 3, 0)

    def valid_move(self, piece, x_offset=0, y_offset=0):
        for x, y in piece.get_positions():
            x += x_offset
            y += y_offset
            if x < 0 or x >= 10 or y >= 20 or (y >= 0 and self.board[y][x] is not None):
                return False
        return True

    def lock_piece(self, piece):
        for x, y in piece.get_positions():
            if y < 0:
                self.game_over = True
                return
            self.board[y][x] = piece.color

        # Check for completed lines
        lines_cleared = 0
        for y in range(20):
            if all(self.board[y]):
                lines_cleared += 1
                # Remove the line
                for y2 in range(y, 0, -1):
                    self.board[y2] = self.board[y2-1][:]
                self.board[0] = [None for _ in range(10)]

        # Update score
        if lines_cleared == 1:
            self.score += 100
        elif lines_cleared == 2:
            self.score += 300
        elif lines_cleared == 3:
            self.score += 500
        elif lines_cleared == 4:
            self.score += 800

    def update(self, current_time):
        if self.game_over:
            return

        # Move piece down automatically
        if current_time - self.fall_time > self.fall_speed:
            self.fall_time = current_time
            if self.valid_move(self.current_piece, 0, 1):
                self.current_piece.y += 1
            else:
                self.lock_piece(self.current_piece)
                self.current_piece = self.next_piece
                self.next_piece = self.new_piece()

    def move(self, dx):
        if self.valid_move(self.current_piece, dx, 0):
            self.current_piece.x += dx

    def rotate_piece(self):
        original_shape = self.current_piece.shape
        self.current_piece.rotate()
        if not self.valid_move(self.current_piece):
            self.current_piece.shape = original_shape

    def draw(self, surface, x, y, cell_size=20):
        # Draw board
        for row in range(20):
            for col in range(10):
                rect = pygame.Rect(x + col * cell_size, y + row * cell_size, cell_size, cell_size)
                if self.board[row][col]:
                    pygame.draw.rect(surface, Config.COLORS[self.board[row][col]], rect)
                pygame.draw.rect(surface, Config.COLORS["WHITE"], rect, 1)

        # Draw current piece
        if not self.game_over:
            for pos_x, pos_y in self.current_piece.get_positions():
                if pos_y >= 0:
                    rect = pygame.Rect(x + pos_x * cell_size, y + pos_y * cell_size, cell_size, cell_size)
                    pygame.draw.rect(surface, Config.COLORS[self.current_piece.color], rect)
                    pygame.draw.rect(surface, Config.COLORS["WHITE"], rect, 1)

        # Draw next piece preview
        for pos_x, pos_y in self.next_piece.get_positions():
            rect = pygame.Rect(x + 11 * cell_size + pos_x * cell_size, y + 2 * cell_size + pos_y * cell_size, cell_size, cell_size)
            pygame.draw.rect(surface, Config.COLORS[self.next_piece.color], rect)
            pygame.draw.rect(surface, Config.COLORS["WHITE"], rect, 1)

# Asteroids Game Implementation
class Asteroid:
    def __init__(self, x, y, size, speed):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.angle = random.uniform(0, 2 * math.pi)
        self.vertices = self.generate_vertices()

    def generate_vertices(self):
        vertices = []
        for i in range(8):
            angle = 2 * math.pi * i / 8
            distance = self.size + random.uniform(-self.size/3, self.size/3)
            x = self.x + math.cos(angle) * distance
            y = self.y + math.sin(angle) * distance
            vertices.append((x, y))
        return vertices

    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        # Wrap around screen
        if self.x < 0: self.x = Config.WIDTH
        if self.x > Config.WIDTH: self.x = 0
        if self.y < 0: self.y = Config.HEIGHT
        if self.y > Config.HEIGHT: self.y = 0

    def draw(self, surface):
        pygame.draw.polygon(surface, Config.COLORS["WHITE"], self.vertices, 2)

class AsteroidsShip:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.rotation_speed = 5
        self.acceleration = 0.1
        self.max_speed = 5
        self.bullets = []
        self.lives = 3

    def rotate(self, direction):
        self.angle += direction * self.rotation_speed

    def accelerate(self):
        self.speed += self.acceleration
        if self.speed > self.max_speed:
            self.speed = self.max_speed

    def decelerate(self):
        self.speed -= self.acceleration
        if self.speed < 0:
            self.speed = 0

    def shoot(self):
        bullet_x = self.x + math.cos(math.radians(self.angle)) * 20
        bullet_y = self.y + math.sin(math.radians(self.angle)) * 20
        self.bullets.append({
            'x': bullet_x,
            'y': bullet_y,
            'angle': self.angle,
            'speed': 10,
            'life': 60  # frames
        })

    def update(self):
        # Update position
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed
        
        # Wrap around screen
        if self.x < 0: self.x = Config.WIDTH
        if self.x > Config.WIDTH: self.x = 0
        if self.y < 0: self.y = Config.HEIGHT
        if self.y > Config.HEIGHT: self.y = 0
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet['x'] += math.cos(math.radians(bullet['angle'])) * bullet['speed']
            bullet['y'] += math.sin(math.radians(bullet['angle'])) * bullet['speed']
            bullet['life'] -= 1
            
            # Remove old bullets
            if bullet['life'] <= 0:
                self.bullets.remove(bullet)
            
            # Wrap bullets around screen
            if bullet['x'] < 0: bullet['x'] = Config.WIDTH
            if bullet['x'] > Config.WIDTH: bullet['x'] = 0
            if bullet['y'] < 0: bullet['y'] = Config.HEIGHT
            if bullet['y'] > Config.HEIGHT: bullet['y'] = 0

    def draw(self, surface):
        # Draw ship
        points = [
            (self.x + math.cos(math.radians(self.angle)) * 20, 
             self.y + math.sin(math.radians(self.angle)) * 20),
            (self.x + math.cos(math.radians(self.angle + 150)) * 15, 
             self.y + math.sin(math.radians(self.angle + 150)) * 15),
            (self.x + math.cos(math.radians(self.angle - 150)) * 15, 
             self.y + math.sin(math.radians(self.angle - 150)) * 15)
        ]
        pygame.draw.polygon(surface, Config.COLORS["WHITE"], points, 2)
        
        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.circle(surface, Config.COLORS["WHITE"], (int(bullet['x']), int(bullet['y'])), 2)

# Platformer Game (Mario-like)
class PlatformerPlayer:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 50)
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = 5
        self.jump_power = 12
        self.gravity = 0.5
        self.is_jumping = False
        self.facing_right = True
        self.lives = 3
        self.score = 0
        self.coins = 0
        
    def update(self, platforms, enemies, coins):
        # Apply gravity
        self.velocity.y += self.gravity
        
        # Update position
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        
        # Check platform collisions
        on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Landing on top of platform
                if self.velocity.y > 0 and self.rect.bottom > platform.rect.top and self.rect.top < platform.rect.top:
                    self.rect.bottom = platform.rect.top
                    self.velocity.y = 0
                    on_ground = True
                # Hitting platform from below
                elif self.velocity.y < 0 and self.rect.top < platform.rect.bottom and self.rect.bottom > platform.rect.bottom:
                    self.rect.top = platform.rect.bottom
                    self.velocity.y = 0
                # Hitting platform from sides
                elif self.velocity.x > 0 and self.rect.right > platform.rect.left and self.rect.left < platform.rect.left:
                    self.rect.right = platform.rect.left
                elif self.velocity.x < 0 and self.rect.left < platform.rect.right and self.rect.right > platform.rect.right:
                    self.rect.left = platform.rect.right
        
        # Check enemy collisions
        for enemy in enemies[:]:
            if self.rect.colliderect(enemy.rect):
                # Jumping on enemy
                if self.velocity.y > 0 and self.rect.bottom < enemy.rect.top + 10:
                    enemies.remove(enemy)
                    self.velocity.y = -self.jump_power * 0.7
                    self.score += 100
                    sound_system.play("beep2")
                else:
                    self.lives -= 1
                    self.rect.x = 100
                    self.rect.y = 100
                    self.velocity = pygame.math.Vector2(0, 0)
                    sound_system.play("explosion")
        
        # Check coin collisions
        for coin in coins[:]:
            if self.rect.colliderect(coin.rect):
                coins.remove(coin)
                self.coins += 1
                self.score += 50
                sound_system.play("powerup")
        
        # Reset jumping state
        if on_ground:
            self.is_jumping = False
        
        # Screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > Config.WIDTH:
            self.rect.right = Config.WIDTH
        if self.rect.bottom > Config.HEIGHT:
            self.rect.bottom = Config.HEIGHT
            self.velocity.y = 0
            on_ground = True
        
        return self.lives > 0
    
    def jump(self):
        if not self.is_jumping:
            self.velocity.y = -self.jump_power
            self.is_jumping = True
            sound_system.play("beep1")
    
    def draw(self, surface):
        # Draw player as a simple character
        color = Config.COLORS["RED"] if self.facing_right else Config.COLORS["PINK"]
        pygame.draw.rect(surface, color, self.rect)
        
        # Draw eyes
        eye_x = self.rect.right - 10 if self.facing_right else self.rect.left + 10
        pygame.draw.circle(surface, Config.COLORS["WHITE"], (eye_x, self.rect.top + 15), 5)

class Platform:
    def __init__(self, x, y, width, height, color="BROWN"):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = Config.COLORS[color] if isinstance(color, str) else color
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

class Enemy:
    def __init__(self, x, y, speed=2):
        self.rect = pygame.Rect(x, y, 40, 30)
        self.speed = speed
        self.direction = 1
    
    def update(self, platforms):
        self.rect.x += self.speed * self.direction
        
        # Change direction at edges or when hitting a wall
        change_dir = False
        if self.rect.left <= 0 or self.rect.right >= Config.WIDTH:
            change_dir = True
        
        for platform in platforms:
            if (self.direction > 0 and self.rect.colliderect(pygame.Rect(platform.rect.left, platform.rect.top, 1, platform.rect.height)) or
                self.direction < 0 and self.rect.colliderect(pygame.Rect(platform.rect.right - 1, platform.rect.top, 1, platform.rect.height))):
                change_dir = True
        
        if change_dir:
            self.direction *= -1
    
    def draw(self, surface):
        pygame.draw.rect(surface, Config.COLORS["GREEN"], self.rect)
        # Draw spikes
        for i in range(3):
            x = self.rect.left + 10 + i * 10
            points = [(x, self.rect.top), (x + 5, self.rect.top - 10), (x + 10, self.rect.top)]
            pygame.draw.polygon(surface, Config.COLORS["RED"], points)

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
    
    def draw(self, surface):
        pygame.draw.circle(surface, Config.COLORS["YELLOW"], self.rect.center, 10)
        pygame.draw.circle(surface, Config.COLORS["ORANGE"], self.rect.center, 7)

# Pokemon-like RPG
class PokemonPlayer:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.speed = 3
        self.direction = "DOWN"
        self.pokemon = []
        self.current_pokemon = None
        self.badges = 0
    
    def move(self, direction, boundaries):
        self.direction = direction
        if direction == "UP" and self.rect.top > boundaries.top:
            self.rect.y -= self.speed
        elif direction == "DOWN" and self.rect.bottom < boundaries.bottom:
            self.rect.y += self.speed
        elif direction == "LEFT" and self.rect.left > boundaries.left:
            self.rect.x -= self.speed
        elif direction == "RIGHT" and self.rect.right < boundaries.right:
            self.rect.x += self.speed
    
    def draw(self, surface):
        # Draw player as a simple character
        color = Config.COLORS["RED"]
        pygame.draw.rect(surface, color, self.rect)
        
        # Draw face based on direction
        if self.direction == "UP":
            pygame.draw.circle(surface, Config.COLORS["BLACK"], (self.rect.centerx, self.rect.top + 10), 5)
        elif self.direction == "DOWN":
            pygame.draw.circle(surface, Config.COLORS["BLACK"], (self.rect.centerx, self.rect.bottom - 10), 5)
        elif self.direction == "LEFT":
            pygame.draw.circle(surface, Config.COLORS["BLACK"], (self.rect.left + 10, self.rect.centery), 5)
        elif self.direction == "RIGHT":
            pygame.draw.circle(surface, Config.COLORS["BLACK"], (self.rect.right - 10, self.rect.centery), 5)

class Pokemon:
    def __init__(self, name, type, level=5):
        self.name = name
        self.type = type
        self.level = level
        self.hp = 20 + level * 5
        self.max_hp = 20 + level * 5
        self.attack = 5 + level
        self.defense = 5 + level
        self.moves = []
        
        # Assign moves based on type
        if type == "FIRE":
            self.moves = [("Ember", 25), ("Fire Spin", 35)]
            self.color = Config.COLORS["RED"]
        elif type == "WATER":
            self.moves = [("Water Gun", 25), ("Bubble", 35)]
            self.color = Config.COLORS["BLUE"]
        elif type == "GRASS":
            self.moves = [("Vine Whip", 25), ("Razor Leaf", 35)]
            self.color = Config.COLORS["GREEN"]
        elif type == "ELECTRIC":
            self.moves = [("Thunder Shock", 25), ("Thunderbolt", 35)]
            self.color = Config.COLORS["YELLOW"]
    
    def draw(self, surface, x, y, size=50):
        rect = pygame.Rect(x, y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, Config.COLORS["BLACK"], rect, 2)
        
        # Draw name and level
        font = pygame.font.Font(None, 20)
        name_text = font.render(self.name, True, Config.COLORS["WHITE"])
        level_text = font.render(f"Lv{self.level}", True, Config.COLORS["WHITE"])
        
        surface.blit(name_text, (x + 5, y + 5))
        surface.blit(level_text, (x + size - 30, y + 5))
        
        # Draw HP bar
        hp_width = (size - 10) * (self.hp / self.max_hp)
        pygame.draw.rect(surface, Config.COLORS["RED"], (x + 5, y + size - 15, hp_width, 8))

class PokemonBattle:
    def __init__(self, player_pokemon, wild_pokemon):
        self.player_pokemon = player_pokemon
        self.wild_pokemon = wild_pokemon
        self.state = "SELECT_MOVE"  # SELECT_MOVE, BATTLE, RESULT
        self.selected_move = 0
        self.battle_text = []
        self.text_timer = 0
        self.result = None  # WIN, LOSE, CATCH
    
    def update(self):
        if self.state == "BATTLE":
            self.text_timer += 1
            if self.text_timer > 120:  # 2 seconds
                self.state = "SELECT_MOVE"
                self.text_timer = 0
                
                # Check if battle should end
                if self.wild_pokemon.hp <= 0:
                    self.result = "WIN"
                    self.battle_text = [f"{self.wild_pokemon.name} fainted!"]
                elif self.player_pokemon.hp <= 0:
                    self.result = "LOSE"
                    self.battle_text = [f"{self.player_pokemon.name} fainted!"]
    
    def select_move(self, move_index):
        if self.state != "SELECT_MOVE":
            return
            
        self.selected_move = move_index
        move_name, move_power = self.player_pokemon.moves[move_index]
        
        # Player attacks
        damage = max(1, move_power + self.player_pokemon.attack - self.wild_pokemon.defense)
        self.wild_pokemon.hp -= damage
        self.battle_text = [f"{self.player_pokemon.name} used {move_name}!", f"It did {damage} damage!"]
        
        # Wild pokemon attacks if still alive
        if self.wild_pokemon.hp > 0:
            wild_move_name, wild_move_power = random.choice(self.wild_pokemon.moves)
            wild_damage = max(1, wild_move_power + self.wild_pokemon.attack - self.player_pokemon.defense)
            self.player_pokemon.hp -= wild_damage
            self.battle_text.append(f"{self.wild_pokemon.name} used {wild_move_name}!")
            self.battle_text.append(f"It did {wild_damage} damage!")
        
        self.state = "BATTLE"
        self.text_timer = 0
    
    def try_catch(self):
        if self.state != "SELECT_MOVE":
            return
            
        # Higher chance to catch if HP is low
        catch_chance = 0.3 + (1 - self.wild_pokemon.hp / self.wild_pokemon.max_hp) * 0.5
        if random.random() < catch_chance:
            self.result = "CATCH"
            self.battle_text = [f"Caught {self.wild_pokemon.name}!"]
        else:
            self.battle_text = [f"Failed to catch {self.wild_pokemon.name}!"]
            # Wild pokemon attacks
            wild_move_name, wild_move_power = random.choice(self.wild_pokemon.moves)
            wild_damage = max(1, wild_move_power + self.wild_pokemon.attack - self.player_pokemon.defense)
            self.player_pokemon.hp -= wild_damage
            self.battle_text.append(f"{self.wild_pokemon.name} used {wild_move_name}!")
            self.battle_text.append(f"It did {wild_damage} damage!")
        
        self.state = "BATTLE"
        self.text_timer = 0
    
    def draw(self, surface):
        # Draw player pokemon
        self.player_pokemon.draw(surface, 100, 300)
        
        # Draw wild pokemon
        self.wild_pokemon.draw(surface, 500, 100)
        
        # Draw battle text
        font = pygame.font.Font(None, 24)
        for i, text in enumerate(self.battle_text):
            text_surface = font.render(text, True, Config.COLORS["WHITE"])
            surface.blit(text_surface, (50, 400 + i * 30))
        
        # Draw move selection if in SELECT_MOVE state
        if self.state == "SELECT_MOVE":
            for i, (move_name, move_power) in enumerate(self.player_pokemon.moves):
                color = Config.COLORS["YELLOW"] if i == self.selected_move else Config.COLORS["WHITE"]
                move_text = f"{i+1}. {move_name} (Power: {move_power})"
                text_surface = font.render(move_text, True, color)
                surface.blit(text_surface, (50, 450 + i * 30))
            
            # Draw catch option
            catch_color = Config.COLORS["YELLOW"] if self.selected_move == len(self.player_pokemon.moves) else Config.COLORS["WHITE"]
            catch_text = f"{len(self.player_pokemon.moves)+1}. Try to Catch"
            text_surface = font.render(catch_text, True, catch_color)
            surface.blit(text_surface, (50, 450 + len(self.player_pokemon.moves) * 30))

# --- Enhanced Game Engine ---
class GameEngine:
    def __init__(self):
        self.screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
        pygame.display.set_caption("RETRO ARCADE MEGA COLLECTION - 1980s EDITION")
        self.clock = pygame.time.Clock()
        self.current_state = Config.GAME_STATES["PLAYER_SELECT"]
        self.game_mode = "SOLO"
        self.score = 0
        self.lives = 3
        self.player_name = ""
        self.save_system = SaveSystem()
        
        # Game objects
        self.pong_objects = {}
        self.snake_objects = {}
        self.breakout_objects = {}
        self.space_invaders_objects = {}
        self.tetris_objects = {}
        self.asteroids_objects = {}
        self.platformer_objects = {}
        self.pokemon_objects = {}
        
        # 80s style background effect
        self.stars = [(random.randint(0, Config.WIDTH), random.randint(0, Config.HEIGHT), 
                      random.randint(1, 3)) for _ in range(100)]
        self.star_timer = 0
        
    def draw_text(self, text, size, x, y, color=Config.COLORS["WHITE"], centered=True):
        font = pygame.font.Font(None, size)
        text_surface = font.render(str(text), True, color)
        if centered:
            text_rect = text_surface.get_rect(center=(x, y))
        else:
            text_rect = text_surface.get_rect(topleft=(x, y))
        self.screen.blit(text_surface, text_rect)
        return text_rect

    def draw_80s_background(self):
        # Draw starfield background
        self.screen.fill(Config.COLORS["BLACK"])
        
        # Animate stars
        self.star_timer += 1
        if self.star_timer > 5:
            self.star_timer = 0
            for i in range(len(self.stars)):
                x, y, speed = self.stars[i]
                x -= speed
                if x < 0:
                    x = Config.WIDTH
                    y = random.randint(0, Config.HEIGHT)
                self.stars[i] = (x, y, speed)
        
        # Draw stars with proper RGB color tuples
        for x, y, speed in self.stars:
            # Create a proper RGB color tuple
            brightness = min(255, 150 + speed * 50)  # Ensure brightness doesn't exceed 255
            color = (int(brightness), int(brightness), int(brightness))  # Convert to integers
            pygame.draw.circle(self.screen, color, (int(x), int(y)), speed)  # Convert coordinates to integers
        
        # Draw scanlines for CRT effect
        for y in range(0, Config.HEIGHT, 4):
            pygame.draw.line(self.screen, (0, 0, 0), (0, y), (Config.WIDTH, y), 1)

    def get_boundaries(self):
        return pygame.Rect(50, 50, Config.WIDTH - 100, Config.HEIGHT - 100)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_state != Config.GAME_STATES["MAIN_MENU"]:
                        self.current_state = Config.GAME_STATES["MAIN_MENU"]
                    else:
                        return False
            self.handle_game_specific_events(event)
        return True

    def handle_game_specific_events(self, event):
        # Placeholder for game-specific event handling
        pass

    def update(self):
        if self.current_state == Config.GAME_STATES["PLAYER_SELECT"]:
            self.update_player_select()
        elif self.current_state == Config.GAME_STATES["MAIN_MENU"]:
            self.update_menu()
        elif self.current_state == Config.GAME_STATES["PONG"]:
            self.update_pong()
        elif self.current_state == Config.GAME_STATES["SNAKE"]:
            self.update_snake()
        elif self.current_state == Config.GAME_STATES["BREAKOUT"]:
            self.update_breakout()
        elif self.current_state == Config.GAME_STATES["SPACE_INVADERS"]:
            self.update_space_invaders()
        elif self.current_state == Config.GAME_STATES["TETRIS"]:
            self.update_tetris()
        elif self.current_state == Config.GAME_STATES["ASTEROIDS"]:
            self.update_asteroids()
        elif self.current_state == Config.GAME_STATES["PLATFORMER"]:
            self.update_platformer()
        elif self.current_state == Config.GAME_STATES["POKEMON"]:
            self.update_pokemon()
        elif self.current_state == Config.GAME_STATES["HIGH_SCORES"]:
            self.update_high_scores()
        elif self.current_state == Config.GAME_STATES["GAME_OVER"]:
            self.update_game_over()

    def draw(self):
        self.draw_80s_background()
        
        if self.current_state == Config.GAME_STATES["PLAYER_SELECT"]:
            self.draw_player_select()
        elif self.current_state == Config.GAME_STATES["MAIN_MENU"]:
            self.draw_menu()
        elif self.current_state == Config.GAME_STATES["PONG"]:
            self.draw_pong()
        elif self.current_state == Config.GAME_STATES["SNAKE"]:
            self.draw_snake()
        elif self.current_state == Config.GAME_STATES["BREAKOUT"]:
            self.draw_breakout()
        elif self.current_state == Config.GAME_STATES["SPACE_INVADERS"]:
            self.draw_space_invaders()
        elif self.current_state == Config.GAME_STATES["TETRIS"]:
            self.draw_tetris()
        elif self.current_state == Config.GAME_STATES["ASTEROIDS"]:
            self.draw_asteroids()
        elif self.current_state == Config.GAME_STATES["PLATFORMER"]:
            self.draw_platformer()
        elif self.current_state == Config.GAME_STATES["POKEMON"]:
            self.draw_pokemon()
        elif self.current_state == Config.GAME_STATES["HIGH_SCORES"]:
            self.draw_high_scores()
        elif self.current_state == Config.GAME_STATES["GAME_OVER"]:
            self.draw_game_over()
            
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(Config.FPS)
        pygame.quit()
        sys.exit()

    # Player Select Screen
    def update_player_select(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        
        # Draw input box for player name
        name_rect = pygame.Rect(Config.WIDTH//2 - 150, Config.HEIGHT//2 - 50, 300, 50)
        
        # Check if clicking on the input box
        if mouse_click and name_rect.collidepoint(mouse_pos):
            # Simple text input
            self.get_player_name()
        
        # Start button
        start_button = RetroButton(Config.WIDTH//2 - 100, Config.HEIGHT//2 + 50, 200, 50, 
                                  "START GAME", "GREEN", "YELLOW")
        start_button.check_hover(mouse_pos)
        
        if start_button.is_clicked(mouse_pos, mouse_click) and self.player_name:
            self.current_state = Config.GAME_STATES["MAIN_MENU"]
            # Load player data
            self.save_system.get_player_data(self.player_name)

    def get_player_name(self):
        # Simple text input using pygame
        name = ""
        input_active = True
        font = pygame.font.Font(None, 36)
        
        while input_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        # Only allow alphanumeric and some special chars
                        if event.unicode.isalnum() or event.unicode in " -_":
                            name += event.unicode
            
            # Draw
            self.draw_80s_background()
            self.draw_text("ENTER YOUR NAME", 48, Config.WIDTH//2, Config.HEIGHT//2 - 100, "CYAN")
            
            # Draw input box
            input_rect = pygame.Rect(Config.WIDTH//2 - 150, Config.HEIGHT//2 - 25, 300, 50)
            pygame.draw.rect(self.screen, Config.COLORS["BLUE"], input_rect)
            pygame.draw.rect(self.screen, Config.COLORS["WHITE"], input_rect, 2)
            
            # Draw text
            name_surface = font.render(name, True, Config.COLORS["WHITE"])
            self.screen.blit(name_surface, (input_rect.x + 10, input_rect.y + 10))
            
            self.draw_text("Press ENTER when done", 24, Config.WIDTH//2, Config.HEIGHT//2 + 50, "YELLOW")
            
            pygame.display.flip()
            self.clock.tick(Config.FPS)
        
        self.player_name = name

    def draw_player_select(self):
        self.draw_text("RETRO ARCADE MEGA COLLECTION", 64, Config.WIDTH//2, 150, "CYAN")
        self.draw_text("1980s EDITION", 48, Config.WIDTH//2, 200, "YELLOW")
        
        # Draw input box for player name
        name_rect = pygame.Rect(Config.WIDTH//2 - 150, Config.HEIGHT//2 - 50, 300, 50)
        pygame.draw.rect(self.screen, Config.COLORS["BLUE"], name_rect)
        pygame.draw.rect(self.screen, Config.COLORS["WHITE"], name_rect, 2)
        
        # Draw player name or prompt
        if self.player_name:
            self.draw_text(self.player_name, 36, Config.WIDTH//2, Config.HEIGHT//2 - 25, "WHITE")
        else:
            self.draw_text("Click to enter name", 24, Config.WIDTH//2, Config.HEIGHT//2 - 25, "GRAY")
        
        self.draw_text("PLAYER NAME:", 36, Config.WIDTH//2, Config.HEIGHT//2 - 100, "WHITE")
        
        # Draw start button
        start_button = RetroButton(Config.WIDTH//2 - 100, Config.HEIGHT//2 + 50, 200, 50, 
                                  "START GAME", "GREEN", "YELLOW")
        start_button.draw(self.screen)

    # Menu methods
    def update_menu(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        
        player_data = self.save_system.get_player_data(self.player_name)
        unlocked_games = player_data["unlocked_games"]
        
        # Create buttons for unlocked games
        game_buttons = []
        game_list = ["PONG", "SNAKE", "BREAKOUT", "SPACE_INVADERS", "TETRIS", "ASTEROIDS", "PLATFORMER", "POKEMON"]
        for i, game in enumerate(game_list):
            if game in unlocked_games:
                color = "GREEN"
            else:
                color = "GRAY"
            
            button = RetroButton(Config.WIDTH//2 - 100, 150 + i * 50, 200, 40, game, color, "YELLOW")
            game_buttons.append(button)
        
        # Other menu buttons
        other_buttons = [
            RetroButton(Config.WIDTH//2 - 100, 550, 200, 40, "HIGH SCORES", "PURPLE", "CYAN"),
            RetroButton(Config.WIDTH//2 - 100, 600, 200, 40, "QUIT", "RED", "ORANGE")
        ]
        
        # Check hover states
        for button in game_buttons + other_buttons:
            button.check_hover(mouse_pos)
        
        # Check game selection (only for unlocked games)
        for i, button in enumerate(game_buttons):
            if button.is_clicked(mouse_pos, mouse_click) and game_list[i] in unlocked_games:
                self.current_state = Config.GAME_STATES[game_list[i]]
                if game_list[i] == "PONG":
                    self.init_pong()
                elif game_list[i] == "SNAKE":
                    self.init_snake()
                elif game_list[i] == "BREAKOUT":
                    self.init_breakout()
                elif game_list[i] == "SPACE_INVADERS":
                    self.init_space_invaders()
                elif game_list[i] == "TETRIS":
                    self.init_tetris()
                elif game_list[i] == "ASTEROIDS":
                    self.init_asteroids()
                elif game_list[i] == "PLATFORMER":
                    self.init_platformer()
                elif game_list[i] == "POKEMON":
                    self.init_pokemon()
        
        # Check other buttons
        if other_buttons[0].is_clicked(mouse_pos, mouse_click):
            self.current_state = Config.GAME_STATES["HIGH_SCORES"]
        elif other_buttons[1].is_clicked(mouse_pos, mouse_click):
            pygame.quit()
            sys.exit()

    def draw_menu(self):
        self.draw_text("RETRO ARCADE MEGA COLLECTION", 48, Config.WIDTH//2, 80, "CYAN")
        self.draw_text(f"Player: {self.player_name}", 24, Config.WIDTH//2, 120, "YELLOW")
        
        player_data = self.save_system.get_player_data(self.player_name)
        unlocked_games = player_data["unlocked_games"]
        
        # Draw game buttons
        game_list = ["PONG", "SNAKE", "BREAKOUT", "SPACE_INVADERS", "TETRIS", "ASTEROIDS", "PLATFORMER", "POKEMON"]
        for i, game in enumerate(game_list):
            if game in unlocked_games:
                color = "GREEN"
            else:
                color = "GRAY"
            
            button = RetroButton(Config.WIDTH//2 - 100, 150 + i * 50, 200, 40, game, color, "YELLOW")
            button.draw(self.screen)
            
            # Show lock icon for locked games
            if game not in unlocked_games:
                lock_rect = pygame.Rect(Config.WIDTH//2 + 80, 150 + i * 50 + 10, 20, 20)
                pygame.draw.rect(self.screen, Config.COLORS["YELLOW"], lock_rect)
        
        # Draw other buttons
        other_buttons = [
            RetroButton(Config.WIDTH//2 - 100, 550, 200, 40, "HIGH SCORES", "PURPLE", "CYAN"),
            RetroButton(Config.WIDTH//2 - 100, 600, 200, 40, "QUIT", "RED", "ORANGE")
        ]
        
        for button in other_buttons:
            button.draw(self.screen)
        
        # Draw player stats
        stats_text = f"Total Score: {player_data['total_score']} | Games Played: {player_data['games_played']}"
        self.draw_text(stats_text, 24, Config.WIDTH//2, Config.HEIGHT - 30, "WHITE")

    # High Scores Screen
    def update_high_scores(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        
        back_button = RetroButton(Config.WIDTH//2 - 100, Config.HEIGHT - 50, 200, 40, "BACK", "BLUE", "CYAN")
        back_button.check_hover(mouse_pos)
        
        if back_button.is_clicked(mouse_pos, mouse_click):
            self.current_state = Config.GAME_STATES["MAIN_MENU"]
    
    def draw_high_scores(self):
        self.draw_text("HIGH SCORES", 64, Config.WIDTH//2, 80, "YELLOW")
        
        game_list = ["PONG", "SNAKE", "BREAKOUT", "SPACE_INVADERS", "TETRIS", "ASTEROIDS", "PLATFORMER", "POKEMON"]
        x_positions = [100, 300, 500, 700]
        
        for col, game in enumerate(game_list[:4]):
            self.draw_text(game, 24, x_positions[col], 150, "CYAN")
            scores = self.save_system.data["high_scores"].get(game, [])
            
            for i, score in enumerate(scores[:5]):
                score_text = f"{i+1}. {score['name']}: {score['score']}"
                self.draw_text(score_text, 20, x_positions[col], 180 + i * 30, "WHITE")
        
        for col, game in enumerate(game_list[4:]):
            self.draw_text(game, 24, x_positions[col], 350, "CYAN")
            scores = self.save_system.data["high_scores"].get(game, [])
            
            for i, score in enumerate(scores[:5]):
                score_text = f"{i+1}. {score['name']}: {score['score']}"
                self.draw_text(score_text, 20, x_positions[col], 380 + i * 30, "WHITE")
        
        # Draw back button
        back_button = RetroButton(Config.WIDTH//2 - 100, Config.HEIGHT - 50, 200, 40, "BACK", "BLUE", "CYAN")
        back_button.draw(self.screen)

    # Game Over Screen
    def update_game_over(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE] or keys[pygame.K_RETURN]:
            # Save score if it's high enough
            if self.score > 0:
                # Check if score qualifies for high scores
                game_name = ""
                if self.current_state == Config.GAME_STATES["PONG"]:
                    game_name = "PONG"
                elif self.current_state == Config.GAME_STATES["SNAKE"]:
                    game_name = "SNAKE"
                elif self.current_state == Config.GAME_STATES["BREAKOUT"]:
                    game_name = "BREAKOUT"
                elif self.current_state == Config.GAME_STATES["SPACE_INVADERS"]:
                    game_name = "SPACE_INVADERS"
                elif self.current_state == Config.GAME_STATES["TETRIS"]:
                    game_name = "TETRIS"
                elif self.current_state == Config.GAME_STATES["ASTEROIDS"]:
                    game_name = "ASTEROIDS"
                elif self.current_state == Config.GAME_STATES["PLATFORMER"]:
                    game_name = "PLATFORMER"
                elif self.current_state == Config.GAME_STATES["POKEMON"]:
                    game_name = "POKEMON"
                
                if game_name:
                    # Show high score input if score is in top 10
                    high_scores = self.save_system.data["high_scores"].get(game_name, [])
                    if len(high_scores) < 10 or self.score > high_scores[-1]["score"]:
                        self.get_high_score_name(game_name)
                    else:
                        self.save_system.update_player_stats(self.player_name, self.score)
                
            self.current_state = Config.GAME_STATES["MAIN_MENU"]

    def get_high_score_name(self, game_name):
        name = self.player_name
        input_active = True
        font = pygame.font.Font(None, 36)
        
        while input_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        if event.unicode.isalnum() or event.unicode in " -_":
                            name += event.unicode
            
            # Draw
            self.draw_80s_background()
            self.draw_text("HIGH SCORE!", 64, Config.WIDTH//2, Config.HEIGHT//2 - 100, "YELLOW")
            self.draw_text(f"Score: {self.score}", 48, Config.WIDTH//2, Config.HEIGHT//2 - 50, "GREEN")
            self.draw_text("Enter your name:", 36, Config.WIDTH//2, Config.HEIGHT//2, "WHITE")
            
            # Draw input box
            input_rect = pygame.Rect(Config.WIDTH//2 - 150, Config.HEIGHT//2 + 50, 300, 50)
            pygame.draw.rect(self.screen, Config.COLORS["BLUE"], input_rect)
            pygame.draw.rect(self.screen, Config.COLORS["WHITE"], input_rect, 2)
            
            # Draw text
            name_surface = font.render(name, True, Config.COLORS["WHITE"])
            self.screen.blit(name_surface, (input_rect.x + 10, input_rect.y + 10))
            
            self.draw_text("Press ENTER to continue", 24, Config.WIDTH//2, Config.HEIGHT//2 + 120, "YELLOW")
            
            pygame.display.flip()
            self.clock.tick(Config.FPS)
        
        # Save high score
        self.save_system.add_high_score(game_name, name, self.score)
        self.save_system.update_player_stats(self.player_name, self.score)

    def draw_game_over(self):
        self.draw_text("GAME OVER", 72, Config.WIDTH//2, Config.HEIGHT//2 - 50, "RED")
        self.draw_text(f"Final Score: {self.score}", 48, Config.WIDTH//2, Config.HEIGHT//2 + 20, "YELLOW")
        self.draw_text("Press ESC or ENTER to continue", 36, Config.WIDTH//2, Config.HEIGHT//2 + 100, "WHITE")

    # Game initialization methods
    def init_pong(self):
        boundaries = self.get_boundaries()
        self.pong_objects = {
            "boundaries": boundaries,
            "paddle1": Paddle(boundaries.left + 10, boundaries.centery - 50, 15, 100, "BLUE", 7),
            "paddle2": Paddle(boundaries.right - 25, boundaries.centery - 50, 15, 100, "RED", 7),
            "ball": RoundBall(Config.WIDTH//2, Config.HEIGHT//2, 8, "WHITE", 5)
        }
        self.score = 0

    def init_snake(self):
        boundaries = self.get_boundaries()
        self.snake_objects = {
            "boundaries": boundaries,
            "snake": Snake(),
            "food": Food(boundaries)
        }
        self.score = 0

    def init_breakout(self):
        boundaries = self.get_boundaries()
        paddle = Paddle(boundaries.centerx - 50, boundaries.bottom - 20, 100, 15, "BLUE", 8)
        ball = BreakoutBall(boundaries.centerx, boundaries.bottom - 40, 8, "WHITE", 5)

        # Create bricks
        bricks = []
        brick_width = 70
        brick_height = 20
        brick_colors = ["RED", "GREEN", "BLUE", "YELLOW", "PURPLE"]

        for row in range(5):
            for col in range(10):
                x = boundaries.left + col * (brick_width + 5)
                y = boundaries.top + row * (brick_height + 5)
                color = brick_colors[row]
                bricks.append(Brick(x, y, brick_width, brick_height, color))

        self.breakout_objects = {
            "boundaries": boundaries,
            "paddle": paddle,
            "ball": ball,
            "bricks": bricks
        }
        self.score = 0

    def init_space_invaders(self):
        boundaries = self.get_boundaries()
        player = PlayerShip(boundaries.centerx - 25, boundaries.bottom - 40, 50, 30, "GREEN", 5)

        invaders = []
        invader_size = 30
        for row in range(5):
            for col in range(10):
                x = boundaries.left + col * (invader_size + 10)
                y = boundaries.top + row * (invader_size + 10)
                color = "RED" if row % 2 == 0 else "YELLOW"
                invaders.append(Invader(x, y, invader_size, color))

        self.space_invaders_objects = {
            "boundaries": boundaries,
            "player": player,
            "invaders": invaders,
            "player_bullets": [],
            "invader_bullets": [],
            "invader_direction": 1,
            "invader_speed": 1,
            "last_invader_shot": pygame.time.get_ticks(),
            "invader_shot_delay": 1000
        }
        self.score = 0

    def init_tetris(self):
        self.tetris_objects = {
            "game": TetrisGame(),
            "last_update": pygame.time.get_ticks()
        }
        self.score = 0

    def init_asteroids(self):
        ship = AsteroidsShip(Config.WIDTH//2, Config.HEIGHT//2)
        asteroids = [Asteroid(random.randint(0, Config.WIDTH), random.randint(0, Config.HEIGHT), 
                            random.randint(20, 50), random.uniform(1, 3)) for _ in range(5)]
        
        self.asteroids_objects = {
            "ship": ship,
            "asteroids": asteroids,
            "score": 0
        }
        self.score = 0

    def init_platformer(self):
        player = PlatformerPlayer(100, 100)
        
        # Create platforms
        platforms = [
            Platform(0, Config.HEIGHT - 50, Config.WIDTH, 50),  # Ground
            Platform(100, 400, 200, 20),
            Platform(400, 300, 200, 20),
            Platform(200, 200, 150, 20),
            Platform(500, 150, 100, 20)
        ]
        
        # Create enemies
        enemies = [
            Enemy(300, Config.HEIGHT - 80),
            Enemy(500, 250),
            Enemy(150, 350)
        ]
        
        # Create coins
        coins = [
            Coin(150, 350),
            Coin(450, 250),
            Coin(250, 150),
            Coin(550, 100)
        ]
        
        self.platformer_objects = {
            "player": player,
            "platforms": platforms,
            "enemies": enemies,
            "coins": coins,
            "camera_x": 0
        }
        self.score = 0

    def init_pokemon(self):
        player = PokemonPlayer(Config.WIDTH//2, Config.HEIGHT//2)
        
        # Start with a basic pokemon
        starter_pokemon = Pokemon("CHARMA", "FIRE", 5)
        player.pokemon.append(starter_pokemon)
        player.current_pokemon = starter_pokemon
        
        self.pokemon_objects = {
            "player": player,
            "map_objects": [],
            "in_battle": False,
            "battle": None
        }
        self.score = 0

    # Game update methods
    def update_pong(self):
        keys = pygame.key.get_pressed()
        boundaries = self.pong_objects["boundaries"]
        paddle1 = self.pong_objects["paddle1"]
        paddle2 = self.pong_objects["paddle2"]
        ball = self.pong_objects["ball"]

        # Player 1 controls (W/S)
        if keys[pygame.K_w]:
            paddle1.move("UP", boundaries)
        if keys[pygame.K_s]:
            paddle1.move("DOWN", boundaries)

        # Player 2 controls or AI
        if self.game_mode == "PVP":
            if keys[pygame.K_UP]:
                paddle2.move("UP", boundaries)
            if keys[pygame.K_DOWN]:
                paddle2.move("DOWN", boundaries)
        else:  # AI mode
            paddle2.ai_move(ball, boundaries)

        # Update ball
        if ball.update([paddle1, paddle2], boundaries):
            sound_system.play("beep3")

        # Update score
        self.score = max(paddle1.score, paddle2.score)

        # Check win condition
        if paddle1.score >= 10 or paddle2.score >= 10:
            self.current_state = Config.GAME_STATES["GAME_OVER"]

    def draw_pong(self):
        boundaries = self.pong_objects["boundaries"]
        paddle1 = self.pong_objects["paddle1"]
        paddle2 = self.pong_objects["paddle2"]
        ball = self.pong_objects["ball"]

        # Draw boundaries
        pygame.draw.rect(self.screen, Config.COLORS["WHITE"], boundaries, 2)

        # Draw center line
        pygame.draw.line(self.screen, Config.COLORS["WHITE"], (Config.WIDTH//2, boundaries.top), (Config.WIDTH//2, boundaries.bottom), 1)

        # Draw paddles and ball
        paddle1.draw(self.screen)
        paddle2.draw(self.screen)
        ball.draw(self.screen)

        # Draw scores
        self.draw_text(str(paddle1.score), 48, Config.WIDTH//4, 30)
        self.draw_text(str(paddle2.score), 48, 3*Config.WIDTH//4, 30)

        # Draw game mode
        self.draw_text(f"Mode: {self.game_mode}", 24, Config.WIDTH//2, 30)

    def update_snake(self):
        keys = pygame.key.get_pressed()
        snake = self.snake_objects["snake"]
        food = self.snake_objects["food"]
        boundaries = self.snake_objects["boundaries"]

        # Change direction (prevent 180-degree turns)
        if keys[pygame.K_UP] and snake.direction != "DOWN":
            snake.direction = "UP"
        elif keys[pygame.K_DOWN] and snake.direction != "UP":
            snake.direction = "DOWN"
        elif keys[pygame.K_LEFT] and snake.direction != "RIGHT":
            snake.direction = "LEFT"
        elif keys[pygame.K_RIGHT] and snake.direction != "LEFT":
            snake.direction = "RIGHT"

        # Move snake
        snake.move()

        # Check for collisions
        if snake.check_collision(boundaries):
            self.current_state = Config.GAME_STATES["GAME_OVER"]

        # Check if snake ate food
        if snake.check_food(food):
            food.respawn()
            # Make sure food doesn't spawn on snake
            while any(food.rect.colliderect(segment) for segment in snake.body):
                food.respawn()

        # Control game speed for snake
        pygame.time.delay(100)

        # Update score
        self.score = snake.score

    def draw_snake(self):
        boundaries = self.snake_objects["boundaries"]
        snake = self.snake_objects["snake"]
        food = self.snake_objects["food"]

        # Draw boundaries
        pygame.draw.rect(self.screen, Config.COLORS["WHITE"], boundaries, 2)

        # Draw snake and food
        snake.draw(self.screen)
        food.draw(self.screen)

        # Draw score
        self.draw_text(f"Score: {snake.score}", 36, Config.WIDTH//2, 30)

    def update_breakout(self):
        keys = pygame.key.get_pressed()
        boundaries = self.breakout_objects["boundaries"]
        paddle = self.breakout_objects["paddle"]
        ball = self.breakout_objects["ball"]
        bricks = self.breakout_objects["bricks"]

        # Move paddle
        if keys[pygame.K_LEFT]:
            paddle.move("LEFT", boundaries)
        if keys[pygame.K_RIGHT]:
            paddle.move("RIGHT", boundaries)

        # Update ball
        if ball.update(paddle, bricks, boundaries):
            paddle.score += 10

        # Check if ball is lost
        if ball.rect.top > boundaries.bottom:
            ball.reset()
            paddle.score = max(0, paddle.score - 5)  # Penalty for missing ball

        # Update score
        self.score = paddle.score

        # Check if all bricks are destroyed
        if all(brick.destroyed for brick in bricks):
            self.score += 1000  # Bonus for completing level
            self.current_state = Config.GAME_STATES["GAME_OVER"]

        # Check if player lost all points
        if paddle.score < 0:
            self.current_state = Config.GAME_STATES["GAME_OVER"]

    def draw_breakout(self):
        boundaries = self.breakout_objects["boundaries"]
        paddle = self.breakout_objects["paddle"]
        ball = self.breakout_objects["ball"]
        bricks = self.breakout_objects["bricks"]

        # Draw boundaries
        pygame.draw.rect(self.screen, Config.COLORS["WHITE"], boundaries, 2)

        # Draw paddle, ball, and bricks
        paddle.draw(self.screen)
        ball.draw(self.screen)
        for brick in bricks:
            brick.draw(self.screen)

        # Draw score
        self.draw_text(f"Score: {paddle.score}", 36, Config.WIDTH//2, 30)

    def update_space_invaders(self):
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()
        
        boundaries = self.space_invaders_objects["boundaries"]
        player = self.space_invaders_objects["player"]
        invaders = self.space_invaders_objects["invaders"]
        player_bullets = self.space_invaders_objects["player_bullets"]
        invader_bullets = self.space_invaders_objects["invader_bullets"]
        invader_direction = self.space_invaders_objects["invader_direction"]
        invader_speed = self.space_invaders_objects["invader_speed"]
        last_invader_shot = self.space_invaders_objects["last_invader_shot"]
        invader_shot_delay = self.space_invaders_objects["invader_shot_delay"]

        # Move player
        if keys[pygame.K_LEFT]:
            player.move("LEFT", boundaries)
        if keys[pygame.K_RIGHT]:
            player.move("RIGHT", boundaries)

        # Shoot bullet
        if keys[pygame.K_SPACE]:
            # Limit firing rate
            if not player_bullets or current_time - getattr(self, 'last_shot', 0) > 500:
                bullet = Bullet(
                    player.rect.centerx - 2,
                    player.rect.top,
                    4, 10, "CYAN", -7
                )
                player_bullets.append(bullet)
                self.last_shot = current_time

        # Move invaders
        move_down = False
        for invader in invaders:
            if invader.alive:
                invader.rect.x += invader_direction * invader_speed

                # Check if any invader hits the boundary
                if (invader.rect.right >= boundaries.right and invader_direction > 0) or \
                   (invader.rect.left <= boundaries.left and invader_direction < 0):
                    move_down = True

        # Move invaders down and change direction if needed
        if move_down:
            invader_direction *= -1
            for invader in invaders:
                if invader.alive:
                    invader.rect.y += 20

        # Invaders shoot randomly
        if current_time - last_invader_shot > invader_shot_delay and invaders:
            # Select a random alive invader to shoot
            alive_invaders = [inv for inv in invaders if inv.alive]
            if alive_invaders:
                shooter = random.choice(alive_invaders)
                bullet = Bullet(
                    shooter.rect.centerx - 2,
                    shooter.rect.bottom,
                    4, 10, "RED", 5
                )
                invader_bullets.append(bullet)
                self.space_invaders_objects["last_invader_shot"] = current_time

        # Update player bullets
        for bullet in player_bullets[:]:
            bullet.update(boundaries)
            if not bullet.active:
                player_bullets.remove(bullet)
                continue

            # Check for collision with invaders
            for invader in invaders:
                if invader.alive and bullet.rect.colliderect(invader.rect):
                    invader.alive = False
                    bullet.active = False
                    player.score += 10
                    if bullet in player_bullets:
                        player_bullets.remove(bullet)
                    break

        # Update invader bullets
        for bullet in invader_bullets[:]:
            bullet.update(boundaries)
            if not bullet.active:
                invader_bullets.remove(bullet)
                continue

            # Check for collision with player
            if bullet.rect.colliderect(player.rect):
                player.lives -= 1
                bullet.active = False
                if bullet in invader_bullets:
                    invader_bullets.remove(bullet)

                if player.lives <= 0:
                    self.current_state = Config.GAME_STATES["GAME_OVER"]

        # Check if all invaders are destroyed
        if all(not invader.alive for invader in invaders):
            player.score += 1000  # Bonus for clearing level
            self.score = player.score
            self.current_state = Config.GAME_STATES["GAME_OVER"]

        # Check if invaders reached the bottom
        for invader in invaders:
            if invader.alive and invader.rect.bottom >= player.rect.top:
                self.current_state = Config.GAME_STATES["GAME_OVER"]

        # Update the objects back
        self.space_invaders_objects.update({
            "player_bullets": player_bullets,
            "invader_bullets": invader_bullets,
            "invader_direction": invader_direction
        })

        # Update score
        self.score = player.score

    def draw_space_invaders(self):
        boundaries = self.space_invaders_objects["boundaries"]
        player = self.space_invaders_objects["player"]
        invaders = self.space_invaders_objects["invaders"]
        player_bullets = self.space_invaders_objects["player_bullets"]
        invader_bullets = self.space_invaders_objects["invader_bullets"]

        # Draw boundaries
        pygame.draw.rect(self.screen, Config.COLORS["WHITE"], boundaries, 2)

        # Draw player, invaders, and bullets
        player.draw(self.screen)
        for invader in invaders:
            invader.draw(self.screen)
        for bullet in player_bullets + invader_bullets:
            bullet.draw(self.screen)

        # Draw score and lives
        self.draw_text(f"Score: {player.score}", 36, Config.WIDTH//4, 30)
        self.draw_text(f"Lives: {player.lives}", 36, 3*Config.WIDTH//4, 30)

    def update_tetris(self):
        keys = pygame.key.get_pressed()
        game = self.tetris_objects["game"]
        current_time = pygame.time.get_ticks()

        # Handle input
        if keys[pygame.K_LEFT]:
            game.move(-1)
        if keys[pygame.K_RIGHT]:
            game.move(1)
        if keys[pygame.K_DOWN]:
            game.fall_speed = 100  # Speed up falling when down is pressed
        else:
            game.fall_speed = 500

        if keys[pygame.K_UP]:
            game.rotate_piece()

        # Update game
        game.update(current_time)

        # Update score
        self.score = game.score

        # Check for game over
        if game.game_over:
            self.current_state = Config.GAME_STATES["GAME_OVER"]

    def draw_tetris(self):
        game = self.tetris_objects["game"]
        
        # Draw game board
        game.draw(self.screen, 200, 50)
        
        # Draw score and next piece label
        self.draw_text(f"Score: {game.score}", 36, Config.WIDTH//2, 30)
        self.draw_text("Next Piece:", 24, 500, 70, "WHITE")

    def update_asteroids(self):
        keys = pygame.key.get_pressed()
        ship = self.asteroids_objects["ship"]
        asteroids = self.asteroids_objects["asteroids"]

        # Handle ship controls
        if keys[pygame.K_LEFT]:
            ship.rotate(-1)
        if keys[pygame.K_RIGHT]:
            ship.rotate(1)
        if keys[pygame.K_UP]:
            ship.accelerate()
        if keys[pygame.K_DOWN]:
            ship.decelerate()
        if keys[pygame.K_SPACE]:
            if not hasattr(self, 'last_shot_asteroids') or pygame.time.get_ticks() - self.last_shot_asteroids > 200:
                ship.shoot()
                self.last_shot_asteroids = pygame.time.get_ticks()

        # Update ship
        ship.update()

        # Update asteroids
        for asteroid in asteroids:
            asteroid.update()

        # Check collisions between bullets and asteroids
        for bullet in ship.bullets[:]:
            for asteroid in asteroids[:]:
                # Simple distance-based collision
                distance = math.sqrt((bullet['x'] - asteroid.x)**2 + (bullet['y'] - asteroid.y)**2)
                if distance < asteroid.size:
                    ship.bullets.remove(bullet)
                    asteroids.remove(asteroid)
                    self.asteroids_objects["score"] += 100
                    
                    # Create smaller asteroids if the original was large enough
                    if asteroid.size > 25:
                        for _ in range(2):
                            new_asteroid = Asteroid(asteroid.x, asteroid.y, asteroid.size//2, asteroid.speed * 1.5)
                            asteroids.append(new_asteroid)
                    break

        # Check collisions between ship and asteroids
        for asteroid in asteroids:
            distance = math.sqrt((ship.x - asteroid.x)**2 + (ship.y - asteroid.y)**2)
            if distance < asteroid.size + 15:  # 15 is roughly the ship size
                ship.lives -= 1
                asteroids.remove(asteroid)
                if ship.lives <= 0:
                    self.current_state = Config.GAME_STATES["GAME_OVER"]

        # Add new asteroids if there are too few
        while len(asteroids) < 5:
            asteroids.append(Asteroid(random.randint(0, Config.WIDTH), random.randint(0, Config.HEIGHT), 
                                    random.randint(20, 50), random.uniform(1, 3)))

        # Update score
        self.score = self.asteroids_objects["score"]

    def draw_asteroids(self):
        ship = self.asteroids_objects["ship"]
        asteroids = self.asteroids_objects["asteroids"]

        # Draw ship and asteroids
        ship.draw(self.screen)
        for asteroid in asteroids:
            asteroid.draw(self.screen)

        # Draw score and lives
        self.draw_text(f"Score: {self.asteroids_objects['score']}", 36, Config.WIDTH//4, 30)
        self.draw_text(f"Lives: {ship.lives}", 36, 3*Config.WIDTH//4, 30)

    def update_platformer(self):
        keys = pygame.key.get_pressed()
        player = self.platformer_objects["player"]
        platforms = self.platformer_objects["platforms"]
        enemies = self.platformer_objects["enemies"]
        coins = self.platformer_objects["coins"]

        # Handle input
        player.velocity.x = 0
        if keys[pygame.K_LEFT]:
            player.velocity.x = -player.speed
            player.facing_right = False
        if keys[pygame.K_RIGHT]:
            player.velocity.x = player.speed
            player.facing_right = True
        if keys[pygame.K_SPACE]:
            player.jump()

        # Update game objects
        still_alive = player.update(platforms, enemies, coins)

        # Update enemies
        for enemy in enemies:
            enemy.update(platforms)

        # Update score
        self.score = player.score

        # Check if game over
        if not still_alive:
            self.current_state = Config.GAME_STATES["GAME_OVER"]

        # Check if level complete (all coins collected)
        if len(coins) == 0:
            self.score += 1000  # Level completion bonus
            self.current_state = Config.GAME_STATES["GAME_OVER"]

    def draw_platformer(self):
        player = self.platformer_objects["player"]
        platforms = self.platformer_objects["platforms"]
        enemies = self.platformer_objects["enemies"]
        coins = self.platformer_objects["coins"]

        # Draw platforms
        for platform in platforms:
            platform.draw(self.screen)

        # Draw enemies
        for enemy in enemies:
            enemy.draw(self.screen)

        # Draw coins
        for coin in coins:
            coin.draw(self.screen)

        # Draw player
        player.draw(self.screen)

        # Draw HUD
        self.draw_text(f"Score: {player.score}", 36, 100, 30, "WHITE")
        self.draw_text(f"Coins: {player.coins}", 36, 300, 30, "YELLOW")
        self.draw_text(f"Lives: {player.lives}", 36, 500, 30, "RED")

    def update_pokemon(self):
        keys = pygame.key.get_pressed()
        player = self.pokemon_objects["player"]
        
        if not self.pokemon_objects["in_battle"]:
            # Handle movement
            if keys[pygame.K_UP]:
                player.move("UP", self.get_boundaries())
            elif keys[pygame.K_DOWN]:
                player.move("DOWN", self.get_boundaries())
            elif keys[pygame.K_LEFT]:
                player.move("LEFT", self.get_boundaries())
            elif keys[pygame.K_RIGHT]:
                player.move("RIGHT", self.get_boundaries())
            
            # Random encounter
            if random.random() < 0.01:  # 1% chance per frame
                wild_pokemon = random.choice([
                    Pokemon("BULBA", "GRASS", random.randint(3, 7)),
                    Pokemon("SQUIRT", "WATER", random.randint(3, 7)),
                    Pokemon("PIKA", "ELECTRIC", random.randint(3, 7))
                ])
                self.pokemon_objects["battle"] = PokemonBattle(player.current_pokemon, wild_pokemon)
                self.pokemon_objects["in_battle"] = True
        else:
            # Battle logic
            battle = self.pokemon_objects["battle"]
            battle.update()
            
            # Handle battle input
            if keys[pygame.K_1]:
                battle.selected_move = 0
            elif keys[pygame.K_2]:
                battle.selected_move = 1
            elif keys[pygame.K_3]:
                battle.selected_move = 2
            
            if keys[pygame.K_RETURN]:
                if battle.selected_move < len(battle.player_pokemon.moves):
                    battle.select_move(battle.selected_move)
                else:
                    battle.try_catch()
            
            # Check battle result
            if battle.result:
                if battle.result == "WIN":
                    self.score += battle.wild_pokemon.level * 100
                    sound_system.play("powerup")
                elif battle.result == "CATCH":
                    player.pokemon.append(battle.wild_pokemon)
                    self.score += battle.wild_pokemon.level * 200
                    sound_system.play("powerup")
                
                self.pokemon_objects["in_battle"] = False
                # Return to overworld after a short delay
                pygame.time.delay(1000)

    def draw_pokemon(self):
        player = self.pokemon_objects["player"]
        
        if not self.pokemon_objects["in_battle"]:
            # Draw overworld
            player.draw(self.screen)
            
            # Draw player stats
            self.draw_text(f"Pokemon: {len(player.pokemon)}", 24, 100, 30, "WHITE")
            self.draw_text(f"Badges: {player.badges}", 24, 300, 30, "YELLOW")
            self.draw_text("Walk around to find Pokemon!", 24, Config.WIDTH//2, Config.HEIGHT - 30, "GREEN")
        else:
            # Draw battle
            battle = self.pokemon_objects["battle"]
            battle.draw(self.screen)
            
            # Draw battle instructions
            self.draw_text("Use 1-2 to select moves, 3 to catch, ENTER to confirm", 20, Config.WIDTH//2, Config.HEIGHT - 50, "WHITE")

# Main function
def main():
    game = GameEngine()
    game.run()

if __name__ == "__main__":
    main()