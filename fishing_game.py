import pygame
import random
import math

pygame.init()

# Constants for the screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
LIGHT_BLUE = (173, 216, 230)  # Light blue for the water surface
DARK_BLUE = (0, 0, 128)  # Dark blue for the wave

# Wave height relative to the bottom of the screen
WAVE_HEIGHT = 500

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fishing Game")

clock = pygame.time.Clock()



class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_x, speed_y, emission_side):
        super().__init__()
        self.image = pygame.Surface((3, 3))  # Particle appearance (3x3 square)
        self.image.fill((0, 0, 128))  # Blue color for the particle
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_x = speed_x  # Horizontal speed
        self.speed_y = speed_y  # Vertical speed
        self.emission_side = emission_side  # Emission side ('left' or 'right')
        self.gravity = 0.5  # Gravitational acceleration (increase for stronger gravity)

    def update(self):
        # Apply gravity to the vertical speed
        self.speed_y += self.gravity

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Remove the particle if it goes off-screen
        if self.rect.bottom < 0 or self.rect.left > SCREEN_WIDTH or self.rect.right < 0:
            self.kill()




class Boat(pygame.sprite.Sprite):
    def __init__(self, waves, all_sprites, particles_group):
        super().__init__()
        self.image = pygame.image.load('boat.png').convert_alpha()
        self.image_flipped = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(centerx=SCREEN_WIDTH // 2, bottom=120)
        self.speed = 5
        self.vertical_offset = 0
        self.waves = waves
        self.direction = 'right'  # Initialize boat direction
        self.all_sprites = all_sprites
        self.particles_group = particles_group  # Group for particles
        self.particle_cooldown = 0  # Cooldown to control particle emission

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.direction = 'left'
        elif keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.direction = 'right'

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        # Update wave amplitude based on boat position
        wave_amplitude = 0
        for wave in self.waves:
            wave_amplitude += wave.amplitude * math.sin(self.rect.centerx / wave.length * 4 * math.pi + wave.offset / 10)

        self.vertical_offset = wave_amplitude
        self.rect.bottom = SCREEN_HEIGHT - WAVE_HEIGHT + self.vertical_offset

        # Emit particles only when the boat is moving
        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
            if self.particle_cooldown <= 0:
                self.particle_cooldown = random.randint(20, 40)  # Adjust cooldown duration

                # Determine emission position and particle speed based on boat direction
                if self.direction == 'left':
                    emission_x = self.rect.left - 5  # Emit from the left side of the boat, adjusted closer by 5 pixels
                    particle_speed_x = -2  # Particle moves to the left
                    emission_side = 'left'  # Emission side is 'left'
                elif self.direction == 'right':
                    emission_x = self.rect.right + 5  # Emit from the right side of the boat, adjusted closer by 5 pixels
                    particle_speed_x = 2  # Particle moves to the right
                    emission_side = 'right'  # Emission side is 'right'

                # Create and add the particle to sprite groups
                particle = Particle(emission_x, self.rect.centery, particle_speed_x, random.randint(-1, -1), emission_side)
                self.all_sprites.add(particle)
                self.particles_group.add(particle)

        # Decrement particle emission cooldown only when the boat is moving
        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
            self.particle_cooldown -= 1

        # Update boat image based on direction
        if self.direction == 'left':
            self.image = self.image_flipped
        elif self.direction == 'right':
            self.image = pygame.image.load('boat.png').convert_alpha()


















class Wave(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.amplitude = 10  # Adjust the amplitude of the wave
        self.length = SCREEN_WIDTH
        self.speed = 1
        self.color = DARK_BLUE  # Use dark blue color for the wave
        self.water_level = SCREEN_HEIGHT - WAVE_HEIGHT  # Lower water level

        self.offset = 0

    def update(self):
        self.offset += self.speed

    def draw(self, screen):
        # Draw the wave pattern directly onto the screen above the water surface
        for x in range(self.length):
            y = self.amplitude * math.sin(x / self.length * 4 * math.pi + self.offset / 10)
            pygame.draw.line(screen, self.color, (x, self.water_level + y), (x, SCREEN_HEIGHT), 2)



class FishingLine(pygame.sprite.Sprite):
    def __init__(self, boat):
        super().__init__()
        self.image = pygame.Surface((2, 0))  # Fishing line appearance
        self.image.fill((85, 85, 85))  # Silver color for the fishing line
        self.rect = self.image.get_rect()
        self.boat = boat
        self.casting = False

        # Load hitbox image
        self.hitbox_image = pygame.image.load('hitbox.png').convert_alpha()
        self.hitbox_rect = self.hitbox_image.get_rect()

        self.update_position()

    def update_position(self):
        # Position the fishing line below the boat
        self.rect.centerx = self.boat.rect.centerx
        self.rect.top = self.boat.rect.bottom  # Place fishing line below the boat

        # Position hitbox at the bottom center of the fishing line
        self.hitbox_rect.centerx = self.rect.centerx
        self.hitbox_rect.top = self.rect.bottom

    def cast_line(self):
        self.casting = True

    def reel_line(self):
        self.casting = False

    def extend_line(self):
        if self.casting and self.rect.height < 450:  # Limit line extension (adjust height as needed)
            self.rect.height += 5
        self.update_position()

    def retract_line(self):
        if self.rect.height > 1:
            self.rect.height -= 5
        self.update_position()

    def draw(self, screen):
        # Draw fishing line in front of water surface
        pygame.draw.rect(screen, (192, 192, 192), self.rect)

    def draw_hitbox(self, screen):
        # Draw hitbox image for fishing line
        screen.blit(self.hitbox_image, self.hitbox_rect)





class Fish(pygame.sprite.Sprite):
    def __init__(self, water_level):
        super().__init__()
        self.image_right = pygame.image.load('fish.png').convert_alpha()
        self.image_left = pygame.image.load('fishR.png').convert_alpha()
        self.image = self.image_right  # Initial image direction
        self.rect = self.image.get_rect()
        self.water_level = water_level
        self.reset()

    def reset(self):
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(self.water_level, SCREEN_HEIGHT - self.rect.height)
        self.speed_x = random.randint(-3, 3)
        self.speed_y = random.randint(-3, 3)

    def update(self):
        # Change fish image based on movement direction
        if self.speed_x > 0:
            self.image = self.image_right
        elif self.speed_x < 0:
            self.image = self.image_left

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Bounce off walls and stay below water level
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speed_x = -self.speed_x
        if self.rect.top < self.water_level or self.rect.bottom > SCREEN_HEIGHT:
            self.speed_y = -self.speed_y
            self.rect.y = min(max(self.rect.y, self.water_level), SCREEN_HEIGHT - self.rect.height)

    def draw_hitbox(self, screen):
        pygame.draw.rect(screen, RED, self.rect, 1)  # Draw hitbox outline



class EvilFish(Fish):
    def __init__(self, water_level):
        super().__init__(water_level)
        self.image_right = pygame.image.load('fishE.png').convert_alpha()
        self.image_left = pygame.transform.flip(self.image_right, True, False)  # Flip the image for left direction
        self.image = self.image_right  # Initial image direction
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Change direction based on speed_x
        if self.speed_x > 0:
            self.image = self.image_right  # Face right
        elif self.speed_x < 0:
            self.image = self.image_left  # Face left

        # Bounce off walls and stay below water level
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speed_x = -self.speed_x
        if self.rect.top < self.water_level or self.rect.bottom > SCREEN_HEIGHT:
            self.speed_y = -self.speed_y
            self.rect.y = min(max(self.rect.y, self.water_level), SCREEN_HEIGHT - self.rect.height)


def intro_screen():
    intro_running = True
    background_image = pygame.image.load('intro_background.png').convert()
    
    while intro_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if mouse click is on the start button
                if start_button_rect.collidepoint(event.pos):
                    intro_running = False
        
        # Display background image
        screen.blit(background_image, (0, 0))
        
        # Draw title
        font_title = pygame.font.Font(None, 72)
        title_text = font_title.render(" ", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(title_text, title_rect)
        
        # Draw start button
        font_button = pygame.font.Font(None, 80)
        start_text = font_button.render("Start", True, BLACK)
        start_button_rect = start_text.get_rect(center=(SCREEN_WIDTH // 1.2, SCREEN_HEIGHT // 1.1))
        pygame.draw.rect(screen, WHITE, start_button_rect, 2)  # Draw button outline
        screen.blit(start_text, start_button_rect)
        
        pygame.display.flip()
        clock.tick(30)



def main_game():
    intro_screen()
    # Create waves
    waves = pygame.sprite.Group(Wave())

    # Create boat instance and fishing line
    all_sprites = pygame.sprite.Group()
    particles_group = pygame.sprite.Group()  # Group for particles

    boat = Boat(waves, all_sprites, particles_group)
    fishing_line = FishingLine(boat)
    all_sprites.add(boat, fishing_line)

    # Create regular fish and evil fish
    fish_sprites = pygame.sprite.Group()
    evil_fish_sprites = pygame.sprite.Group()
    for _ in range(9):
        fish = Fish(SCREEN_HEIGHT - WAVE_HEIGHT)  # Adjust water level for fish
        fish_sprites.add(fish)
        all_sprites.add(fish)

    caught_fish = 0
    caught_evil_fish = False

    start_time = pygame.time.get_ticks()
    last_evil_fish_spawn_time = start_time
    evil_fish_spawn_interval = 20000  # Initial spawn interval in milliseconds (20 seconds)
    evil_fish_count = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not fishing_line.casting:
                        fishing_line.cast_line()
                    else:
                        fishing_line.reel_line()

        # Update boat's position and bobbing effect
        boat.update()

        fishing_line.update_position()
        fishing_line.extend_line()
        if not fishing_line.casting:
            fishing_line.retract_line()

        hitbox_position = fishing_line.hitbox_rect.center

        # Check for collisions with regular fish
        for fish in fish_sprites:
            if fish.rect.collidepoint(hitbox_position):
                fish.reset()
                caught_fish += 1

        # Check for collisions with evil fish
        for evil_fish in evil_fish_sprites:
            if evil_fish.rect.collidepoint(hitbox_position):
                caught_evil_fish = True

        # Create particles moving to the right
        if boat.direction == 'left':
            particle_right = Particle(boat.rect.right, boat.rect.centery, 2, random.randint(-5, -1), 'right')
            particles_group.add(particle_right)

# Create particles moving to the left
        if boat.direction == 'right':
            particle_left = Particle(boat.rect.left, boat.rect.centery, -2, random.randint(-5, -1), 'left')
            particles_group.add(particle_left)


        # Update all sprites including particles
        all_sprites.update()
        particles_group.update()

        screen.fill(LIGHT_BLUE)  # Fill screen with light blue for water surface

        # Draw waves and other sprites except particles
        for wave in waves:
            wave.update()
            wave.draw(screen)

        all_sprites.draw(screen)  # Draw boat, fishing line, fish, evil fish
        particles_group.draw(screen)  # Draw particles on the screen

        # Draw fishing line and its hitbox on top of everything
        fishing_line.draw(screen)
        fishing_line.draw_hitbox(screen)

        # Display caught fish count
        font = pygame.font.Font(None, 36)
        text = font.render(f"Caught: {caught_fish}", True, (0, 0, 0))  # Use black for text
        screen.blit(text, (20, 20))

        # Calculate elapsed time
        elapsed_time = pygame.time.get_ticks() - start_time
        elapsed_seconds = elapsed_time // 1000
        elapsed_milliseconds = (elapsed_time % 1000) // 10
        timer_text = font.render(f"Time: {elapsed_seconds}.{elapsed_milliseconds:02d}", True, (0, 0, 0))  # Use black for text
        timer_rect = timer_text.get_rect(topright=(SCREEN_WIDTH - 20, 20))
        screen.blit(timer_text, timer_rect)

        # Calculate spawn interval based on elapsed time
        current_time = pygame.time.get_ticks()
        if current_time >= last_evil_fish_spawn_time + evil_fish_spawn_interval:
            evil_fish_count += 1
            last_evil_fish_spawn_time = current_time

            # Decrease spawn interval over time to increase spawn rate
            evil_fish_spawn_interval = max(5000, evil_fish_spawn_interval - 1000)  # Cap minimum interval at 5 seconds

            new_evil_fish = EvilFish(SCREEN_HEIGHT - WAVE_HEIGHT)  # Adjust water level for evil fish
            evil_fish_sprites.add(new_evil_fish)
            all_sprites.add(new_evil_fish)

        pygame.display.flip()
        clock.tick(30)

        # End the game if an evil fish is caught
        if caught_evil_fish:
            running = False
            game_over_screen(caught_fish, elapsed_seconds, elapsed_milliseconds)

    pygame.quit()






def game_over_screen(caught_fish, elapsed_seconds, elapsed_milliseconds):
    screen.fill(BLACK)
    font = pygame.font.Font(None, 72)
    game_over_text = font.render("Game Over", True, RED)
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))

    score_text = font.render(f"Score: {caught_fish}", True, WHITE)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

    time_text = font.render(f"Time: {elapsed_seconds}.{elapsed_milliseconds:02d}", True, WHITE)
    time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))

    screen.blit(game_over_text, game_over_rect)
    screen.blit(score_text, score_rect)
    screen.blit(time_text, time_rect)

    pygame.display.flip()
    pygame.time.wait(3000)  # Display "Game Over" for 2 seconds before quitting



# Run the game
if __name__ == "__main__":
    main_game()

