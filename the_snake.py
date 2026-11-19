import random

from typing import Optional, Tuple

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Изгиб Питона')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self) -> None:
        self.position: Tuple[int, int] = (
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        )
        self.body_color: Optional[Tuple[int, int, int]] = None

    def draw(self) -> None:
        """Метод для отрисовки объекта."""
        raise NotImplementedError

    def draw_cell(self, position: Tuple[int, int], color: Tuple[int, int, int]) -> None:
        """Отрисовывает одну ячейку по координатам БЕЗ рамок, чтобы не было артефактов."""
        x, y = position
        rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
        # Рисуем только заливку, без BORDER_COLOR
        pygame.draw.rect(screen, color, rect)


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self) -> None:
        super().__init__()
        self.body_color = APPLE_COLOR
        self.randomize_position([])

    def randomize_position(self, snake_positions: list) -> None:
        """Устанавливает случайное положение яблока, исключая клетки змейки."""
        while True:
            new_pos = (
                random.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if new_pos not in snake_positions:
                self.position = new_pos
                break

    def draw(self) -> None:
        """Отрисовывает яблоко на игровой поверхности."""
        if self.body_color:
            self.draw_cell(self.position, self.body_color)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self) -> None:
        super().__init__()
        self.reset()

    def update_direction(self) -> None:
        """Обновляет текущее направление движения."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Обновляет позицию змейки (движение)."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        global SPEED
        SPEED = 20  # Возвращаем начальную скорость

        self.length: int = 1
        self.positions: list = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction: Tuple[int, int] = random.choice(
            [UP, DOWN, LEFT, RIGHT]
        )
        self.next_direction: Optional[Tuple[int, int]] = None
        self.body_color = SNAKE_COLOR
        self.last: Optional[Tuple[int, int]] = None
        screen.fill(BOARD_BACKGROUND_COLOR)

    def get_head_position(self) -> Tuple[int, int]:
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def draw(self) -> None:
        """Отрисовывает змейку на экране."""
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)

        if self.body_color:
            for position in self.positions:
                self.draw_cell(position, self.body_color)


def handle_keys(game_object: Snake) -> None:
    """Обрабатывает нажатия клавиш для управления змейкой."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main() -> None:
    """Основной игровой цикл."""
    global SPEED
    pygame.init()

    snake = Snake()
    apple = Apple()

    while True:
        handle_keys(snake)
        snake.update_direction()
        
        # Проверка на столкновение с самим собой
        head_x, head_y = snake.get_head_position()
        dx, dy = snake.direction
        next_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        
        if next_head in snake.positions[:-1]:
            snake.reset()
            apple.randomize_position(snake.positions)
            continue

        snake.move()

        # Если змейка съела яблоко
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
            SPEED = min(SPEED + 1, 35)

        # Сначала рисуем змейку, чтобы яблоко было сверху
        snake.draw()
        apple.draw()
        pygame.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
