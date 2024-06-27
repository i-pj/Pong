import sys
import random
import pygame
from menu import create_menu

pygame.init()

# Global variables
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
BALL_RADIUS = 10
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 80
HALF_PADDLE_WIDTH, HALF_PADDLE_HEIGHT = PADDLE_WIDTH // 2, PADDLE_HEIGHT // 2

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((BALL_RADIUS * 2, BALL_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, WHITE, (BALL_RADIUS, BALL_RADIUS), BALL_RADIUS)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed_x = random.choice([-3, -2, 2, 3])
        self.speed_y = random.choice([-3, -2, 2, 3])

    def reset(self):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed_x = random.choice([-3, -2, 2, 3])
        self.speed_y = random.choice([-3, -2, 2, 3])

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.speed_y *= -1

class Paddle(pygame.sprite.Sprite):
    def __init__(self, side):
        super().__init__()
        self.image = pygame.Surface((PADDLE_WIDTH, PADDLE_HEIGHT))
        self.image.fill(WHITE)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.side = side
        if self.side == "left":
            self.rect.x = 50
        else:
            self.rect.x = SCREEN_WIDTH - 50 - PADDLE_WIDTH
        self.rect.centery = SCREEN_HEIGHT // 2
        self.speed_y = 0

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

def handle_input(paddle_left, paddle_right):
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        paddle_left.speed_y = -5
    elif keys[pygame.K_s]:
        paddle_left.speed_y = 5
    else:
        paddle_left.speed_y = 0

    if keys[pygame.K_UP]:
        paddle_right.speed_y = -5
    elif keys[pygame.K_DOWN]:
        paddle_right.speed_y = 5
    else:
        paddle_right.speed_y = 0

def main():
    pygame.display.set_caption("Pong")
    clock = pygame.time.Clock()
    game_mode = create_menu(screen)
    if game_mode == "vs_computer":
        pass
    if game_mode == "vs_player":
        all_sprites = pygame.sprite.Group()
        paddle_left = Paddle("left")
        paddle_right = Paddle("right")
        all_sprites.add(paddle_left, paddle_right)

        ball = Ball()
        all_sprites.add(ball)

        score_left = 0
        score_right = 0

        font = pygame.font.Font(None, 72)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            handle_input(paddle_left, paddle_right)
            all_sprites.update()

            screen.fill(BLACK)

            text_left = font.render(str(score_left), True, WHITE)
            screen.blit(text_left, (SCREEN_WIDTH // 4, 10))

            text_right = font.render(str(score_right), True, WHITE)
            screen.blit(text_right, (SCREEN_WIDTH * 3 // 4, 10))

            all_sprites.draw(screen)
            pygame.display.flip()

            if ball.rect.x < -BALL_RADIUS:
                score_right += 1
                ball.reset()
            elif ball.rect.x > SCREEN_WIDTH + BALL_RADIUS:
                score_left += 1
                ball.reset()

            # Collision with paddles
            if ball.rect.colliderect(paddle_left.rect):
                if ball.rect.centery > paddle_left.rect.top and ball.rect.centery < paddle_left.rect.bottom:
                    ball.speed_x *= -1.1
                    ball.speed_y = (ball.rect.centery - paddle_left.rect.centery) / HALF_PADDLE_HEIGHT * 5
                    ball.rect.x += ball.speed_x
            elif ball.rect.colliderect(paddle_right.rect):
                if ball.rect.centery > paddle_right.rect.top and ball.rect.centery < paddle_right.rect.bottom:
                    ball.speed_x *= -1.1
                    ball.speed_y = (ball.rect.centery - paddle_right.rect.centery) / HALF_PADDLE_HEIGHT * 5
                    ball.rect.x += ball.speed_x

            clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
