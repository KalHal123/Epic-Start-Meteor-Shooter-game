import pygame
import random
import sys
import time
from os.path import join
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Epic Shooter Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Game settings
FPS = 60
PLAYER_SPEED = 5
BULLET_SPEED = 10
ENEMY_SPEED_BASE = 2
ENEMY_SPAWN_RATE = 30  # Frames until a new enemy spawns
STAR_COUNT = 20

# Helper function to find the correct path for assets in both script and executable modes
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Load images
player_surf = pygame.image.load(resource_path(join('images', 'player.png'))).convert_alpha()
bullet_surf = pygame.image.load(resource_path(join('images', 'laser.png'))).convert_alpha()
meteor_surf = pygame.image.load(resource_path(join('images', 'meteor.png'))).convert_alpha()
star_surf = pygame.image.load(resource_path(join('images', 'star.png'))).convert_alpha()

# Load SFX
meteor_explosion = pygame.mixer.Sound(resource_path(join("sounds", "explosion (9).wav")))
meteor_explosion.set_volume(0.6)
player_hit = pygame.mixer.Sound(resource_path(join("sounds", "hitHurt.wav")))
player_shoot = pygame.mixer.Sound(resource_path(join("sounds", "laserShoot.wav")))
player_move = pygame.mixer.Sound(resource_path(join("sounds", "tone.wav")))
player_move.set_volume(0.14)
player_death = pygame.mixer.Sound(resource_path(join("sounds", "synth.wav")))

# Game clock
clock = pygame.time.Clock()

# Sprites and groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
stars = pygame.sprite.Group()

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = player_surf
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.speed = PLAYER_SPEED
        self.health = 3
        self.score = 0
        self.can_shoot = True
        self.shoot_cooldown = 250
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_ESCAPE]:
            pygame.quit

        # Shooting bullets with cooldown
        if keys[pygame.K_SPACE] and self.can_shoot:
            self.shoot()
            player_shoot.play()
            self.last_shot = pygame.time.get_ticks()
        if pygame.time.get_ticks() - self.last_shot >= self.shoot_cooldown:
            self.can_shoot = True

    def shoot(self):
        bullet = Bullet(bullet_surf, self.rect.midtop, bullets)
        bullets.add(bullet)
        all_sprites.add(bullet)
        self.can_shoot = False

    def take_damage(self):
        self.health -= 1
        player_hit.play()

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, *groups):
        super().__init__(*groups)
        self.image = surf
        self.rect = self.image.get_rect(midbottom=pos)
        self.speed = BULLET_SPEED

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

# Enemy (Meteor) class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = meteor_surf
        self.rect = self.image.get_rect(center=(random.randint(0, WIDTH), 0))
        self.speed = ENEMY_SPEED_BASE

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# Star class
class Star(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = star_surf
        self.rect = self.image.get_rect(
            center=(random.randint(0, WIDTH), random.randint(0, HEIGHT))
        )

# Game initialization
player = Player(all_sprites)
all_sprites.add(player)

# Spawn initial stars
for _ in range(STAR_COUNT):
    star = Star(stars)
    stars.add(star)
    all_sprites.add(star)

# Main game loop
def main():
    frame_count = 0
    running = True

    while running:
        screen.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Spawn enemies based on the frame count
        if frame_count % ENEMY_SPAWN_RATE == 0:
            enemy = Enemy(enemies)
            enemy.speed = ENEMY_SPEED_BASE + player.score * 0.1  # Increase speed with score
            enemies.add(enemy)
            all_sprites.add(enemy)

        # Update all sprites
        all_sprites.update()

        # Bullet and enemy collision
        for bullet in bullets:
            hits = pygame.sprite.spritecollide(bullet, enemies, dokill=True)
            if hits:
                bullet.kill()
                meteor_explosion.play()
                player.score += 1

        # Player and enemy collision
        if pygame.sprite.spritecollide(player, enemies, dokill=True):
            player.take_damage()
            if player.health <= 0:
                player_death.play()
                time.sleep(0.6)
                running = False  # End game if health reaches 0

        # Draw stars in the background
        stars.draw(screen)

        # Draw sprites (player, bullets, enemies)
        all_sprites.draw(screen)

        # Draw health meter
        font = pygame.font.Font(None, 36)
        health_text = font.render(f"Health: {player.health}", True, WHITE)
        screen.blit(health_text, (WIDTH - 150, 10))

        # Draw score
        score_text = font.render(f"Score: {player.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

        # Increment frame count
        frame_count += 1

if __name__ == "__main__":
    main()
