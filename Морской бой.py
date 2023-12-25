from random import randint


class Dot:      # класс точек на поле
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):        # сравнивает 2 объекта
        return self.x == other.x and self.y == other.y

    def __repr__(self):             # вывод точек в консоль
        return f"({self.x}, {self.y})"


class BoardException(Exception):    # содержит в себе все классы с исключениями
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):  # исключение для правильного размещения кораблей
    pass


class Ship:     # класс корабля
    def __init__(self, bow, l, o):  # l - длина, o - направление
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):     # список всех точек корабля
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x  # точки носа корабля
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):    # проверка на попадание
        return shot in self.dots


class Board:    # игровая доска
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0  # кол-во подбитых кораблей

        self.field = [["O"] * size for _ in range(size)]    # field атрибут содержит сетку (size * size)

        self.busy = []  # хранятся занятые точки, корабль или куда уже стреляли
        self.ships = []  # список кораблей доски

    def add_ship(self, ship):       # добавляем корабль, если не получается - выбрасываем исключения

        for d in ship.dots:   # проверяет не выходит ли точка и незанята ли
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"  # поставим квадрат
            self.busy.append(d)     # добавим точку в список занятых точек

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):        # метод помечает соседние точки, где не может быть кораблей
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:   # проход по токам соседствующим с кораблём
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)   # добавим точку в список занятых точек и ставим точку

    def __str__(self):  # метод рисует доску
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:    # нужно ли скрывать корабли на доске
            res = res.replace("■", "O")     # заменяем все символы корабля на пустые
        return res

    def out(self, d):       # метод для точки (объекта класса Dot) который возвращает True, если точка выходит
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))  # за пределы поля, иначе False

    def shot(self, d):      # выстрел, если за пределы доски - исключение
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:   # класс игрока (AI и пользователь), передаются доски
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):  # этот метод должен быть у потомков этого класса
        raise NotImplementedError()

    def move(self):  # в бесконечном цикле делаем выстрел
        while True:
            try:
                target = self.ask()  # получаем координаты выстрела от компа или пользователя
                repeat = self.enemy.shot(target)    # если выстрел прошёл нужно ли повторить ход
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:     # класс игры
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()    # создаём доски
        co = self.random_board()
        co.hid = True   # скрываем корабли компьютера

        self.ai = AI(co, pl)    # создаём игроков, передав им доски
        self.us = User(pl, co)

    def random_board(self):     # генерирует случайную доску
        board = None
        while board is None:
            board = self.random_place()
        return board    # возвращаем готовую доску

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]    # длины кораблей
        board = Board(size=self.size)
        attempts = 0    # кол-во попыток поставить корабли
        for l in lens:
            while True:     # пытаемся поставить корабли
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)    # добавление корабля
                    break
                except BoardWrongShipException:     # если не добавился, то повторяем цикл заново
                    pass
        board.begin()   # возвращаем доску, чтобы подготовить её к игре
        return board

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):     # метод с игровым циклом
        num = 0     # номер хода
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()     # нужно ли повторить ход
            if repeat:
                num -= 1    # при повторе хода, чтобы ход остался у того же игрока

            if self.ai.board.count == 7:    # проверка кол-ва поражённых кораблей
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()