import pygame
from constants import *
from circleshape import CircleShape


class Player(CircleShape):
    def __init__(self, x, y, laser_sound=None, death_sound=None):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shot_cooldown = 0  # Cooldown timer for shooting
        self.laser_sound = laser_sound  # Sound effect for shooting
        self.death_sound = death_sound  # Sound effect for death
        self.lives = 3  # Player starts with 3 lives
        self.invulnerable = 0  # Invulnerability timer after being hit

    def draw(self, screen):
        # Make player blink when invulnerable
        if self.invulnerable <= 0 or (self.invulnerable * 10) % 2 < 1:
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
        
        # Update invulnerability timer
        if self.invulnerable > 0:
            self.invulnerable -= dt
            
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
        
        # Play laser sound effect if available
        if self.laser_sound:
            self.laser_sound.play()
            
        # Print debug info
        print(f"Player shot at position {shot_pos} with rotation {self.rotation}")
        return shot
        
    def collide(self, other):
        # Don't collide when invulnerable
        if self.invulnerable > 0:
            return False
            
        # Simple circle collision detection
        distance = (self.position - other.position).length()
        return distance < (self.radius + other.radius)
        
    def lose_life(self):
        """Player loses a life and becomes invulnerable for a short time"""
        self.lives -= 1
        self.invulnerable = 3.0  # 3 seconds of invulnerability
        
        # Play death sound
        if self.death_sound:
            self.death_sound.play()
            
        # Print debug info
        print(f"Player lost a life! Lives remaining: {self.lives}")
        return self.lives <= 0  # Return True if game over