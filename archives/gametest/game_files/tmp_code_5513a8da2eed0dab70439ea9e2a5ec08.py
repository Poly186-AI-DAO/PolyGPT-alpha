import pygame
import sys
import time
import random

# Define some constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRIDSIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRIDSIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRIDSIZE
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
        self.clock = pygame.time.Clock()
        self.snake = Snake()
        self.food = Food()

    def check_for_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.snake.turn(UP)
                elif event.key == pygame.K_DOWN:
                    self.snake.turn(DOWN)
                elif event.key == pygame.K_LEFT:
                    self.snake.turn(LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.snake.turn(RIGHT)

    def update(self):
        self.snake.move()
        if self.snake.get_head_position() == self.food.position:
            self.snake.length += 1
            self.food.randomize_position()

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.snake.draw(self.screen)
        self.food.draw(self.screen)
        pygame.display.update()

    def run(self):
        while True:
            self.check_for_events()
            self.update()
            self.draw()
            self.clock.tick(12)

class Snake:
    def __init__(self):
        self.length = 1
        self.positions = [((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color = (0, 255, 0)

    def get_head_position(self):
        return self.positions[0]

    def turn(self, point):
        if self.length > 1 and (point[0] * -1, point[1] * -1) == self.direction:
            return
        else:
            self.direction = point

    def move(self):
        cur = self.get_head_position()
        x, y = self.direction
        new = (((cur[0] + (x*GRIDSIZE)) % SCREEN_WIDTH), (cur[1] + (y*GRIDSIZE)) % SCREEN_HEIGHT)
        if len(self.positions) > 2 and new in self.positions[2:]:
            self.reset()
        else:
            self.positions.insert(0, new)
            if len(self.positions) > self.length:
                self.positions.pop()

    def reset(self):
        self.length = 1
        self.positions = [((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])

    def draw(self, surface):
        for p in self.positions:
            pygame.draw.rect(surface, self.color, (p[0], p[1], GRIDSIZE, GRIDSIZE))

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = (255, 0, 0)
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1) * GRIDSIZE, random.randint(0, GRID_HEIGHT - 1) * GRIDSIZE)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.position[0], self.position[1], GRIDSIZE, GRIDSIZE))

if __name__ == "__main__":
    game = Game()
    game.run()