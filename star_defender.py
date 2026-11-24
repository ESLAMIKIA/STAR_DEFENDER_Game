import random
import sys
import pygame

# -------------------- SETTINGS --------------------
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 6
BULLET_SPEED = 9
ENEMY_BASE_SPEED = 2

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("STAR DEFENDER")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 26, bold=True)
BIG_FONT = pygame.font.SysFont("arial", 58, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 18)

# Colors
BLACK = (7, 10, 25)
WHITE = (240, 245, 255)
CYAN = (70, 220, 255)
PINK = (255, 90, 150)
YELLOW = (255, 220, 90)
RED = (255, 75, 75)
GREEN = (90, 235, 150)

# Background stars
stars = [
    [random.randrange(WIDTH), random.randrange(HEIGHT), random.choice((1, 1, 2, 3))]
    for _ in range(90)
]


def draw_text(surface, text, font, color, center):
    image = font.render(text, True, color)
    surface.blit(image, image.get_rect(center=center))


class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 22, HEIGHT - 75, 44, 38)
        self.health = 3
        self.cooldown = 0
        self.invulnerable = 0

    def update(self, keys):
        dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (
            keys[pygame.K_LEFT] or keys[pygame.K_a]
        )
        dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (
            keys[pygame.K_UP] or keys[pygame.K_w]
        )
        self.rect.x += dx * PLAYER_SPEED
        self.rect.y += dy * PLAYER_SPEED
        self.rect.clamp_ip(screen.get_rect())

        if self.cooldown > 0:
            self.cooldown -= 1
        if self.invulnerable > 0:
            self.invulnerable -= 1

    def shoot(self):
        if self.cooldown == 0:
            self.cooldown = 13
            return Bullet(self.rect.centerx, self.rect.top)
        return None

    def draw(self, surface):
        if self.invulnerable and self.invulnerable // 5 % 2 == 0:
            return
        x, y = self.rect.center
        points = [(x, y - 25), (x - 23, y + 17), (x, y + 8), (x + 23, y + 17)]
        pygame.draw.polygon(surface, CYAN, points)
        pygame.draw.polygon(surface, WHITE, points, 2)
        pygame.draw.polygon(surface, YELLOW, [(x - 7, y + 15), (x, y + 29), (x + 7, y + 15)])


class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 3, y - 12, 6, 16)

    def update(self):
        self.rect.y -= BULLET_SPEED

    def draw(self, surface):
        pygame.draw.rect(surface, YELLOW, self.rect, border_radius=3)
        pygame.draw.circle(surface, WHITE, self.rect.center, 3)


class Enemy:
    def __init__(self, level):
        size = random.randint(28, 43)
        self.rect = pygame.Rect(random.randint(8, WIDTH - size - 8), -size, size, size)
        self.speed = ENEMY_BASE_SPEED + level * 0.22 + random.random() * 1.5
        self.color = random.choice((PINK, RED, (180, 110, 255)))

    def update(self):
        self.rect.y += self.speed

    def draw(self, surface):
        pygame.draw.polygon(
            surface,
            self.color,
            [
                (self.rect.centerx, self.rect.bottom),
                (self.rect.left, self.rect.top),
                (self.rect.right, self.rect.top),
            ],
        )
        pygame.draw.polygon(
            surface, WHITE,
            [
                (self.rect.centerx, self.rect.bottom),
                (self.rect.left, self.rect.top),
                (self.rect.right, self.rect.top),
            ],
            2,
        )
        pygame.draw.circle(surface, WHITE, (self.rect.centerx, self.rect.centery), 4)


def draw_background():
    screen.fill(BLACK)
    for star in stars:
        star[1] += star[2]
        if star[1] > HEIGHT:
            star[0] = random.randrange(WIDTH)
            star[1] = 0
        pygame.draw.circle(screen, (100, 125, 175), (star[0], star[1]), star[2] // 2 + 1)


def reset_game():
    return Player(), [], [], 0, 0, 0


player, bullets, enemies, score, spawn_timer, level = reset_game()
game_state = "menu"

# -------------------- MAIN LOOP --------------------
while True:
    clock.tick(FPS)
    shoot_requested = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_SPACE:
                if game_state == "menu":
                    game_state = "playing"
                elif game_state == "gameover":
                    player, bullets, enemies, score, spawn_timer, level = reset_game()
                    game_state = "playing"
                elif game_state == "playing":
                    shoot_requested = True

    draw_background()

    if game_state == "menu":
        draw_text(screen, "STAR DEFENDER", BIG_FONT, CYAN, (WIDTH // 2, 205))
        draw_text(screen, "Protect your ship. Survive the enemy attack.", FONT, WHITE, (WIDTH // 2, 280))
        draw_text(screen, "WASD / ARROW KEYS  -  MOVE", SMALL_FONT, (180, 195, 220), (WIDTH // 2, 355))
        draw_text(screen, "SPACE  -  SHOOT", SMALL_FONT, (180, 195, 220), (WIDTH // 2, 385))
        draw_text(screen, "PRESS SPACE TO START", FONT, YELLOW, (WIDTH // 2, 465))

    elif game_state == "playing":
        keys = pygame.key.get_pressed()
        player.update(keys)

        if keys[pygame.K_SPACE]:
            shoot_requested = True
        if shoot_requested:
            bullet = player.shoot()
            if bullet:
                bullets.append(bullet)

        level = score // 100
        spawn_timer += 1
        spawn_delay = max(18, 55 - level * 3)
        if spawn_timer >= spawn_delay:
            enemies.append(Enemy(level))
            spawn_timer = 0

        for bullet in bullets[:]:
            bullet.update()
            if bullet.rect.bottom < 0:
                bullets.remove(bullet)

        for enemy in enemies[:]:
            enemy.update()
            if enemy.rect.top > HEIGHT:
                enemies.remove(enemy)
                player.health -= 1
                player.invulnerable = 45
            elif enemy.rect.colliderect(player.rect) and player.invulnerable == 0:
                enemies.remove(enemy)
                player.health -= 1
                player.invulnerable = 60

        for bullet in bullets[:]:
            hit_enemy = next((enemy for enemy in enemies if bullet.rect.colliderect(enemy.rect)), None)
            if hit_enemy:
                bullets.remove(bullet)
                enemies.remove(hit_enemy)
                score += 10

        for bullet in bullets:
            bullet.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        player.draw(screen)

        # HUD
        pygame.draw.rect(screen, (25, 35, 65), (18, 16, 210, 42), border_radius=10)
        draw_text(screen, f"SCORE  {score}", FONT, WHITE, (123, 37))
        pygame.draw.rect(screen, (25, 35, 65), (WIDTH - 190, 16, 172, 42), border_radius=10)
        draw_text(screen, f"LIVES  {max(0, player.health)}", FONT, GREEN if player.health > 1 else RED, (WIDTH - 104, 37))

        if player.health <= 0:
            game_state = "gameover"

    elif game_state == "gameover":
        draw_text(screen, "GAME OVER", BIG_FONT, PINK, (WIDTH // 2, 220))
        draw_text(screen, f"FINAL SCORE: {score}", FONT, WHITE, (WIDTH // 2, 305))
        draw_text(screen, "PRESS SPACE TO PLAY AGAIN", FONT, YELLOW, (WIDTH // 2, 390))
        draw_text(screen, "ESC - QUIT", SMALL_FONT, (180, 195, 220), (WIDTH // 2, 435))

    pygame.display.flip()
