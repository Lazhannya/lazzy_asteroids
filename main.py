import pygame
from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot

updatable = pygame.sprite.Group()
drawable = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
shots = pygame.sprite.Group()

Player.containers = (updatable, drawable)
Asteroid.containers = (updatable, drawable, asteroids)
AsteroidField.containers = (updatable, )
Shot.containers = (updatable, drawable, shots)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    asteroid_field = AsteroidField()  # Create a new AsteroidField object
    dt = 0  # Assuming a frame rate of ~60 FPS
    print("Starting Asteroids!")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")

    # Main game loop
    running = True
    frame_count = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Print debug info every 60 frames
        frame_count += 1
        if frame_count % 60 == 0:
            print(f"Number of objects: updatable={len(updatable)}, drawable={len(drawable)}, asteroids={len(asteroids)}")
            
        screen.fill((0, 0, 0))  # Fill the screen with black
        
        # Update all objects
        for obj in updatable:
            obj.update(dt)  # Update things
        
        # Check for player collisions with asteroids
        for asteroid in asteroids:
            if player.collide(asteroid):
                print("Game Over!")
                running = False
                
        # Check for shot collisions with asteroids
        for shot in shots:
            for asteroid in list(asteroids):  # Create a copy of the list to avoid modification during iteration
                # Simple circle collision detection
                distance = (shot.position - asteroid.position).length()
                if distance < (shot.radius + asteroid.radius):
                    shot.kill()
                    asteroid.split()  # Call the split method instead of just killing the asteroid
                    print("Shot hit asteroid!")

        # Draw all objects
        for obj in drawable:
            obj.draw(screen)  # Draw things
            
        pygame.display.flip()  # Update the display
        clock.tick(60)  # Cap the frame rate at 60 FPS
        dt = clock.get_time() / 1000.0  # Delta time in seconds
        

    pygame.quit()



if __name__ == "__main__":
    main()
