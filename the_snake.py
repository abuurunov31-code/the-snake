import os
import random
import sys
from typing import Callable, List, Optional, Tuple

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

SNAKE_COLORS = [
    (50, 255, 50), (50, 150, 255), (255, 255, 50), (255, 100, 200)
]
APPLE_COLORS = [(255, 50, 50), (255, 215, 0), (200, 50, 255)]
APPLE_SHAPES = ['Квадрат', 'Круг', 'Яблоко']

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
HIGHSCORE_FILE = 'highscore.txt'

translations = {
    'ru': {
        'play': 'Играть', 'settings': 'Настройки', 'records': 'Рекорды',
        'exit': 'Выход', 'speed': 'Скорость', 'difficulty': 'Сложность',
        'sound': 'Звук', 'on': 'Вкл', 'off': 'Выкл', 'back': 'Назад',
        'score': 'Очки', 'best': 'Лучший результат', 'lang_btn': 'Язык',
        'easy': 'Легко', 'normal': 'Средне', 'hard': 'Сложно',
        'snake_color': 'Цвет змейки', 'apple_color': 'Цвет яблока',
        'apple_shape': 'Форма яблока'
    },
    'en': {
        'play': 'Play', 'settings': 'Settings', 'records': 'Records',
        'exit': 'Exit', 'speed': 'Speed', 'difficulty': 'Difficulty',
        'sound': 'Sound', 'on': 'On', 'off': 'Off', 'back': 'Back',
        'score': 'Score', 'best': 'Best score', 'lang_btn': 'Language',
        'easy': 'Easy', 'normal': 'Normal', 'hard': 'Hard',
        'snake_color': 'Snake color', 'apple_color': 'Apple color',
        'apple_shape': 'Apple shape'
    },
    'tg': {
        'play': 'Бозӣ', 'settings': 'Танзимот', 'records': 'Рекордҳо',
        'exit': 'Баромад', 'speed': 'Суръат', 'difficulty': 'Мураккабӣ',
        'sound': 'Овоз', 'on': 'Дар', 'off': 'Хомӯш', 'back': 'Бозгашт',
        'score': 'Хол', 'best': 'Беҳтарин натиҷа', 'lang_btn': 'Забон',
        'easy': 'Осон', 'normal': 'Миёна', 'hard': 'Сахт',
        'snake_color': 'Ранги мор', 'apple_color': 'Ранги себ',
        'apple_shape': 'Шакли себ'
    }
}


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
        color: Tuple[int, int, int] = (255, 50, 50),
        shape: str = 'Квадрат'
    ) -> None:
        """Инициализация яблока."""
        super().__init__()
        self.body_color = color
        self.shape = shape
        self.randomize_position()

    def randomize_position(
        self,
        obstacles: Optional[List['Obstacle']] = None,
        snake_positions: Optional[List[Tuple[int, int]]] = None
    ) -> None:
        """Устанавливает случайное положение яблока."""
        while True:
            self.position = (
                random.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if obstacles and self.position in [
                obs.position for obs in obstacles
            ]:
                continue
            if snake_positions and self.position in snake_positions:
                continue
            break

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает яблоко на игровой поверхности."""
        if self.shape == 'Круг':
            center = (
                self.position[0] + GRID_SIZE // 2,
                self.position[1] + GRID_SIZE // 2
            )
            pygame.draw.circle(
                surface, self.body_color, center, GRID_SIZE // 2
            )
            pygame.draw.circle(
                surface, BORDER_COLOR, center, GRID_SIZE // 2, 1
            )

        elif self.shape == 'Яблоко':
            center_left = (
                self.position[0] + GRID_SIZE // 3,
                self.position[1] + GRID_SIZE // 2
            )
            center_right = (
                self.position[0] + 2 * GRID_SIZE // 3,
                self.position[1] + GRID_SIZE // 2
            )
            radius = GRID_SIZE // 3

            pygame.draw.circle(surface, self.body_color, center_left, radius)
            pygame.draw.circle(surface, self.body_color, center_right, radius)

            branch_rect = pygame.Rect(
                self.position[0] + GRID_SIZE // 2 - 1,
                self.position[1], 2, GRID_SIZE // 3
            )
            pygame.draw.rect(surface, (139, 69, 19), branch_rect)

            leaf_points = [
                (self.position[0] + GRID_SIZE // 2,
                 self.position[1] + GRID_SIZE // 6),
                (self.position[0] + GRID_SIZE // 2 + 5,
                 self.position[1] + 2),
                (self.position[0] + GRID_SIZE // 2 - 3,
                 self.position[1] + 4)
            ]
            pygame.draw.polygon(surface, (50, 200, 50), leaf_points)
            pygame.draw.circle(
                surface, (255, 255, 255),
                (center_left[0] - 2, center_left[1] - 2), 2
            )

        else:
            self.draw_cell(surface, self.position, self.body_color)


class GoldenApple(Apple):
    """Класс золотого яблока."""

    def __init__(self, shape: str = 'Квадрат') -> None:
        """Инициализация золотого яблока."""
        super().__init__(color=HIGHLIGHT_COLOR, shape=shape)
        self.timer = 300

    def update(self) -> bool:
        """Обновляет таймер жизни золотого яблока."""
        self.timer -= 1
        return self.timer > 0


class Obstacle(GameObject):
    """Класс препятствия."""

    def __init__(self, pos: Tuple[int, int]) -> None:
        """Инициализация препятствия."""
        super().__init__()
        self.position = pos
        self.body_color = (150, 150, 150)

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает препятствие."""
        x, y = self.position
        rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.line(
            surface, BOARD_BACKGROUND_COLOR, rect.topleft,
            rect.bottomright, 2
        )
        pygame.draw.line(
            surface, BOARD_BACKGROUND_COLOR, rect.topright,
            rect.bottomleft, 2
        )


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self, color: Tuple[int, int, int] = (50, 255, 50)) -> None:
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


class Button:
    """Класс кнопки меню."""

    def __init__(
        self,
        text: str,
        x: int,
        y: int,
        w: int,
        h: int,
        color: Tuple[int, int, int],
        action: Callable,
        click_sound: Optional[pygame.mixer.Sound] = None
    ) -> None:
        """Инициализация кнопки."""
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.action = action
        self.font = pygame.font.Font(None, 28)
        self.click_sound = click_sound

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает кнопку."""
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, TEXT_COLOR, self.rect, 2)
        text_surf = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_click(self, pos: Tuple[int, int]) -> None:
        """Проверяет клик по кнопке."""
        if self.rect.collidepoint(pos):
            if self.click_sound:
                self.click_sound.play()
            self.action()


# --- МЕНЮ ---
def draw_main_menu(
    screen: pygame.Surface,
    t: dict,
    s: Optional[pygame.mixer.Sound],
    a: dict
) -> List[Button]:
    """Отрисовывает главное меню."""
    screen.fill(BOARD_BACKGROUND_COLOR)
    return [
        Button(t['play'], 220, 100, 200, 50, (100, 255, 100), a['play'], s),
        Button(t['settings'], 220, 170, 200, 50, (255, 255, 100), a['settings'], s),
        Button(t['records'], 220, 240, 200, 50, (255, 215, 0), a['records'], s),
        Button(t['exit'], 220, 310, 200, 50, (255, 100, 100), a['exit'], s),
    ]


def draw_settings_menu(
    screen: pygame.Surface,
    t: dict,
    st: dict,
    s: Optional[pygame.mixer.Sound],
    a: dict
) -> List[Button]:
    """Отрисовывает меню настроек."""
    screen.fill(BOARD_BACKGROUND_COLOR)
    title = pygame.font.Font(None, 50).render(t['settings'], True, TEXT_COLOR)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 10))
    dm = {'Easy': t['easy'], 'Normal': t['normal'], 'Hard': t['hard']}
    sound_txt = f"{t['sound']}: {t['on'] if st['sound'] else t['off']}"
    shape_txt = f"{t['apple_shape']}: {APPLE_SHAPES[st['apple_shape_idx']]}"
    return [
        Button(f"{t['speed']}: {st['speed']}", 170, 60, 300, 35, (255, 200, 200), a['speed'], s),
        Button(f"{t['difficulty']}: {dm[st['difficulty']]}", 170, 105, 300, 35, (200, 200, 255), a['diff'], s),
        Button(sound_txt, 170, 150, 300, 35, (200, 255, 200), a['sound'], s),
        Button(f"{t['lang_btn']}: {st['lang'].upper()}", 170, 195, 300, 35, (255, 255, 150), a['lang'], s),
        Button(f"{t['snake_color']}: {st['snake_color_idx'] + 1}", 170, 240, 300, 35, (150, 255, 255), a['sc'], s),
        Button(f"{t['apple_color']}: {st['apple_color_idx'] + 1}", 170, 285, 300, 35, (255, 200, 150), a['ac'], s),
        Button(shape_txt, 170, 330, 300, 35, (200, 150, 255), a['ash'], s),
        Button(t['back'], 220, 400, 200, 40, (100, 100, 255), a['back'], s),
    ]


def draw_records_menu(
    screen: pygame.Surface,
    t: dict,
    s: Optional[pygame.mixer.Sound],
    a: dict
) -> List[Button]:
    """Отрисовывает меню рекордов."""
    screen.fill(BOARD_BACKGROUND_COLOR)
    title = pygame.font.Font(None, 50).render(t['records'], True, TEXT_COLOR)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
    hs = load_highscore()
    score_text = pygame.font.Font(None, 50).render(f"{t['best']}: {hs}", True, HIGHLIGHT_COLOR)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 180))
    return [Button(t['back'], 220, 380, 200, 50, (100, 100, 255), a['back'], s)]


def create_actions(settings: dict, go: Callable, set_run: Callable) -> dict:
    """Создает словарь действий для кнопок меню."""
    def cycle_speed() -> None:
        sp = [10, 15, 20, 25, 30, 35]
        settings['speed'] = sp[(sp.index(settings['speed']) + 1) % len(sp)]

    def cycle_diff() -> None:
        lv = ['Easy', 'Normal', 'Hard']
        settings['difficulty'] = lv[(lv.index(settings['difficulty']) + 1) % len(lv)]

    def toggle_sound() -> None:
        settings['sound'] = not settings['sound']

    def cycle_lang() -> None:
        lg = ['ru', 'en', 'tg']
        settings['lang'] = lg[(lg.index(settings['lang']) + 1) % len(lg)]

    def cycle_snake() -> None:
        settings['snake_color_idx'] = (settings['snake_color_idx'] + 1) % len(SNAKE_COLORS)

    def cycle_apple() -> None:
        settings['apple_color_idx'] = (settings['apple_color_idx'] + 1) % len(APPLE_COLORS)

    def cycle_shape() -> None:
        settings['apple_shape_idx'] = (settings['apple_shape_idx'] + 1) % len(APPLE_SHAPES)

    return {
        'play': lambda: set_run(False),
        'exit': lambda: sys.exit(),
        'settings': lambda: go('settings'),
        'records': lambda: go('records'),
        'back': lambda: go('main'),
        'speed': cycle_speed,
        'diff': cycle_diff,
        'sound': toggle_sound,
        'lang': cycle_lang,
        'sc': cycle_snake,
        'ac': cycle_apple,
        'ash': cycle_shape,
    }


def show_menu(screen: pygame.Surface, clock: pygame.time.Clock) -> dict:
    """Отображает главное меню."""
    settings = {'speed': 20, 'difficulty': 'Normal', 'sound': True, 'lang': 'ru', 'snake_color_idx': 0, 'apple_color_idx': 0, 'apple_shape_idx': 0}
    try:
        s = pygame.mixer.Sound('click.wav')
    except (pygame.error, IOError):
        s = None

    curr = ['main']
    run = [True]

    def go(name: str) -> None:
        curr[0] = name

    def set_run(val: bool) -> None:
        run[0] = val

    actions = create_actions(settings, go, set_run)

    while run[0]:
        t = translations[settings['lang']]
        if curr[0] == 'main':
            buttons = draw_main_menu(screen, t, s, actions)
        elif curr[0] == 'settings':
            buttons = draw_settings_menu(screen, t, settings, s, actions)
        else:
            buttons = draw_records_menu(screen, t, s, actions)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in buttons:
                    btn.check_click(event.pos)

        for btn in buttons:
            btn.draw(screen)
        pygame.display.flip()
        clock.tick(30)
    return settings


# --- ОСНОВНАЯ ИГРА ---
def handle_input(snake: Snake) -> None:
    """Обрабатывает нажатия клавиш."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
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


def check_collisions(snake: Snake, obstacles: List[Obstacle]) -> bool:
    """Проверяет, жива ли змейка."""
    head_x, head_y = snake.get_head_position()
    dx, dy = snake.direction
    nh = ((head_x + dx * GRID_SIZE) % SCREEN_WIDTH, (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT)
    return nh not in snake.positions[:-1] and nh not in [o.position for o in obstacles]


def draw_game(screen: pygame.Surface, snake: Snake, apple: Apple, obs: List[Obstacle], golden: Optional[GoldenApple], score: int, highscore: int, t: dict) -> None:
    """Отрисовывает игровой процесс."""
    screen.fill(BOARD_BACKGROUND_COLOR)
    for o in obs:
        o.draw(screen)
    apple.draw(screen)
    if golden:
        golden.draw(screen)
    snake.draw(screen)
    font = pygame.font.Font(None, 30)
    screen.blit(font.render(f"{t['score']}: {score}", True, TEXT_COLOR), (10, 10))
    screen.blit(font.render(f"{t['best']}: {highscore}", True, HIGHLIGHT_COLOR), (SCREEN_WIDTH - 150, 10))


def main() -> None:
    """Основной игровой цикл."""
    pygame.init()
    try:
        pygame.mixer.init()
        eat_sound = pygame.mixer.Sound('eat.wav')
        crash_sound = pygame.mixer.Sound('crash.wav')
    except (pygame.error, IOError):
        eat_sound = None
        crash_sound = None

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Продвинутая Змейка')
    clock = pygame.time.Clock()

    settings = show_menu(screen, clock)
    t = translations[settings['lang']]
    score = 0
    hs = load_highscore()

    obs = []
    count = 10 if settings['difficulty'] == 'Normal' else 20
    for _ in range(count):
        pos = (random.randint(0, GRID_WIDTH - 1) * GRID_SIZE, random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE)
        obs.append(Obstacle(pos))

    snake = Snake(color=SNAKE_COLORS[settings['snake_color_idx']])
    apple = Apple(color=APPLE_COLORS[settings['apple_color_idx']], shape=APPLE_SHAPES[settings['apple_shape_idx']])
    apple.randomize_position(obs, snake.positions)
    golden = None

    running = True
    while running:
        handle_input(snake)
        snake.update_direction()

        if check_collisions(snake, obs):
            snake.move()
            if snake.get_head_position() == apple.position:
                snake.length += 1
                apple.randomize_position(obs, snake.positions)
                if eat_sound and settings['sound']:
                    eat_sound.play()
                score += 10
                if random.random() < 0.2 and golden is None:
                    golden = GoldenApple(shape=APPLE_SHAPES[settings['apple_shape_idx']])
                    golden.randomize_position(obs, snake.positions)
            if golden:
                if not golden.update():
                    golden = None
                elif snake.get_head_position() == golden.position:
                    snake.length += 3
                    score += 30
                    golden = None
                    if eat_sound and settings['sound']:
                        eat_sound.play()
        else:
            if crash_sound and settings['sound']:
                crash_sound.play()
            if score > hs:
                hs = score
                save_highscore(hs)
            snake.reset()
            apple.randomize_position(obs, snake.positions)
            golden = None
            score = 0

        draw_game(screen, snake, apple, obs, golden, score, hs, t)
        pygame.display.update()
        clock.tick(settings['speed'])

    pygame.quit()


if __name__ == '__main__':
    main()
