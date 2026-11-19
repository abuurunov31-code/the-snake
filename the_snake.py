import os
import random
import sys
from typing import List, Optional, Tuple

import pygame

# --- НАСТРОЙКИ ---
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

BOARD_BACKGROUND_COLOR = (20, 20, 20)
BORDER_COLOR = (93, 216, 228)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 215, 0)
APPLE_COLOR = (255, 50, 50)
SNAKE_COLOR = (50, 255, 50)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
HIGHSCORE_FILE = 'highscore.txt'

# --- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ (ТРЕБУЮТСЯ ТЕСТАМИ) ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


def load_highscore() -> int:
    """Загружает рекорд из файла."""
    if not os.path.exists(HIGHSCORE_FILE):
        return 0
    try:
        with open(HIGHSCORE_FILE, 'r') as f:
            return int(f.read().strip())
    except ValueError:
        return 0


def save_highscore(score: int) -> None:
    """Сохраняет рекорд в файл."""
    with open(HIGHSCORE_FILE, 'w') as f:
        f.write(str(score))


# --- КЛАССЫ ---
class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self) -> None:
        """Инициализация объекта."""
        self.position: Tuple[int, int] = (
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        )
        self.body_color: Optional[Tuple[int, int, int]] = None

    def draw(self, surface: pygame.Surface) -> None:
        """Метод для отрисовки объекта."""
        raise NotImplementedError

    def draw_cell(
        self,
        surface: pygame.Surface,
        position: Tuple[int, int],
        color: Tuple[int, int, int],
        border: bool = True
    ) -> None:
        """Универсальный метод отрисовки клетки."""
        x, y = position
        rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, color, rect)
        if border:
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс яблока."""

    def __init__(
        self,
        color: Tuple[int, int, int] = APPLE_COLOR
    ) -> None:
        """Инициализация яблока."""
        super().__init__()
        self.body_color = color
        self.randomize_position()

    def randomize_position(
        self,
        snake_positions: Optional[List[Tuple[int, int]]] = None
    ) -> None:
        """Устанавливает случайное положение яблока."""
        while True:
            self.position = (
                random.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if snake_positions and self.position in snake_positions:
                continue
            break

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает яблоко на игровой поверхности."""
        self.draw_cell(surface, self.position, self.body_color)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(
        self, color: Tuple[int, int, int] = SNAKE_COLOR
    ) -> None:
        """Инициализация змейки."""
        super().__init__()
        self.length: int = 1
        self.positions: List[Tuple[int, int]] = [self.position]
        self.direction: Tuple[int, int] = RIGHT
        self.next_direction: Optional[Tuple[int, int]] = None
        self.body_color = color
        self.last: Optional[Tuple[int, int]] = None

    def update_direction(self) -> None:
        """Обновляет текущее направление движения."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Обновляет позицию змейки."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        )
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None

    def get_head_position(self) -> Tuple[int, int]:
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает змейку на экране."""
        if self.last:
            self.draw_cell(
                surface, self.last, BOARD_BACKGROUND_COLOR, border=False
            )
        for position in self.positions:
            self.draw_cell(surface, position, self.body_color)


# --- ИГРОВОЙ ЦИКЛ ---
def handle_keys(snake: Snake) -> None:
    """Обрабатывает нажатия клавиш."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake.direction != DOWN:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN and snake.direction != UP:
                snake.next_direction = DOWN
            elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                snake.next_direction = RIGHT


def draw_game(
    surface: pygame.Surface,
    snake: Snake,
    apple: Apple,
    score: int,
    highscore: int
) -> None:
    """Отрисовывает игровой процесс."""
    surface.fill(BOARD_BACKGROUND_COLOR)
    apple.draw(surface)
    snake.draw(surface)
    font = pygame.font.Font(None, 30)
    score_text = font.render(f'Очки: {score}', True, TEXT_COLOR)
    highscore_text = font.render(
        f'Рекорд: {highscore}', True, HIGHLIGHT_COLOR
    )
    surface.blit(score_text, (10, 10))
    surface.blit(
        highscore_text, (SCREEN_WIDTH - 150, 10)
    )


def main() -> None:
    """Основной игровой цикл."""
    speed = 15
    score = 0
    highscore = load_highscore()

    snake = Snake()
    apple = Apple()
    apple.randomize_position(snake.positions)

    running = True
    while running:
        handle_keys(snake)
        snake.update_direction()

        head_x, head_y = snake.get_head_position()
        dx, dy = snake.direction
        next_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        )

        if next_head in snake.positions[:-1]:
            if score > highscore:
                highscore = score
                save_highscore(highscore)
            snake.reset()
            apple.randomize_position(snake.positions)
            score = 0
        else:
            snake.move()
            if snake.get_head_position() == apple.position:
                snake.length += 1
                apple.randomize_position(snake.positions)
                score += 10
                speed = min(speed + 1, 35)

        draw_game(screen, snake, apple, score, highscore)
        pygame.display.update()
        clock.tick(speed)

    pygame.quit()


if __name__ == '__main__':
    main()
