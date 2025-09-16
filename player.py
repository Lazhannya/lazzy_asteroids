import pygame
from constants import *
from circleshape import CircleShape


class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shot_cooldown = 0  # Cooldown timer for shooting

    def draw(self, screen):
        pygame.draw.polygon(screen, "white", self.triangle(), 2)

    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def rotate(self, direction, dt):
        if direction == "left":
            self.rotation -= PLAYER_TURN_SPEED * dt
        elif direction == "right":
            self.rotation += PLAYER_TURN_SPEED * dt
        self.rotation %= 360  # Keep rotation within 0-359 degrees

    def update(self, dt):
        # Update cooldown timer
        if self.shot_cooldown > 0:
            self.shot_cooldown -= dt
            
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rotate("left", dt)
        if keys[pygame.K_d]:
            self.rotate("right", dt)
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-dt)
        if keys[pygame.K_SPACE] and self.shot_cooldown <= 0:
            self.shoot()
            self.shot_cooldown = 0.3  # 300 ms cooldown between shots

    def move(self, dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        self.position += forward * PLAYER_SPEED * dt
        # Screen wrapping
        if self.position.x < 0:
            self.position.x = SCREEN_WIDTH
        elif self.position.x > SCREEN_WIDTH:
            self.position.x = 0
        if self.position.y < 0:
            self.position.y = SCREEN_HEIGHT
        elif self.position.y > SCREEN_HEIGHT:
            self.position.y = 0

    def shoot(self):
        from shot import Shot
        
        # Calculate the position for the shot (at the front of the player)
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        shot_pos = self.position + forward * self.radius  # Start at the tip of the player triangle
        
        # Create the shot - this will automatically add it to the sprite groups
        # because Shot.containers is defined in main.py
        shot = Shot(shot_pos.x, shot_pos.y, self.rotation)
        
        # Print debug info
        print(f"Player shot at position {shot_pos} with rotation {self.rotation}")
        return shot
        
    def collide(self, other):
        # Simple circle collision detection
        distance = (self.position - other.position).length()
        return distance < (self.radius + other.radius)