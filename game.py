
# game.py
import sys
import random
from pathlib import Path
import pygame

GRID_SIZE = 24
GRID_W, GRID_H = 28, 22
MARGIN = 32
FPS_START = 10
FPS_INC = 0.6

BG = (18, 18, 18)
GRID_DARK = (28, 28, 28)
GRID_LIGHT = (24, 24, 24)
SNAKE_HEAD = (64, 220, 120)
SNAKE_BODY = (32, 160, 96)
FOOD = (240, 64, 64)
TEXT = (230, 230, 230)
SHADOW = (0, 0, 0)

WIDTH = GRID_W * GRID_SIZE
HEIGHT = GRID_H * GRID_SIZE + MARGIN
HS_FILE = Path(__file__).with_name("snake_highscore.txt")


def load_high_score():
    try:
        return int(HS_FILE.read_text().strip())
    except Exception:
        return 0


def save_high_score(score):
    try:
        current = load_high_score()
        if score > current:
            HS_FILE.write_text(str(score))
    except Exception:
        pass


def rand_empty_cell(occupied):
    while True:
        p = (random.randrange(GRID_W), random.randrange(GRID_H))
        if p not in occupied:
            return p


class Snake:
    def __init__(self):
        cx, cy = GRID_W // 2, GRID_H // 2
        self.body = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.dir = (1, 0)
        self.grow = 0

    def set_dir(self, dx, dy):
        if (dx, dy) == (-self.dir[0], -self.dir[1]):
            return
        if dx == 0 and dy == 0:
            return
        self.dir = (dx, dy)

    def head(self):
        return self.body[0]

    def step(self):
        hx, hy = self.head()
        dx, dy = self.dir
        nx, ny = hx + dx, hy + dy
        self.body.insert(0, (nx, ny))
        if self.grow > 0:
            self.grow -= 1
        else:
            self.body.pop()
        return nx, ny

    def occupies(self):
        return set(self.body)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snake — pygame")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas,menlo,monospace", 20)
        self.reset()

    def reset(self):
        self.snake = Snake()
        self.food = rand_empty_cell(self.snake.occupies())
        self.score = 0
        self.high = load_high_score()
        self.fps = FPS_START
        self.paused = False
        self.game_over = False

    def update(self):
        if self.paused or self.game_over:
            return
        nx, ny = self.snake.step()
        if not (0 <= nx < GRID_W and 0 <= ny < GRID_H):
            self.game_over = True
            save_high_score(self.score)
            return
        if self.snake.body[0] in self.snake.body[1:]:
            self.game_over = True
            save_high_score(self.score)
            return
        if (nx, ny) == self.food:
            self.score += 1
            self.snake.grow += 1
            self.fps += FPS_INC
            self.food = rand_empty_cell(self.snake.occupies())
            if self.score > self.high:
                self.high = self.score

    def draw_grid(self):
        for y in range(GRID_H):
            for x in range(GRID_W):
                r = pygame.Rect(x * GRID_SIZE, MARGIN + y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                self.screen.fill(GRID_LIGHT if (x + y) % 2 == 0 else GRID_DARK, r)

    def draw_snake(self):
        for i, (x, y) in enumerate(self.snake.body):
            rect = pygame.Rect(x * GRID_SIZE + 2, MARGIN + y * GRID_SIZE + 2, GRID_SIZE - 4, GRID_SIZE - 4)
            color = SNAKE_HEAD if i == 0 else SNAKE_BODY
            pygame.draw.rect(self.screen, color, rect, border_radius=6)

    def draw_food(self):
        x, y = self.food
        cx = x * GRID_SIZE + GRID_SIZE // 2
        cy = MARGIN + y * GRID_SIZE + GRID_SIZE // 2
        pygame.draw.circle(self.screen, FOOD, (cx, cy), GRID_SIZE // 3)

    def draw_ui(self):
        self.screen.fill(BG, pygame.Rect(0, 0, WIDTH, MARGIN))
        s_text = self.font.render(f"Score: {self.score}", True, TEXT)
        h_text = self.font.render(f"High: {self.high}", True, TEXT)
        self.screen.blit(s_text, (12, 6))
        self.screen.blit(h_text, (WIDTH - h_text.get_width() - 12, 6))
        if self.paused:
            self.overlay("Paused — press P to resume")
        if self.game_over:
            self.overlay("Game Over — press R to restart")

    def overlay(self, msg):
        font_big = pygame.font.SysFont("consolas,menlo,monospace", 26, bold=True)
        text = font_big.render(msg, True, TEXT)
        shadow = font_big.render(msg, True, SHADOW)
        cx = WIDTH // 2 - text.get_width() // 2
        cy = MARGIN + (GRID_H * GRID_SIZE) // 2 - text.get_height() // 2
        self.screen.blit(shadow, (cx + 2, cy + 2))
        self.screen.blit(text, (cx, cy))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_high_score(self.score)
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        save_high_score(self.score)
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_p and not self.game_over:
                        self.paused = not self.paused
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        self.snake.set_dir(0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.snake.set_dir(0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self.snake.set_dir(-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.snake.set_dir(1, 0)

            self.update()
            self.screen.fill(BG)
            self.draw_ui()
            self.draw_grid()
            self.draw_food()
            self.draw_snake()

            pygame.display.flip()
            self.clock.tick(self.fps)

# main.py
from game import Game

def main():
    Game().run()

if __name__ == "__main__":
    main()


