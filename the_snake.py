from random import choice, randint

import pygame


# Инициализация PyGame:
pygame.init()

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
DIRECT = (UP, DOWN, LEFT, RIGHT)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


def handle_keys(game_object):
    """Функция обработки действий пользователя.
    Квадратик X -> Quit -> выход из игры.
    Стрелки на клавиатуре - изменение направления движения змейки.
    """
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


class GameObject:
    """Родительский класс. Задаются атрибуты:
    position, как центральная точка экрана и
    body_color. как цвет объекта (определяется в
    дочерних классах).
    """

    def __init__(self, body_color=(0, 0, 0)):
        self.position = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        self.body_color = body_color

    def draw(self):
        """Абстрактный метод, который переопределяется
        в дочерних классах. Этот метод должен определять,
        как объект будет отрисовываться на экране.
        """
        pass


class Snake(GameObject):
    """Наследуется от GameObject. Змейка — это список списков из координат,
    каждый элемент которого - отдельный квадратик тела змейки.
    Атрибуты и методы класса обеспечивают логику движения, отрисовку,
    обработку событий и другие аспекты поведения змейки в игре.
    Начало движения вправо из центра экрана. Цвет тела зеленый.
    """

    def __init__(self, body_color=(0, 255, 0)):
        super().__init__(body_color)
        self.positions = [self.position]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Метод возвращает позицию головы змейки
        (первый элемент в списке positions.
        """
        head_position = self.positions[0]
        return head_position

    def update_direction(self):
        """Метод обновления направления после нажатия игроком
        на кнопку c соответствующей стрелкой.
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Метод обновляет позицию змейки (список координат),
        добавляя новую 'голову' в начало списка positions и удаляя
        последний элемент, если длина змейки не увеличилась.
        Применяется обработка краев экрана: выход змейки c противоположной
        стороны при достижении края экрана.
        """
        old_x, old_y = self.get_head_position()
        dx = self.direction[0] * GRID_SIZE
        dy = self.direction[1] * GRID_SIZE
        new_x = (old_x + dx) % SCREEN_WIDTH
        new_y = (old_y + dy) % SCREEN_HEIGHT
        self.new_position = [new_x, new_y]
        if self.new_position in self.positions[1:]:
            self.reset()
        self.positions.insert(0, self.new_position)
        self.last = self.positions[-1]
        if len(self.positions) > self.length:
            self.positions.pop()

    def reset(self):
        """Сбрасывает змейку в начальное состояние после столкновения
        c собой и задает ей случайное направление движения.
        """
        self.length = 1
        self.positions.clear()
        self.new_position = self.position
        self.next_direction = None
        self.direction = choice(DIRECT)
        screen.fill(BOARD_BACKGROUND_COLOR)

    def draw(self, surface):
        """Отрисовывает змейку на экране, затирая след.
        Использует библиотеку pygame.
        """
        for position in self.positions[:-1]:
            rect = (
                pygame.Rect((position[0], position[1]), (GRID_SIZE, GRID_SIZE))
            )
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)

    # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, head_rect)
        pygame.draw.rect(surface, BORDER_COLOR, head_rect, 1)

    # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(
                (self.last[0], self.last[1]),
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)


class Apple(GameObject):
    """Наследуется от GameObject, описывает яблоко и действия c ним.
    Яблоко красного цвета отображается в случайных клетках игрового поля.
    """

    def __init__(self, body_color=(255, 0, 0)):
        super().__init__(body_color)
        self.randomize_position()

    def randomize_position(self):
        """Метод устанавливает случайное положение яблока на игровом поле.
        Задаёт атрибуту position новое значение. Координаты выбираются так,
        чтобы яблоко оказалось в пределах игрового поля.
        """
        self.position = (randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                         randint(0, GRID_HEIGHT - 1) * GRID_SIZE)

    # Метод draw класса Apple
    def draw(self, surface):
        """Метод отрисовывает яблоко на игровой поверхности"""
        rect = pygame.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


def main():
    """Основной игровой цикл.
    Создаются экземпляров классов Snake и Apple.
    B бесконечном цикле:
    обрабатываются события клавиш при помощи функции handle_keys;
    обновляется направление движения змейки при помощи метода update_direction;
    двигается змейка при помощи метода move;
    проверяется, если змейка съела яблоко, то +1 к длине змейки и новое яблоко;
    отрисовываем змейку и яблоко, используя методы draw;
    обновляем экран при помощи метода pygame.display.update.
    """
    apple = Apple()
    snake = Snake()
    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        if snake.new_position == list(apple.position):
            snake.length += 1
            apple.randomize_position()
        apple.draw(screen)
        snake.draw(screen)
        pygame.display.update()


if __name__ == '__main__':
    main()
