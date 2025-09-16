import pygame
import random
from constants import *
from circleshape import CircleShape

class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.velocity = pygame.Vector2(0, 0)

    def draw(self, screen):
        # Print debug info occasionally
        if hasattr(self, 'draw_counter'):
            self.draw_counter += 1
            if self.draw_counter % 60 == 0:
                print(f"Drawing asteroid at position: {self.position}")
        else:
            self.draw_counter = 0
            
        # Draw the asteroid - make it more visible with a filled circle
        pygame.draw.circle(screen, ("brown"), (int(self.position.x), int(self.position.y)), self.radius)

    def update(self, dt):
        self.position += self.velocity * dt
        # Screen wrapping
        if self.position.x < 0:
            self.position.x = SCREEN_WIDTH
        elif self.position.x > SCREEN_WIDTH:
            self.position.x = 0
        if self.position.y < 0:
            self.position.y = SCREEN_HEIGHT
        elif self.position.y > SCREEN_HEIGHT:
            self.position.y = 0
    
    def split(self):
        # Only split if the asteroid is larger than the minimum size
        if self.radius > ASTEROID_MIN_RADIUS:
            # Calculate new radius for child asteroids
            new_radius = self.radius // 2  # Integer division to ensure smaller radius
            
            # Create random angle for splitting
            angle = random.uniform(20, 50)
            
            # Calculate velocities for the two new asteroids
            velocity1 = self.velocity.rotate(angle) * 1.2
            velocity2 = self.velocity.rotate(-angle) * 1.2
            
            # Create two new smaller asteroids
            asteroid1 = Asteroid(self.position.x, self.position.y, new_radius)
            asteroid1.velocity = velocity1
            
            asteroid2 = Asteroid(self.position.x, self.position.y, new_radius)
            asteroid2.velocity = velocity2
            
            print(f"Split asteroid at position {self.position} into two with radius {new_radius}")
            
        # Remove the original asteroid
        self.kill()