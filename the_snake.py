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

SNAKE_COLORS = [(50, 255, 50), (50, 150, 255), (255, 255, 50), (255, 100, 200)]
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
    """Сохраняет рекорд."""
    with open(HIGHSCORE_FILE, 'w') as f:
        f.write(str(score))


# --- КЛАССЫ ---
class GameObject:
    """Базовый класс."""
    def __init__(self) -> None:
        self.position: Tuple[int, int] = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color: Optional[Tuple[int, int, int]] = None

    def draw(self, surface: pygame.Surface) -> None:
        raise NotImplementedError

    def draw_cell(self, surface: pygame.Surface, position: Tuple[int, int], color: Tuple[int, int, int], border: bool = True) -> None:
        rect = pygame.Rect(position[0], position[1], GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, color, rect)
        if border:
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Яблоко."""
    def __init__(self, color: Tuple[int, int, int] = (255, 50, 50), shape: str = 'Квадрат') -> None:
        super().__init__()
        self.body_color = color
        self.shape = shape
        self.randomize_position()

    def randomize_position(self, obstacles: Optional[List['Obstacle']] = None, snake_positions: Optional[List[Tuple[int, int]]] = None) -> None:
        while True:
            self.position = (random.randint(0, GRID_WIDTH - 1) * GRID_SIZE, random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE)
            if obstacles and self.position in [obs.position for obs in obstacles]:
                continue
            if snake_positions and self.position in snake_positions:
                continue
            break

    def draw(self, surface: pygame.Surface) -> None:
        if self.shape == 'Круг':
            center = (self.position[0] + GRID_SIZE // 2, self.position[1] + GRID_SIZE // 2)
            pygame.draw.circle(surface, self.body_color, center, GRID_SIZE // 2)
            pygame.draw.circle(surface, BORDER_COLOR, center, GRID_SIZE // 2, 1)
        elif self.shape == 'Яблоко':
            cl = (self.position[0] + GRID_SIZE // 3, self.position[1] + GRID_SIZE // 2)
            cr = (self.position[0] + 2 * GRID_SIZE // 3, self.position[1] + GRID_SIZE // 2)
            r = GRID_SIZE // 3
            pygame.draw.circle(surface, self.body_color, cl, r)
            pygame.draw.circle(surface, self.body_color, cr, r)
            rect = pygame.Rect(self.position[0] + GRID_SIZE // 2 - 1, self.position[1], 2, GRID_SIZE // 3)
            pygame.draw.rect(surface, (139, 69, 19), rect)
            pts = [(self.position[0] + GRID_SIZE // 2, self.position[1] + GRID_SIZE // 6), (self.position[0] + GRID_SIZE // 2 + 5, self.position[1] + 2), (self.position[0] + GRID_SIZE // 2 - 3, self.position[1] + 4)]
            pygame.draw.polygon(surface, (50, 200, 50), pts)
            pygame.draw.circle(surface, (255, 255, 255), (cl[0] - 2, cl[1] - 2), 2)
        else:
            self.draw_cell(surface, self.position, self.body_color)


class GoldenApple(Apple):
    """Золотое яблоко."""
    def __init__(self, shape: str = 'Квадрат') -> None:
        super().__init__(color=HIGHLIGHT_COLOR, shape=shape)
        self.timer = 300

    def update(self) -> bool:
        self.timer -= 1
        return self.timer > 0


class Obstacle(GameObject):
    """Препятствие."""
    def __init__(self, pos: Tuple[int, int]) -> None:
        super().__init__()
        self.position = pos
        self.body_color = (150, 150, 150)

    def draw(self, surface: pygame.Surface) -> None:
        rect = pygame.Rect(self.position[0], self.position[1], GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.line(surface, BOARD_BACKGROUND_COLOR, rect.topleft, rect.bottomright, 2)
        pygame.draw.line(surface, BOARD_BACKGROUND_COLOR, rect.topright, rect.bottomleft, 2)


class Snake(GameObject):
    """Змейка."""
    def __init__(self, color: Tuple[int, int, int] = (50, 255, 50)) -> None:
        super().__init__()
        self.length: int = 1
        self.positions: List[Tuple[int, int]] = [self.position]
        self.direction: Tuple[int, int] = RIGHT
        self.next_direction: Optional[Tuple[int, int]] = None
        self.body_color = color
        self.last: Optional[Tuple[int, int]] = None

    def update_direction(self) -> None:
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = ((head_x + dx * GRID_SIZE) % SCREEN_WIDTH, (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT)
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def reset(self) -> None:
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None

    def get_head_position(self) -> Tuple[int, int]:
        return self.positions[0]

    def draw(self, surface: pygame.Surface) -> None:
        if self.last:
            self.draw_cell(surface, self.last, BOARD_BACKGROUND_COLOR, border=False)
        for pos in self.positions:
            self.draw_cell(surface, pos, self.body_color)


class Button:
    """Кнопка."""
    def __init__(self, text: str, x: int, y: int, w: int, h: int, color: Tuple[int, int, int], action: Callable, click_sound: Optional[pygame.mixer.Sound] = None) -> None:
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.action = action
        self.font = pygame.font.Font(None, 28)
        self.click_sound = click_sound

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, TEXT_COLOR, self.rect, 2)
        text = self.font.render(self.text, True, (0, 0, 0))
        surface.blit(text, text.get_rect(center=self.rect.center))

    def check_click(self, pos: Tuple[int, int]) -> None:
        if self.rect.collidepoint(pos):
            if self.click_sound:
                self.click_sound.play()
            self.action()


# --- МЕНЮ (МАЛЕНЬКИЕ ФУНКЦИИ) ---
def draw_menu(screen: pygame.Surface, t: dict, s: Optional[pygame.mixer.Sound], a: dict) -> List[Button]:
    screen.fill(BOARD_BACKGROUND_COLOR)
    return [
        Button(t['play'], 220, 100, 200, 50, (100, 255, 100), a['play'], s),
        Button(t['settings'], 220, 170, 200, 50, (255, 255, 100), a['settings'], s),
        Button(t['records'], 220, 240, 200, 50, (255, 215, 0), a['records'], s),
        Button(t['exit'], 220, 310, 200, 50, (255, 100, 100), a['exit'], s),
    ]


def draw_settings(screen: pygame.Surface, t: dict, st: dict, s: Optional[pygame.mixer.Sound], a: dict) -> List[Button]:
    screen.fill(BOARD_BACKGROUND_COLOR)
    title = pygame.font.Font(None, 50).render(t['settings'], True, TEXT_COLOR)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 10))
    dm = {'Easy': t['easy'], 'Normal': t['normal'], 'Hard': t['hard']}
    return [
        Button(f"{t['speed']}: {st['speed']}", 170, 60, 300, 35, (255, 200, 200), a['speed'], s),
        Button(f"{t['difficulty']}: {dm[st['difficulty']]}", 170, 105, 300, 35, (200, 200, 255), a['diff'], s),
        Button(f"{t['sound']}: {t['on'] if st['sound'] else t['off']}", 170, 150, 300, 35, (200, 255, 200), a['sound'], s),
        Button(f"{t['lang_btn']}: {st['lang'].upper()}", 170, 195, 300, 35, (255, 255, 150), a['lang'], s),
        Button(f"{t['snake_color']}: {st['snake_color_idx'] + 1}", 170, 240, 300, 35, (150, 255, 255), a['sc'], s),
        Button(f"{t['apple_color']}: {st['apple_color_idx'] + 1}", 170, 285, 300, 35, (255, 200, 150), a['ac'], s),
        Button(f"{t['apple_shape']}: {APPLE_SHAPES[st['apple_shape_idx']]}", 170, 330, 300, 35, (200, 150, 255), a['ash'], s),
        Button(t['back'], 220, 400, 200, 40, (100, 100, 255), a['back'], s),
    ]


def draw_records(screen: pygame.Surface, t: dict, s: Optional[pygame.mixer.Sound], a: dict) -> List[Button]:
    screen.fill(BOARD_BACKGROUND_COLOR)
    title = pygame.font.Font(None, 50).render(t['records'], True, TEXT_COLOR)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
    hs = load_highscore()
    text = pygame.font.Font(None, 50).render(f"{t['best']}: {hs}", True, HIGHLIGHT_COLOR)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 180))
    return [Button(t['back'], 220, 380, 200, 50, (100, 100, 255), a['back'], s)]


def show_menu(screen: pygame.Surface, clock: pygame.time.Clock) -> dict:
    """Главное меню."""
    running = True
    curr = 'main'
    st = {'speed': 20, 'difficulty': 'Normal', 'sound': True, 'lang': 'ru', 'snake_color_idx': 0, 'apple_color_idx': 0, 'apple_shape_idx': 0}

    try:
        s = pygame.mixer.Sound('click.wav')
    except (pygame.error, IOError):
        s = None

    def go(n: str) -> None:
        nonlocal curr
        curr = n

    def act(k: str) -> Callable:
        return lambda: handle(k)

    def handle(k: str) -> None:
        nonlocal running
        if k == 'play':
            running = False
        elif k == 'exit':
            pygame.quit()
            sys.exit()
        elif k == 'back':
            go('main')
        elif k == 'settings':
            go('settings')
        elif k == 'records':
            go('records')
        elif k == 'speed':
            sp = [10, 15, 20, 25, 30, 35]
            st['speed'] = sp[(sp.index(st['speed']) + 1) % len(sp)]
        elif k == 'diff':
            lv = ['Easy', 'Normal', 'Hard']
            st['difficulty'] = lv[(lv.index(st['difficulty']) + 1) % len(lv)]
        elif k == 'sound':
            st['sound'] = not st['sound']
        elif k == 'lang':
            lg = ['ru', 'en', 'tg']
            st['lang'] = lg[(lg.index(st['lang']) + 1) % len(lg)]
        elif k == 'sc':
            st['snake_color_idx'] = (st['snake_color_idx'] + 1) % len(SNAKE_COLORS)
        elif k == 'ac':
            st['apple_color_idx'] = (st['apple_color_idx'] + 1) % len(APPLE_COLORS)
        elif k == 'ash':
            st['apple_shape_idx'] = (st['apple_shape_idx'] + 1) % len(APPLE_SHAPES)

    a = {k: act(k) for k in ['play', 'exit', 'settings', 'records', 'back', 'speed', 'diff', 'sound', 'lang', 'sc', 'ac', 'ash']}

    while running:
        t = translations[st['lang']]
        if curr == 'main':
            b = draw_menu(screen, t, s, a)
        elif curr == 'settings':
            b = draw_settings(screen, t, st, s, a)
        else:
            b = draw_records(screen, t, s, a)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                for btn in b:
                    btn.check_click(e.pos)

        for btn in b:
            btn.draw(screen)
        pygame.display.flip()
        clock.tick(30)
    return st


def update_game(snake: Snake, apple: Apple, obstacles: List[Obstacle], st: dict, score: int) -> Tuple[int, Optional[GoldenApple]]:
    """Обновляет игру. Возвращает новый счет и золотое яблоко (если есть)."""
    head_x, head_y = snake.get_head_position()
    dx, dy = snake.direction
    nh = ((head_x + dx * GRID_SIZE) % SCREEN_WIDTH, (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT)
    
    alive = nh not in snake.positions[:-1] and nh not in [o.position for o in obstacles]

    if not alive:
        snake.reset()
        apple.randomize_position(obstacles, snake.positions)
        return 0, None

    snake.move()

    if snake.get_head_position() == apple.position:
        snake.length += 1
        apple.randomize_position(obstacles, snake.positions)
        score += 10

    return score, None


def main() -> None:
    """Игра."""
    pygame.init()
    try:
        pygame.mixer.init()
        eat = pygame.mixer.Sound('eat.wav')
        crash = pygame.mixer.Sound('crash.wav')
    except (pygame.error, IOError):
        eat = None
        crash = None

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Продвинутая Змейка')
    clock = pygame.time.Clock()

    st = show_menu(screen, clock)
    t = translations[st['lang']]
    score = 0
    hs = load_highscore()
    font = pygame.font.Font(None, 30)

    obs = [Obstacle((random.randint(0, GRID_WIDTH - 1) * GRID_SIZE, random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE)) for _ in range(10 if st['difficulty'] == 'Normal' else 20)]
    snake = Snake(color=SNAKE_COLORS[st['snake_color_idx']])
    apple = Apple(color=APPLE_COLORS[st['apple_color_idx']], shape=APPLE_SHAPES[st['apple_shape_idx']])
    apple.randomize_position(obs, snake.positions)

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP and snake.direction != DOWN:
                    snake.next_direction = UP
                elif e.key == pygame.K_DOWN and snake.direction != UP:
                    snake.next_direction = DOWN
                elif e.key == pygame.K_LEFT and snake.direction != RIGHT:
                    snake.next_direction = LEFT
                elif e.key == pygame.K_RIGHT and snake.direction != LEFT:
                    snake.next_direction = RIGHT

        snake.update_direction()
        score, _ = update_game(snake, apple, obs, st, score)

        if score > hs:
            hs = score
            save_highscore(hs)

        screen.fill(BOARD_BACKGROUND_COLOR)
        for o in obs:
            o.draw(screen)
        apple.draw(screen)
        snake.draw(screen)

        screen.blit(font.render(f"{t['score']}: {score}", True, TEXT_COLOR), (10, 10))
        screen.blit(font.render(f"{t['best']}: {hs}", True, HIGHLIGHT_COLOR), (SCREEN_WIDTH - 150, 10))

        pygame.display.update()
        clock.tick(st['speed'])

    pygame.quit()


if __name__ == '__main__':
    main()
