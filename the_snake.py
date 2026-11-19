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


# --- БАЗОВЫЕ КЛАССЫ ---
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


# --- МЕНЮ (МАКСИМАЛЬНО РАЗБИТО) ---
def draw_main_menu(screen, t, s, a):
    """Главное меню."""
    screen.fill(BOARD_BACKGROUND_COLOR)
    return [
        Button(t['play'], 220, 100, 200, 50, (100, 255, 100), a['play'], s),
        Button(t['settings'], 220, 170, 200, 50, (255, 255, 100), a['settings'], s),
        Button(t['records'], 220, 240, 200, 50, (255, 215, 0), a['records'], s),
        Button(t['exit'], 220, 310, 200, 50, (255, 100, 100), a['exit'], s),
    ]

def draw_settings_menu(screen, t, st, s, a):
    """Меню настроек."""
    screen.fill(BOARD_BACKGROUND_COLOR)
    title = pygame.font.Font(None, 50).render(t['settings'], True, TEXT_COLOR)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 10))
    dm = {'Easy': t['easy'], 'Normal': t['normal'], 'Hard': t['hard']}
    stxt = f"{t['sound']}: {t['on'] if st['sound'] else t['off']}"
    shtxt = f"{t['apple_shape']}: {APPLE_SHAPES[st['apple_shape_idx']]}"
    return [
        Button(f"{t['speed']}: {st['speed']}", 170, 60, 300, 35, (255, 200, 200), a['speed'], s),
        Button(f"{t['difficulty']}: {dm[st['difficulty']]}", 170, 105, 300, 35, (200, 200, 255), a['diff'], s),
        Button(stxt, 170, 150, 300, 35, (200, 255, 200), a['sound'], s),
        Button(f"{t['lang_btn']}: {st['lang'].upper()}", 170, 195, 300, 35, (255, 255, 150), a['lang'], s),
        Button(f"{t['snake_color']}: {st['snake_color_idx'] + 1}", 170, 240, 300, 35, (150, 255, 255), a['sc'], s),
        Button(f"{t['apple_color']}: {st['apple_color_idx'] + 1}", 170, 285, 300, 35, (255, 200, 150), a['ac'], s),
        Button(shtxt, 170, 330, 300, 35, (200, 150, 255), a['ash'], s),
        Button(t['back'], 220, 400, 200, 40, (100, 100, 255), a['back'], s),
    ]

def draw_records_menu(screen, t, s, a):
    """Меню рекордов."""
    screen.fill(BOARD_BACKGROUND_COLOR)
    title = pygame.font.Font(None, 50).render(t['records'], True, TEXT_COLOR)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
    hs = load_highscore()
    score_text = pygame.font.Font(None, 50).render(f"{t['best']}: {hs}", True, HIGHLIGHT_COLOR)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 180))
    return [Button(t['back'], 220, 380, 200, 50, (100, 100, 255), a['back'], s)]

def cycle_speed(st): st['speed'] = [10, 15, 20, 25, 30, 35][([10, 15, 20, 25, 30, 35].index(st['speed']) + 1) % 6]
def cycle_diff(st): st['difficulty'] = ['Easy', 'Normal', 'Hard'][(['Easy', 'Normal', 'Hard'].index(st['difficulty']) + 1) % 3]
def toggle_snd(st): st['sound'] = not st['sound']
def cycle_lng(st): st['lang'] = ['ru', 'en', 'tg'][(['ru', 'en', 'tg'].index(st['lang']) + 1) % 3]
def cycle_snk(st): st['snake_color_idx'] = (st['snake_color_idx'] + 1) % len(SNAKE_COLORS)
def cycle_apl(st): st['apple_color_idx'] = (st['apple_color_idx'] + 1) % len(APPLE_COLORS)
def cycle_shp(st): st['apple_shape_idx'] = (st['apple_shape_idx'] + 1) % len(APPLE_SHAPES)

def show_menu(screen, clock):
    """Меню."""
    st = {'speed': 20, 'difficulty': 'Normal', 'sound': True, 'lang': 'ru', 'snake_color_idx': 0, 'apple_color_idx': 0, 'apple_shape_idx': 0}
    try: s = pygame.mixer.Sound('click.wav')
    except: s = None
    curr = ['main']
    run = [True]
    
    a = {
        'play': lambda: run.__setitem__(0, False),
        'exit': lambda: sys.exit(),
        'settings': lambda: curr.__setitem__(0, 'settings'),
        'records': lambda: curr.__setitem__(0, 'records'),
        'back': lambda: curr.__setitem__(0, 'main'),
        'speed': lambda: cycle_speed(st),
        'diff': lambda: cycle_diff(st),
        'sound': lambda: toggle_snd(st),
        'lang': lambda: cycle_lng(st),
        'sc': lambda: cycle_snk(st),
        'ac': lambda: cycle_apl(st),
        'ash': lambda: cycle_shp(st),
    }

    while run[0]:
        t = translations[st['lang']]
        if curr[0] == 'main': b = draw_main_menu(screen, t, s, a)
        elif curr[0] == 'settings': b = draw_settings_menu(screen, t, st, s, a)
        else: b = draw_records_menu(screen, t, s, a)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                for btn in b: btn.check_click(e.pos)
        for btn in b: btn.draw(screen)
        pygame.display.flip()
        clock.tick(30)
    return st

# --- ИГРА (МАКСИМАЛЬНО РАЗБИТО) ---
def handle_input(sn):
    """Ввод."""
    for e in pygame.event.get():
        if e.type == pygame.QUIT: sys.exit()
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_UP and sn.direction != DOWN: sn.next_direction = UP
            elif e.key == pygame.K_DOWN and sn.direction != UP: sn.next_direction = DOWN
            elif e.key == pygame.K_LEFT and sn.direction != RIGHT: sn.next_direction = LEFT
            elif e.key == pygame.K_RIGHT and sn.direction != LEFT: sn.next_direction = RIGHT

def check_col(sn, obs):
    """Коллизии."""
    hx, hy = sn.get_head_position()
    dx, dy = sn.direction
    nh = ((hx + dx * GRID_SIZE) % SCREEN_WIDTH, (hy + dy * GRID_SIZE) % SCREEN_HEIGHT)
    return nh not in sn.positions[:-1] and nh not in [o.position for o in obs]

def draw_game(screen, sn, ap, obs, gld, sc, hs, t):
    """Отрисовка."""
    screen.fill(BOARD_BACKGROUND_COLOR)
    for o in obs: o.draw(screen)
    ap.draw(screen)
    if gld: gld.draw(screen)
    sn.draw(screen)
    f = pygame.font.Font(None, 30)
    screen.blit(f.render(f"{t['score']}: {sc}", True, TEXT_COLOR), (10, 10))
    screen.blit(f.render(f"{t['best']}: {hs}", True, HIGHLIGHT_COLOR), (SCREEN_WIDTH - 150, 10))

def main():
    """Игра."""
    pygame.init()
    try:
        pygame.mixer.init()
        eat = pygame.mixer.Sound('eat.wav')
        crash = pygame.mixer.Sound('crash.wav')
    except: eat = crash = None

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Продвинутая Змейка')
    clock = pygame.time.Clock()
    st = show_menu(screen, clock)
    t = translations[st['lang']]
    sc = 0
    hs = load_highscore()
    obs = [Obstacle((random.randint(0, GRID_WIDTH - 1) * GRID_SIZE, random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE)) for _ in range(10 if st['difficulty'] == 'Normal' else 20)]
    sn = Snake(color=SNAKE_COLORS[st['snake_color_idx']])
    ap = Apple(color=APPLE_COLORS[st['apple_color_idx']], shape=APPLE_SHAPES[st['apple_shape_idx']])
    ap.randomize_position(obs, sn.positions)
    gld = None
    run = True

    while run:
        handle_input(sn)
        sn.update_direction()
        if check_col(sn, obs):
            sn.move()
            if sn.get_head_position() == ap.position:
                sn.length += 1
                ap.randomize_position(obs, sn.positions)
                if eat and st['sound']: eat.play()
                sc += 10
                if random.random() < 0.2 and gld is None:
                    gld = GoldenApple(shape=APPLE_SHAPES[st['apple_shape_idx']])
                    gld.randomize_position(obs, sn.positions)
            if gld:
                if not gld.update(): gld = None
                elif sn.get_head_position() == gld.position:
                    sn.length += 3
                    sc += 30
                    gld = None
                    if eat and st['sound']: eat.play()
        else:
            if crash and st['sound']: crash.play()
            if sc > hs:
                hs = sc
                save_highscore(hs)
            sn.reset()
            ap.randomize_position(obs, sn.positions)
            gld = None
            sc = 0
        draw_game(screen, sn, ap, obs, gld, sc, hs, t)
        pygame.display.update()
        clock.tick(st['speed'])
    pygame.quit()

if __name__ == '__main__':
    main()
