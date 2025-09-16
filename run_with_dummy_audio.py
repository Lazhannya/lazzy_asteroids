#!/usr/bin/env python3
import os
import pygame
from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot

# Try to set audio driver to null/dummy before pygame initialization
os.environ['SDL_AUDIODRIVER'] = 'pulse'

# The rest of your main.py content follows
updatable = pygame.sprite.Group()
drawable = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
shots = pygame.sprite.Group()

Player.containers = (updatable, drawable)
Asteroid.containers = (updatable, drawable, asteroids)
AsteroidField.containers = (updatable, )
Shot.containers = (updatable, drawable, shots)


def init_game():
    """Initialize the game and return necessary objects"""
    pygame.init()
    
    # Try to initialize the sound mixer, but continue if it fails
    laser_sound = None
    rock_break_sound = None
    death_sound = None
    lose_sound = None
    try:
        pygame.mixer.init(channels=4)
        
        # Reserve channel 1 for asteroid breaking sounds to prevent overlapping
        rock_break_channel = pygame.mixer.Channel(1)
        rock_break_channel.set_volume(0.4)  # Set volume to 40% for this channel
        
        # Reserve channel 2 for player death sound
        death_channel = pygame.mixer.Channel(2)
        death_channel.set_volume(0.4)  # Set volume to 40% for this channel
        
        # Reserve channel 3 for game over sound
        lose_channel = pygame.mixer.Channel(3)
        lose_channel.set_volume(0.4)  # Set volume to 40% for this channel
        
        laser_sound = pygame.mixer.Sound("sounds/laser.ogg")
        laser_sound.set_volume(0.4)  # Set laser sound volume to 40% as well
        
        rock_break_sound = pygame.mixer.Sound("sounds/rock_break.ogg")
        # Set the volume of rock_break sound to 40%
        rock_break_sound.set_volume(0.4)
        
        death_sound = pygame.mixer.Sound("sounds/heavy_ded.mp3")
        death_sound.set_volume(0.4)  # Set death sound volume to 40%
        
        lose_sound = pygame.mixer.Sound("sounds/lose.ogg")
        lose_sound.set_volume(0.4)  # Set game over sound volume to 40%
        print("Sound initialized successfully with dummy driver!")
    except pygame.error as e:
        print(f"Sound could not be initialized: {e}")
        print("Game will continue without sound.")
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, laser_sound, death_sound)  # Pass the sounds to player
    asteroid_field = AsteroidField()  # Create a new AsteroidField object
    dt = 0  # Assuming a frame rate of ~60 FPS
    font = pygame.font.Font(None, 36)  # Font for displaying lives
    
    print("Game initialized!")
    return screen, clock, player, asteroid_field, laser_sound, rock_break_sound, death_sound, rock_break_channel, lose_sound, lose_channel


def show_game_over_screen(screen, clock, font, lose_sound=None, lose_channel=None):
    """Display the game over screen with restart option"""
    # Play the game over sound if available
    if lose_sound and lose_channel:
        lose_channel.play(lose_sound)
    
    big_font = pygame.font.Font(None, 72)
    game_over_text = big_font.render("GAME OVER", True, (255, 0, 0))
    restart_text = font.render("Press R to Restart or Q to Quit", True, (255, 255, 255))
    
    screen.fill((0, 0, 0))  # Fill screen with black
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 
                                SCREEN_HEIGHT // 3))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                              SCREEN_HEIGHT // 2))
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Quit game
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True  # Restart game
                if event.key == pygame.K_q:
                    return False  # Quit game
                    
        clock.tick(60)
    
    return False


def game_loop(screen, clock, player, asteroid_field, laser_sound, rock_break_sound, death_sound, rock_break_channel):
    """Main game loop"""
    font = pygame.font.Font(None, 36)  # Font for displaying lives
    
    print("Starting Asteroids!")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    
    # Clear sprite groups to ensure a clean start
    global updatable, drawable, asteroids, shots
    updatable.empty()
    drawable.empty()
    asteroids.empty()
    shots.empty()
    
    # Re-add the player and asteroid field
    updatable.add(player)
    drawable.add(player)
    updatable.add(asteroid_field)
    
    # Main game loop
    running = True
    frame_count = 0
    dt = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Signal to exit the entire game
        
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
                # Player loses a life when colliding with an asteroid
                game_over = player.lose_life()
                if game_over:
                    print("Game Over! No lives remaining.")
                    running = False
                    return "game_over"  # Signal game over to main function
                else:
                    # Destroy the asteroid that hit the player
                    asteroid.split()
                
        # Check for shot collisions with asteroids
        for shot in shots:
            for asteroid in list(asteroids):  # Create a copy of the list to avoid modification during iteration
                # Simple circle collision detection
                distance = (shot.position - asteroid.position).length()
                if distance < (shot.radius + asteroid.radius):
                    shot.kill()
                    asteroid.split()  # Call the split method instead of just killing the asteroid
                    # Play rock breaking sound effect if available
                    if rock_break_sound:
                        # Use the dedicated channel for rock break sounds to prevent overlapping
                        rock_break_channel.play(rock_break_sound)
                    print("Shot hit asteroid!")

        # Draw all objects
        for obj in drawable:
            obj.draw(screen)  # Draw things
            
        # Draw lives counter
        lives_text = font.render(f"Lives: {player.lives}", True, (255, 255, 255))
        screen.blit(lives_text, (20, 20))
        
        pygame.display.flip()  # Update the display
        clock.tick(60)  # Cap the frame rate at 60 FPS
        dt = clock.get_time() / 1000.0  # Delta time in seconds
    
    return True  # Signal normal exit from game loop


def main():
    """Main game function handling game over and restart"""
    # Game state variables
    running = True
    
    # Initialize the game for the first time
    screen, clock, player, asteroid_field, laser_sound, rock_break_sound, death_sound, rock_break_channel, lose_sound, lose_channel = init_game()
    
    while running:
        # Run the main game loop
        result = game_loop(screen, clock, player, asteroid_field, laser_sound, rock_break_sound, death_sound, rock_break_channel)
        
        if result == "game_over":
            # Show game over screen and check for restart
            if show_game_over_screen(screen, clock, pygame.font.Font(None, 36), lose_sound, lose_channel):
                # User wants to restart, reinitialize the player and asteroid field
                player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, laser_sound, death_sound)
                asteroid_field = AsteroidField()
            else:
                # User wants to quit
                running = False
        else:
            # Normal exit or window close
            running = False
    
    pygame.quit()


if __name__ == "__main__":
    main()