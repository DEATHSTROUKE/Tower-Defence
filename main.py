from copy import deepcopy
import sys
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLabel
from PyQt5.QtWidgets import QLineEdit, QMainWindow
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5 import uic
from PyQt5.QtGui import QPalette, QImage, QBrush, QPixmap, QIcon
import pygame as pg
import os
from time import time, sleep
import math


# Menu

class Menu(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('menu.ui', self)
        self.setFixedSize(1300, 900)
        self.setWindowIcon(QIcon('data/Tiles/171.png'))
        self.setWindowTitle('Tower Defence')
        self.update_bg()
        self.start()

    def keyPressEvent(self, event):
        '''Hot keys'''
        if event.key() == Qt.Key_Escape:
            self.close()

    def start(self):
        self.scroll1.takeWidget()
        self.newForm = Start(self)
        self.scroll1.setWidget(self.newForm)

    def choose_lvl(self):
        self.scroll1.takeWidget()
        self.newForm = Levels(self)
        self.scroll1.setWidget(self.newForm)

    def help(self):
        self.scroll1.takeWidget()
        self.newForm = Help(self)
        self.scroll1.setWidget(self.newForm)

    def settings(self):
        self.scroll1.takeWidget()
        self.newForm = Settings(self)
        self.scroll1.setWidget(self.newForm)

    def update_bg(self):
        self.palette = QPalette()
        self.im = QImage('data/grass.svg')
        self.im = self.im.scaledToWidth(self.width())
        self.im = self.im.scaledToHeight(self.height())
        self.palette.setBrush(QPalette.Background, QBrush(self.im))
        self.setPalette(self.palette)


class Start(QWidget):
    def __init__(self, main):
        super().__init__()
        uic.loadUi('start_screen.ui', self)
        self.main = main
        self.play.clicked.connect(self.play1)
        self.help.clicked.connect(self.help1)
        self.settings.clicked.connect(self.settings1)

    def play1(self):
        self.main.choose_lvl()

    def settings1(self):
        self.main.settings()

    def help1(self):
        self.main.help()


class Levels(QWidget):
    def __init__(self, main):
        super().__init__()
        uic.loadUi('levels.ui', self)
        self.main = main
        self.home1.clicked.connect(self.home)
        for i in range(1, 6):
            item = QListWidgetItem(self.lw)
            lvl = Level(self.main, f'{i} level', str(1), i)
            self.lw.addItem(item)
            self.lw.setItemWidget(item, lvl)
            item.setSizeHint(lvl.size())

    def home(self):
        self.main.start()


class Level(QWidget):
    def __init__(self, main, title, diff, number):
        super().__init__()
        uic.loadUi('lvl.ui', self)
        self.main = main
        self.number = number
        # self.title.setText(title)
        self.diff.setText(self.diff.text() + diff)
        self.start.clicked.connect(self.start_game)

    def start_game(self):
        print(f'Game have been started. Level {self.number}')
        self.main.hide()
        start_level(self.number)


class Help(QWidget):
    def __init__(self, main):
        super().__init__()
        uic.loadUi('help.ui', self)
        self.main = main
        self.home1.clicked.connect(self.home)

    def home(self):
        self.main.start()


class Settings(QWidget):
    def __init__(self, main):
        super().__init__()
        uic.loadUi('settings.ui', self)
        self.main = main
        self.is_sound = True
        self.home1.clicked.connect(self.home)
        self.sound.clicked.connect(self.change)

    def home(self):
        self.main.start()

    def change(self):
        if self.is_sound:
            self.is_sound = False
            self.sound.setIcon(QIcon('data/nosound.png'))
        else:
            self.is_sound = True
            self.sound.setIcon(QIcon('data/sound.png'))


# Pygame
pg.init()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pg.image.load(fullname)
    if colorkey is not None:
        image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# groups
all_sprites = pg.sprite.Group()
tiles_group = pg.sprite.Group()
decors_group = pg.sprite.Group()
mobs_group = pg.sprite.Group()
towers_group = pg.sprite.Group()
obj_group = pg.sprite.Group()
pause_group = pg.sprite.Group()
tower_place_group = pg.sprite.Group()
tower_menu_group = pg.sprite.Group()
money_group = pg.sprite.Group()
tower_base_group = pg.sprite.Group()
upgrade_group = pg.sprite.Group()
sell_group = pg.sprite.Group()
bullet_group = pg.sprite.Group()
dead_group = pg.sprite.Group()

# constant
MONEY = 0
LIFES = 0
LEVEL = 0
CURRENT_WAVE = 0
WAVES = 1
FPS = 30
MOD = 1

WIDTH, HEIGHT = 20, 13
images = {}
way = []
waves = []
tile_size = 64
chosen_tower, chosen_tower_base = None, None


class Tile(pg.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = images[tile_type]
        self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)


class Decor(pg.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        if tile_type == '80':
            super().__init__(tower_place_group, all_sprites)
        else:
            super().__init__(decors_group, all_sprites)
        self.image = images[tile_type]
        self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)


class Money(pg.sprite.Sprite):
    def __init__(self, money, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        tile_type = '197'
        if money == 0:
            tile_type = '197'
        elif money == 1:
            tile_type = '198'
        elif money == 2:
            tile_type = '199'
        elif money == 3:
            tile_type = '200'
        elif money == 4:
            tile_type = '201'
        elif money == 5:
            tile_type = '202'
        elif money == 6:
            tile_type = '203'
        elif money == 7:
            tile_type = '204'
        elif money == 8:
            tile_type = '205'
        elif money == 9:
            tile_type = '206'

        self.image = images[tile_type]
        self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)


# Mobs

class Mob(pg.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, health, speed):
        super().__init__(mobs_group, all_sprites)
        self.image = images[tile_type]
        self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)
        self.health = self.max_health = health
        self.speed = speed

        # controle points
        self.dest = deepcopy([i[:2] for i in way])
        for i in range(len(self.dest)):
            self.dest[i][0] *= 64
            self.dest[i][1] *= 64
        self.visited = 1
        self.pos = [pos_x * tile_size, pos_y * tile_size]

        self.last = time()
        self.dt = 0
        self.healthbar = None

    def get_damage(self, damage):
        self.health -= damage

    def is_alive(self):
        return self.health > 0

    def get_center(self):
        return self.pos[0] + tile_size // 2, self.pos[1] + tile_size // 2

    def dead(self):
        self.image = images['114']
        self.speed = 0
        self.kill()
        dead_group.add(self)
        self.dead_time = time()

    def is_dead(self):
        return self.health <= 0

    def has_destination(self):
        return self.visited < len(self.dest)

    def move(self):
        global LIFES
        steps = self.speed * self.dt
        while steps > 0 and self.has_destination():
            x, y = self.pos
            dest = self.dest[self.visited]
            if self.pos == dest:
                self.visited += 1
                try:
                    self.angle = way[self.visited][2]
                    self.image = pg.transform.rotate(self.image, self.angle)
                except BaseException:
                    self.kill()
                continue
            sign_x = -1
            if dest[0] > x:
                sign_x = 1
            elif dest[0] == x:
                sign_x = 0
            sign_y = -1
            if dest[1] > y:
                sign_y = 1
            elif dest[1] == y:
                sign_y = 0

            x += sign_x
            y += sign_y
            self.pos = [x, y]
            self.rect.x = self.pos[0]
            self.rect.y = self.pos[1]
            steps -= 1
        if not self.has_destination():
            self.kill()
            LIFES -= 1

    def update(self):
        t = time()
        self.dt = t - self.last
        self.last = t

        if self.health <= 0:
            self.dead()
        self.move()


class Ball(Mob):
    def __init__(self, level, pos_x, pos_y, angle):
        tile_type = ''
        health = 100
        speed = 20
        if level == 1:
            health = 100
            speed = 20
            tile_type = '193'
        elif level == 2:
            health = 200
            speed = 50
            tile_type = '195'
        elif level == 3:
            health = 400
            speed = 100
            tile_type = '194'
        elif level == 4:
            health = 800
            speed = 300
            tile_type = '196'
        health *= MOD
        super().__init__(tile_type, pos_x, pos_y, health, speed)
        self.image = pg.transform.rotate(self.image, angle)


class Frog(Mob):
    def __init__(self, level, pos_x, pos_y, angle):
        tile_type = ''
        health = 200
        speed = 10
        if level == 1:
            tile_type = '163'
            health = 200
            speed = 10
        elif level == 2:
            tile_type = '165'
            health = 500
            speed = 20
        elif level == 3:
            tile_type = '166'
            health = 1000
            speed = 50
        elif level == 4:
            tile_type = '164'
            health = 2000
            speed = 100
        health *= MOD
        super().__init__(tile_type, pos_x, pos_y, health, speed)
        self.image = pg.transform.rotate(self.image, angle)


class Tank(Mob):
    def __init__(self, level, pos_x, pos_y, angle):
        tile_type = ''
        health = 2000
        speed = 20
        if level == 1:
            tile_type = '188'
            health = 2000
            speed = 20
        elif level == 2:
            tile_type = '189'
            health = 5000
            speed = 50
        health *= MOD
        super().__init__(tile_type, pos_x, pos_y, health, speed)
        self.image = pg.transform.rotate(self.image, 180)


class Plain(Mob):
    def __init__(self, level):
        tile_type = ''
        health = 200
        speed = 50
        if level == 1:
            tile_type = '190'
            health = 200
            speed = 50
        elif level == 2:
            tile_type = '192'
            health = 500
            speed = 100
        health *= MOD
        super().__init__(tile_type, -0.5, HEIGHT // 2, health, speed)

    def move(self):
        global LIFES
        steps = self.speed * self.dt
        while steps > 0 and self.pos[0] < (WIDTH + 2) * tile_size:
            x, y = self.pos
            sign_x = 1
            x += sign_x
            self.pos = [x, y]
            self.rect.x = self.pos[0]
            self.rect.y = self.pos[1]
            steps -= 1
        if not self.pos[0] < (WIDTH + 2) * tile_size:
            self.kill()
            LIFES -= 1

    def update(self):
        t = time()
        self.dt = t - self.last
        self.last = t

        if self.health <= 0:
            self.dead()
        self.move()


# Towers

class Tower(pg.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, damage, rng, speed, cost_up, sell):
        super().__init__(towers_group, all_sprites)
        self.image = images[tile_type]
        self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)
        self.pos = pos_x * tile_size, pos_y * tile_size
        self.angle = 0
        self.cost = cost_up
        self.sell = sell
        self.range = rng
        self.active = False
        self.level = 1
        self.speed_rot = 300
        self.speed = speed

        self.bullet_type = Bullet
        self.bullet_damage = damage
        self.bullet_speed = 300

        self.last_attack = self.speed_rot
        self.last_angle = 0
        self.dt = 0

        self.target = None
        self.bullets = pg.sprite.Group()

    def get_cost(self):
        return self.cost

    def get_range(self):
        return self.range[self.level]

    def is_active(self):
        return self.active

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def get_center(self):
        return self.pos[0] + tile_size // 2, self.pos[1] + tile_size // 2

    def in_range(self, pos):
        px, py = pos
        cx, cy = self.get_center()
        distance = math.sqrt((px - cx) ** 2 + (py - cy) ** 2)
        return distance <= self.range

    def dist(self, pos):
        return math.sqrt((self.get_center()[0] - pos[0]) ** 2 +
                         (self.get_center()[1] - pos[1]) ** 2)

    def can_attack(self):
        return time() - self.last_attack >= 1.0 / self.speed

    def attack(self, target):
        b = self.bullet_type(self.get_center()[0], self.get_center()[1],
                             self.bullet_damage, self.bullet_speed)
        b.set_target(target)
        self.bullets.add(b)
        self.last_attack = time()

    def turn(self):
        x, y = self.target.get_center()
        rel_x, rel_y = x - self.rect.x, y - self.rect.y
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        print(angle)
        self.image = pg.transform.rotate(self.image, int(angle))
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, screen):
        # self.bullets.draw(screen)
        if self.target is not None and self.target.is_dead():
            self.target = None
        if self.can_attack():
            if self.target is not None and self.in_range(self.target.get_center()):
                self.attack(self.target)
                t = time()
                self.dt = t - self.last_angle
                self.last_angle = t
                # self.image = pg.transform.rotate(self.image, 1)
                # if self.dt > 0.05:
                #     self.turn()
            else:
                min_s = 99999
                for mob in mobs_group:
                    if self.in_range(mob.get_center()) and self.dist(mob.get_center()) < min_s:
                        self.target = mob
                        min_s = self.dist(mob.get_center())


class TowerBase(pg.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tower_base_group, all_sprites)
        self.image = images[tile_type]
        self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)
        self.level = 1

    def upgrade(self):
        self.level += 1
        if self.level == 2:
            self.image = images['93']
        elif self.level == 3:
            self.image = images['90']


class MashineGun(Tower):
    def __init__(self, pos_x, pos_y):
        super().__init__('300', pos_x, pos_y, 50, 300, 20, 8, 6)
        self.level = 1
        self.bullet_type = MGBullet

    def upgrade(self):
        self.level += 1
        if self.level == 2:
            self.image = images['301']
        elif self.level == 3:
            self.image = images['302']


class SmallGun(Tower):
    def __init__(self, pos_x, pos_y):
        super().__init__('117', pos_x, pos_y, 200, 200, 1, 30, 15)
        self.level = 1
        self.bullet_type = SmallBullet

    def upgrade(self):
        self.level += 1
        if self.level == 2:
            pass
        elif self.level == 3:
            self.image = images['142']


class Rocket(Tower):
    def __init__(self, pos_x, pos_y):
        super().__init__('118', pos_x, pos_y, 300, 300, 1, 40, 20)
        self.level = 1
        self.bullet_type = SmallRocketBullet

    def upgrade(self):
        self.level += 1
        if self.level == 2:
            pass
        elif self.level == 3:
            pass


class PVO(Tower):
    def __init__(self, pos_x, pos_y):
        super().__init__('120', pos_x, pos_y, 500, 1000, 1, 120, 80)
        self.level = 1
        self.bullet_type = PVOBullet

    def upgrade(self):
        self.level += 1
        if self.level == 2:
            pass
        if self.level == 3:
            self.image = images['119']


class BigGun(Tower):
    def __init__(self, pos_x, pos_y):
        super().__init__('167', pos_x, pos_y, 1000, 1000, 1, 200, 100)
        self.level = 1
        self.bullet_type = BigBullet

    def upgrade(self):
        self.level += 1
        if self.level == 2:
            pass
        if self.level == 3:
            self.image = images['168']


# Bullets

class Bullet(pg.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, damage, speed):
        super().__init__(bullet_group, all_sprites)
        self.damage = damage
        self.speed = speed
        self.target = None
        self.image = images[tile_type]
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.mask = pg.mask.from_surface(self.image)
        self.pos = pos_x, pos_y

        # frame rate independent data
        self.last_frame = time()
        self.dt = 0

    def get_damage(self):
        return self.damage

    def set_target(self, target):
        self.target = target

    def get_center(self):
        return self.pos[0] + tile_size // 2, self.pos[1] + tile_size // 2

    def move(self):
        if self.target is None:
            return

        # move based on center points
        dest = self.target.get_center()
        curr = self.get_center()

        direction = (dest[0] - curr[0], dest[1] - curr[1])
        x = direction[0] ** 2
        y = direction[1] ** 2

        # normalize the direction vector
        mag = math.sqrt(float(x) + float(y))
        try:
            normalized = (direction[0] / mag, direction[1] / mag)
        except ZeroDivisionError:
            normalized = (0, 0)
        dist = min(self.speed * self.dt, math.sqrt(x + y))
        self.pos = (self.pos[0] + dist * normalized[0], self.pos[1] + dist * normalized[1])
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]

    def update(self):
        t = time()
        self.dt = t - self.last_frame
        self.last_frame = t
        self.move()
        if self.target is None or self.target.is_dead():
            self.kill()
        # elif pg.sprite.collide_mask(self, self.target):
        elif pg.sprite.collide_mask(self, self.target):
            self.target.get_damage(self.get_damage())
            if self.target.is_dead():
                self.kill()


class MGBullet(Bullet):
    def __init__(self, pos_x, pos_y, damage, speed):
        super().__init__('303', pos_x, pos_y, damage, speed)


class SmallBullet(Bullet):
    def __init__(self, pos_x, pos_y, damage, speed):
        super().__init__('218', pos_x, pos_y, damage, speed)


class SmallRocketBullet(Bullet):
    def __init__(self, pos_x, pos_y, damage, speed):
        super().__init__('170', pos_x, pos_y, damage, speed)


class PVOBullet(Bullet):
    def __init__(self, pos_x, pos_y, damage, speed):
        super().__init__('171', pos_x, pos_y, damage, speed)


class BigBullet(Bullet):
    def __init__(self, pos_x, pos_y, damage, speed):
        super().__init__('219', pos_x, pos_y, damage, speed)


# Tower Menu

class TowerMenu(pg.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, angle, tower_type):
        super().__init__(tower_menu_group, all_sprites)
        self.image = images[tile_type]
        self.image = pg.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)
        self.type = tower_type


class Upgrade(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(upgrade_group, all_sprites)
        self.image = load_image('upgrade.png')
        self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)
        self.activ = False

    def update(self, *args):
        global chosen_tower, chosen_tower_base
        self.activ = args[0]
        if self.activ:
            self.image = load_image('upgrade_clicked.png')
        else:
            self.image = load_image('upgrade.png')
            chosen_tower, chosen_tower_base = None, None


class Sell(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(sell_group, all_sprites)
        self.image = load_image('sell.png')
        self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)
        self.activ = False

    def update(self, *args):
        self.activ = args[0]
        if self.activ:
            self.image = load_image('sell_clicked.png')
        else:
            self.image = load_image('sell.png')


def load_level(fname):
    """Loads level from file"""
    global MONEY, LIFES, WIDTH, HEIGHT, way, waves, WAVES, MOD
    fname = "data/Maps/" + fname
    with open(fname, 'r') as mapf:
        level_map = []
        decor_map = []
        for i, line in enumerate(mapf):
            if i == 0:
                MONEY = int(line.strip())
            elif i == 1:
                m = line.split()
                LIFES = int(m[0])
                MOD = float(m[1])
            elif i == 2:
                t = line.split()
                WIDTH, HEIGHT = int(t[0]), int(t[1])
            elif 3 <= i < HEIGHT + 3:
                level_map.append(line.split())
            elif i == HEIGHT + 3:
                h = int(line.strip())
            elif HEIGHT + 3 < i < HEIGHT + h + 3:
                decor_map.append(line.split())
            elif i == HEIGHT + h + 3:
                corners = int(line.strip())
            elif HEIGHT + h + 3 < i < HEIGHT + h + 3 + corners:
                way.append([float(j) for j in line.split()])
            elif i == HEIGHT + h + 3 + corners:
                w = int(line.strip())
                WAVES = w - 1
            elif HEIGHT + h + 3 + corners < i < HEIGHT + h + 3 + corners + w:
                wave1 = line.split()
                wave2 = []
                for j in range(2, len(wave1), 3):
                    sp = [int(wave1[j]), wave1[j - 1], int(wave1[j - 2])]
                    wave2.append(sp)
                waves.append(wave2)
        print(waves)
    return level_map, decor_map


def generate_tiles():
    """Makes dict with tiles and other objects"""
    global images
    for i in range(1, 304):
        try:
            images[str(i)] = load_image(f'Tiles/{str(i)}.png')
        except BaseException:
            try:
                images[str(i)] = load_image(f'Decor/{str(i)}.png')
            except BaseException:
                try:
                    images[str(i)] = load_image(f'Mobs/{str(i)}.png')
                except BaseException:
                    try:
                        images[str(i)] = load_image(f'Towers/{str(i)}.png')
                    except BaseException:
                        pass


def generate_level(level):
    """Makes level"""
    for x in range(len(level)):
        for y in range(len(level[x])):
            Tile(level[x][y], y, x)


def generate_decor(level):
    """Makes decorations on level"""
    for x in range(len(level)):
        for y in range(len(level[x])):
            if level[x][y] != '0':
                Decor(level[x][y], y, x)


def other_obj():
    """Makes other sprites on level such as: pause or score"""
    pause = pg.sprite.Sprite()
    pause.image = load_image('pause.png')
    pause.rect = pause.image.get_rect()
    obj_group.add(pause)
    pause.rect.x = 1210
    pause.rect.y = 20
    Upgrade(8, 10)
    Sell(10.5, 10)


def pause_obj():
    """Makes other sprites in pause menu"""
    pause = pg.sprite.Sprite()
    pause.image = load_image('paused.png')
    pause.rect = pause.image.get_rect()
    pause_group.add(pause)
    pause.rect.x = 390
    pause.rect.y = 200


def towers_menu():
    """Makes menu of towers"""
    TowerMenu('300', 12, 10, 270, 1)
    TowerMenu('117', 13.5, 10, 0, 2)
    TowerMenu('118', 15, 10, 0, 3)
    TowerMenu('120', 16.5, 10, 0, 4)
    TowerMenu('167', 18, 10, 0, 5)


def get_cell(mouse_pos):
    """Get coords of cell"""
    for x in range(WIDTH):
        for y in range(HEIGHT):
            if x * tile_size <= mouse_pos[0] <= (x + 1) * tile_size and \
                    y * tile_size <= mouse_pos[1] <= (y + 1) * tile_size:
                return x, y
    return None


def generate_money():
    """Makes start money"""
    global money_group
    money_group = pg.sprite.Group()
    dol = pg.sprite.Sprite()
    dol.image = images['209']
    dol.rect = dol.image.get_rect()
    money_group.add(dol)
    dol.rect.x = 0
    dol.rect.y = 0
    x, y = 0, 0
    money = str(MONEY)
    for i in money:
        x += 0.5
        Money(int(i), x, y)


def generate_prices(screen):
    """Makes prices for towers"""
    font = pg.font.Font(None, 30)
    # upgrade
    screen.blit(font.render('$10', 1, (0, 0, 0)), (512, 700))
    # sell
    screen.blit(font.render('$10', 1, (0, 0, 0)), (672, 700))
    # towers
    screen.blit(font.render('$10', 1, (0, 0, 0)), (784, 700))
    screen.blit(font.render('$30', 1, (0, 0, 0)), (880, 700))
    screen.blit(font.render('$50', 1, (0, 0, 0)), (976, 700))
    screen.blit(font.render('$150', 1, (0, 0, 0)), (1072, 700))
    screen.blit(font.render('$200', 1, (0, 0, 0)), (1168, 700))


def generate_wave():
    """Makes waves of enemies"""
    global waves, dead_group
    dead_group = pg.sprite.Group()
    if waves:
        for i in mobs_group:
            i.kill()
            pg.display.flip()
        cur_wave = waves[0]
        waves.pop(0)
        for mob in cur_wave:
            for k in range(mob[0]):
                if mob[1] == 'ball':
                    Ball(mob[2], way[0][0], way[0][1], way[0][2])
                    if mob[2] == 1:
                        sleep(1)
                    elif mob[2] == 2:
                        sleep(0.5)
                    elif mob[2] == 3:
                        sleep(0.3)
                    else:
                        sleep(0.1)
                elif mob[1] == 'frog':
                    Frog(mob[2], way[0][0], way[0][1], way[0][2])
                    if mob[2] == 1:
                        sleep(2)
                    elif mob[2] == 2:
                        sleep(1)
                    elif mob[2] == 3:
                        sleep(0.5)
                    else:
                        sleep(0.2)
                elif mob[1] == 'tank':
                    Tank(mob[2], way[0][0], way[0][1], way[0][2])
                    if mob[2] == 1:
                        sleep(4)
                    elif mob[2] == 2:
                        sleep(2)
                elif mob[1] == 'plain':
                    Plain(mob[2])
                    if mob[2] == 1:
                        sleep(1)
                    elif mob[2] == 2:
                        sleep(0.5)
    else:
        game_over()


def generate_lifes(screen):
    """Shows your remaining lifes"""
    font = pg.font.Font(None, 50)
    screen.blit(font.render(f'LIFE: {LIFES}', 1, (255, 255, 255)), (832, 16))


def show_waves(screen):
    """Shows current wave and how many is remaining"""
    font = pg.font.Font(None, 50)
    screen.blit(font.render(f'{CURRENT_WAVE}/{WAVES}', 1, (255, 255, 255)), (448, 16))


def start_level(level):
    global LEVEL
    LEVEL = level
    main()


def game_over():
    if LIFES > 0:
        pass
    else:
        pass


def main():
    """Main game function"""
    global chosen_tower, chosen_tower_base, CURRENT_WAVE
    size = (pg.display.Info().current_w, pg.display.Info().current_h)
    screen = pg.display.set_mode((1280, 720))
    fullscreen = False
    screen.fill(pg.Color('black'))

    # make dict of tiles and other objects
    generate_tiles()
    # generate objects and groups on the main screen
    level, decor_map = load_level('map1.txt')
    generate_level(level)
    generate_decor(decor_map)
    other_obj()
    pause_obj()
    towers_menu()
    generate_money()
    pg.display.flip()

    # create flags
    tower_menu_clicked = False
    tower_type = 0

    # test
    TowerBase('92', 4, 5)
    Rocket(4, 5)

    clock = pg.time.Clock()
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                '''Exit to menu'''
                running = False

            if pg.key.get_pressed()[pg.K_ESCAPE]:
                '''Pause'''
                pg.quit()
                sys.exit()

            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if 1210 < event.pos[0] < 1260 and 0 < event.pos[1] < 40:
                        # Pause
                        flag = True
                        while flag:
                            pause_group.draw(screen)
                            pg.display.flip()
                            for ev in pg.event.get():
                                if pg.key.get_pressed()[pg.K_ESCAPE]:
                                    flag = False
                                    break
                                if ev.type == pg.MOUSEBUTTONDOWN:
                                    flag = False
                                    break
                    else:
                        x1, y1 = event.pos
                        # choose tower (clicked on tower menu)
                        for tower in tower_menu_group:
                            if tower.rect.collidepoint(x1, y1) and not tower_menu_clicked:
                                tower_menu_clicked = True
                                tower_type = tower.type
                                break
                        else:
                            # clicked on field with chosen tower
                            if tower_menu_clicked:
                                # you can`t put tower on place with other tower
                                for i in towers_group:
                                    if i.rect.collidepoint(x1, y1):
                                        break
                                else:
                                    for t in tower_place_group:
                                        if t.rect.collidepoint(x1, y1):
                                            x2, y2 = get_cell(event.pos)
                                            TowerBase('92', x2, y2)
                                            if tower_type == 1:
                                                MashineGun(x2, y2)
                                            elif tower_type == 2:
                                                SmallGun(x2, y2)
                                            elif tower_type == 3:
                                                Rocket(x2, y2)
                                            elif tower_type == 4:
                                                PVO(x2, y2)
                                            elif tower_type == 5:
                                                BigGun(x2, y2)
                                            break
                                tower_menu_clicked = False

                        # upgrade and sell
                        # upgrade
                        for up in upgrade_group:
                            if up.rect.collidepoint(x1, y1):
                                if chosen_tower:
                                    chosen_tower.upgrade()
                                    chosen_tower_base.upgrade()
                                    break
                        # sell
                        for se in sell_group:
                            if se.rect.collidepoint(x1, y1):
                                if chosen_tower:
                                    chosen_tower.kill()
                                    chosen_tower_base.kill()
                                    break
                        # choose tower to upgrade or sell
                        for tower in towers_group:
                            if tower.rect.collidepoint(x1, y1):
                                upgrade_group.update(True)
                                sell_group.update(True)
                                chosen_tower = tower
                                for tb in tower_base_group:
                                    if tb.rect.collidepoint(x1, y1):
                                        chosen_tower_base = tb
                                break
                        else:
                            for up in upgrade_group:
                                if up.rect.collidepoint(x1, y1):
                                    break
                            else:
                                upgrade_group.update(False)
                                sell_group.update(False)

            if pg.key.get_pressed()[pg.K_F11]:
                '''Change screen size'''
                if fullscreen:
                    screen = pg.display.set_mode((1280, 720))
                    fullscreen = False
                else:
                    size = (pg.display.Info().current_w, pg.display.Info().current_h)
                    screen = pg.display.set_mode(size, pg.FULLSCREEN)
                    fullscreen = True

        # groups and objects on screen
        tiles_group.draw(screen)
        obj_group.draw(screen)
        decors_group.draw(screen)
        if tower_menu_clicked:
            tower_place_group.draw(screen)
        pg.draw.rect(screen, pg.Color('#66cdaa'), (512, 640, 704, 96)), 768, 640
        # text on the screen
        generate_prices(screen)
        generate_lifes(screen)
        show_waves(screen)

        tower_menu_group.draw(screen)
        tower_base_group.draw(screen)
        towers_group.draw(screen)
        money_group.draw(screen)
        upgrade_group.draw(screen)
        sell_group.draw(screen)
        mobs_group.draw(screen)
        bullet_group.draw(screen)
        dead_group.draw(screen)
        mobs_group.update()
        towers_group.update(screen)
        bullet_group.update()
        pg.display.flip()

        if len(mobs_group) == 0:
            # start wave
            CURRENT_WAVE += 1
            show_waves(screen)
            generate_wave()
        if LIFES <= 0:
            game_over()

    pg.quit()
    # menu()


def menu():
    """Shows menu"""
    # win.show()


if __name__ == '__main__':
    main()
    # app = QApplication(sys.argv)
    # win = Menu()
    # menu()
    # sys.exit(app.exec_())
