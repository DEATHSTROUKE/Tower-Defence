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
import sqlite3
from time import time
from random import choice
import math

# Menu
mode = ''
con = sqlite3.connect('levels_state.db')
cur = con.cursor()


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
        # load levels from bd
        res = list(cur.execute('''SELECT * FROM levels'''))
        files = os.listdir('data/Maps')
        names = [i[1] for i in res]
        for i in files:
            str1 = i.replace('.txt', '')
            if str1[:-1] not in names:
                cur.execute('''INSERT INTO levels(title, difficulty) VALUES(?, ?)''',
                            (str1[:-1], int(str1[-1])))
                con.commit()
        names = [i.replace('.txt', '')[:-1] for i in files]
        for i in res:
            if i[1] not in names:
                cur.execute('''DELETE FROM levels
                    WHERE title = ?''',
                            (i[1],))
                con.commit()
        res = list(cur.execute('''SELECT * FROM levels'''))
        for i in res:
            item = QListWidgetItem(self.lw)
            lvl = Level(self.main, i[1], i[2], i[3], i[4], i[5])
            self.lw.addItem(item)
            self.lw.setItemWidget(item, lvl)
            item.setSizeHint(lvl.size())

    def home(self):
        self.main.start()


class Level(QWidget):
    def __init__(self, main, title, diff, normal, endless, hardcore):
        super().__init__()
        uic.loadUi('lvl.ui', self)
        self.main = main
        self.name = f'{title}{diff}.txt'
        self.dif = diff
        self.title.setPixmap(QPixmap(f'data/{title}.png'))
        if diff == 1:
            self.diff.setPixmap(QPixmap('data/easy.png'))
        elif diff == 2:
            self.diff.setPixmap(QPixmap('data/medium.png'))
        elif diff == 3:
            self.diff.setPixmap(QPixmap('data/onelife.png'))
        if normal == 1:
            self.first.setPixmap(QPixmap('data/star.png'))
        if endless == 1:
            self.second.setPixmap(QPixmap('data/star.png'))
        if hardcore == 1:
            self.third.setPixmap(QPixmap('data/star.png'))

        self.normal.clicked.connect(lambda: self.start_game('n'))
        self.endless.clicked.connect(lambda: self.start_game('e'))
        self.hardcore.clicked.connect(lambda: self.start_game('h'))

    def start_game(self, mod):
        global mode
        if mod == 'n':
            mode = 'normal'
        elif mod == 'e':
            mode = 'endless'
        elif mod == 'h':
            mode = 'hardcore'
        self.main.hide()
        start_level(self.name)


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
screen = None
clock = pg.time.Clock()


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
ground_mobs = pg.sprite.Group()
air_mobs = pg.sprite.Group()
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
end_group = pg.sprite.Group()
shadow_group = pg.sprite.Group()

# constant
MONEY = 0
LIFES = 0
LEVEL = 0
CURRENT_WAVE = 0
WAVES = 1
FPS = 30
MOD = 1
REPLAY = 1
INCREASE = 1.0
TOTAL_INCREASE = 1

WIDTH, HEIGHT = 20, 13
images = {}
way = []
waves = []
waves_res = []
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
        super().__init__(money_group, all_sprites)
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
            tile_type = '203'
        elif money == 6:
            tile_type = '204'
        elif money == 7:
            tile_type = '205'
        elif money == 8:
            tile_type = '206'
        elif money == 9:
            tile_type = '207'

        self.image = images[tile_type]
        self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)


# Healthbar
class HealthBar:
    def __init__(self, pos, max_health, width=tile_size // 2, height=5):
        self.max_health = max_health
        self.pos = pos
        self.current_health = max_health
        self.width = width
        self.height = height
        self.current_width = width
        # self.bg_color = (255, 0, 0)
        # self.color = (0, 255, 0)
        self.bg_color = (0, 0, 0)
        self.color = (255, 0, 0)
        self.place_bar()

    def place_bar(self):
        self.bg = pg.rect.Rect(self.pos, (self.width, self.height))
        self.current = pg.rect.Rect(self.pos, (self.current_width, self.height))

    def update_health(self, value):
        if self.current_health != value:
            self.current_health = value
            perc = float(self.current_health) / self.max_health
            self.current_width = min(self.width, self.width * perc)

    def set_position(self, pos):
        self.pos = pos
        self.place_bar()

    def paint(self, surface):
        pg.draw.rect(surface, self.bg_color, self.bg, 5)
        pg.draw.rect(surface, self.color, self.current)


# Mobs

class Mob(pg.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, health, speed):
        super().__init__(mobs_group, all_sprites)
        self.image = images[tile_type]
        self.orig_image = self.image
        self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)
        self.image = pg.transform.rotate(self.orig_image, way[0][2])
        self.health = self.max_health = health * TOTAL_INCREASE
        self.money = 10
        self.speed = speed
        self.alive = True
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
        self.setup_healthbar()

    def get_damage(self, damage):
        self.health -= damage

    def setup_healthbar(self):
        health_pos = self.pos[0] + 0.5 * tile_size - 0.5 * tile_size // 2, self.pos[1] - 5
        self.healthbar = HealthBar(health_pos, self.max_health)

    def paint_health(self, surface):
        self.healthbar.paint(surface)

    def set_health_pos(self):
        self.healthbar.set_position((self.pos[0] + 0.5 * tile_size - 0.5 * tile_size // 2,
                                     self.pos[1] - 5))

    def get_center(self):
        return self.pos[0] + tile_size // 2, self.pos[1] + tile_size // 2

    def dead(self):
        global MONEY
        self.image = images['114']
        self.speed = 0
        self.health = -100
        self.kill()
        dead_group.add(self)
        self.dead_time = time()
        MONEY += self.money
        generate_money()

    def remove_target(self):
        self.alive = False

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
                    self.angle = way[self.visited - 1][2]
                    self.image = pg.transform.rotate(self.orig_image, self.angle)
                except BaseException:
                    pass
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
            self.remove_target()
            self.kill()
            LIFES -= 1

    def update(self):
        t = time()
        self.dt = t - self.last
        self.last = t
        if self.health <= 0:
            self.dead()
        self.healthbar.update_health(self.health)
        self.set_health_pos()
        self.paint_health(screen)
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
        self.add(ground_mobs)
        self.money = 5 * level ** 2


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
        self.add(ground_mobs)
        self.money = 20 * level


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
        self.image = pg.transform.rotate(self.image, way[0][2])
        self.add(ground_mobs)
        self.money = 100 * level


class Plain(Mob):
    def __init__(self, level, pos_x, pos_y):
        tile_type = ''
        health = 1000
        speed = 50
        if level == 1:
            tile_type = '190'
            health = 1000
            speed = 50
            self.ten = '216'
        elif level == 2:
            tile_type = '192'
            health = 2000
            speed = 100
            self.ten = '217'
        health *= MOD
        super().__init__(tile_type, pos_x, pos_y, health, speed)
        self.add(air_mobs)
        self.money = 100 * level
        self.shadow = pg.sprite.Sprite()
        self.shadow.image = images[self.ten]
        self.shadow.rect = self.shadow.image.get_rect()
        shadow_group.add(self.shadow)
        self.shadow.rect.x = self.pos[0] + 32
        self.shadow.rect.y = self.pos[1] + 32

    def dead(self):
        global MONEY
        self.image = images['114']
        self.speed = 0
        self.health = -100
        self.kill()
        self.shadow.kill()
        dead_group.add(self)
        self.dead_time = time()
        MONEY += self.money
        generate_money()

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
            self.shadow.rect.x = self.pos[0] + 32
            self.shadow.rect.y = self.pos[1] + 64
            steps -= 1
        if not self.pos[0] < (WIDTH + 2) * tile_size:
            self.remove_target()
            self.kill()
            self.shadow.kill()
            LIFES -= 1

    def update(self):
        t = time()
        self.dt = t - self.last
        self.last = t

        if self.health <= 0:
            self.dead()
        self.healthbar.update_health(self.health)
        self.set_health_pos()
        self.paint_health(screen)
        self.move()


# Towers

class Tower(pg.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, damage, rng, speed, cost_up, sell):
        super().__init__(towers_group, all_sprites)
        self.image = images[tile_type]
        self.orig_image = self.image
        self.tile = tile_type
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
        self.bullet_speed = 700
        self.bullet_im = ''
        self.mob_group = mobs_group

        self.last_attack = 0
        self.last_angle = 0
        self.dt = 0

        self.range_im = pg.Surface((self.range * 2, self.range * 2), pg.SRCALPHA)
        self.target = None
        self.bullets = pg.sprite.Group()

    def get_cost(self):
        return self.cost

    def get_range(self):
        return self.range

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

    def draw_range(self):
        pg.draw.circle(self.range_im, (255, 0, 0, 30),
                       (self.range, self.range), self.range)
        screen.blit(self.range_im, (self.get_center()[0] - self.range,
                                    self.get_center()[1] - self.range))

    def can_attack(self):
        return time() - self.last_attack >= 1.0 / self.speed

    def attack(self, target):
        if self.bullet_im:
            b = self.bullet_type(self.pos[0], self.pos[1],
                                 self.bullet_damage, self.bullet_speed, self.bullet_im)
        else:
            b = self.bullet_type(self.pos[0], self.pos[1],
                                 self.bullet_damage, self.bullet_speed)
        b.set_target(target)
        self.bullets.add(b)
        self.last_attack = time()

    def turn(self):
        x, y = self.target.get_center()
        rel_x, rel_y = x - self.rect.x, y - self.rect.y
        angle = 270 + (180 / math.pi) * -math.atan2(rel_y, rel_x)
        self.angle = angle
        # print(angle)
        # print(self.pos[0] + 32 * math.cos(self.angle), self.pos[1] + 32 * math.sin(self.angle))
        self.image = pg.transform.rotate(self.orig_image, int(angle) % 360)
        self.rect = self.image.get_rect(center=self.get_center())

    def update(self, screen):
        # self.bullets.draw(screen)
        if self.target and self.target.is_dead():
            self.target = None
        if self.target:
            self.turn()
        if self.active:
            self.draw_range()
        if self.can_attack():
            if self.target is not None and self.target.alive and self.in_range(self.target.get_center()):
                self.attack(self.target)
                t = time()
                self.dt = t - self.last_angle
                self.last_angle = t
            else:
                min_s = 99999
                for mob in self.mob_group:
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
        super().__init__('300', pos_x, pos_y, 25, 200, 30, 8, 6)
        self.level = 1
        self.bullet_type = MGBullet
        self.bullet_im = '303'
        self.bullet_speed = 3000
        self.img = [self.image, images['314'], self.image]

    def upgrade(self):
        if self.level == 3:
            return
        self.level += 1
        if self.level == 2:
            self.image = images['301']
            self.orig_image = self.image
            self.rect.x = self.pos[0]
            self.rect.y = self.pos[1]
            self.bullet_im = '308'
            self.bullet_damage *= 2
            self.image = pg.transform.rotate(self.orig_image, self.angle)
            self.rect = self.image.get_rect(center=self.get_center())
            self.img = [self.image, images['315'], self.image]

        elif self.level == 3:
            self.image = images['302']
            self.orig_image = self.image
            self.rect.x = self.pos[0]
            self.rect.y = self.pos[1]
            self.bullet_damage *= 2
            self.bullet_speed *= 2
            self.image = pg.transform.rotate(self.orig_image, self.angle)
            self.rect = self.image.get_rect(center=self.get_center())
            self.bullet_im = '303'
            self.img = [self.image, images['316'], self.image]

    def update(self, screen):
        # self.bullets.draw(screen)
        if self.target and (self.target.is_dead() or not self.in_range(self.target.get_center())):
            self.target = None
            self.image = self.img[0]
            self.orig_image = self.img[0]
            self.image = pg.transform.rotate(self.orig_image, self.angle)
        if self.target:
            self.turn()
            self.image = self.img[1]
            self.orig_image = self.img[1]
            self.image = pg.transform.rotate(self.orig_image, self.angle)

        if self.active:
            self.draw_range()

        if self.can_attack():
            if self.target is not None and self.target.alive and self.in_range(self.target.get_center()):
                self.attack(self.target)
                self.image = self.img[2]
                self.orig_image = self.img[2]
                self.image = pg.transform.rotate(self.orig_image, self.angle)
                t = time()
                self.dt = t - self.last_angle
                self.last_angle = t
            else:
                min_s = 99999
                for mob in self.mob_group:
                    if self.in_range(mob.get_center()) and self.dist(mob.get_center()) < min_s:
                        self.target = mob
                        min_s = self.dist(mob.get_center())


class SmallGun(Tower):
    def __init__(self, pos_x, pos_y):
        super().__init__('117', pos_x, pos_y, 200, 200, 2, 30, 15)
        self.level = 1
        self.bullet_type = SmallBullet
        self.mob_group = ground_mobs

    def upgrade(self):
        if self.level == 3:
            return
        self.level += 1
        if self.level == 2:
            self.bullet_damage *= 2

        elif self.level == 3:
            self.image = images['142']
            self.orig_image = self.image
            self.rect.x = self.pos[0]
            self.rect.y = self.pos[1]
            self.bullet_damage *= 2
            self.image = pg.transform.rotate(self.orig_image, self.angle)
            self.rect = self.image.get_rect(center=self.get_center())


class Rocket(Tower):
    def __init__(self, pos_x, pos_y):
        super().__init__('118', pos_x, pos_y, 100, 250, 3, 40, 20)
        self.level = 1
        self.bullet_type = SmallRocketBullet
        self.speed_bullet = 300
        self.stage = 0
        self.mob_group = ground_mobs

    def half_can_attack(self):
        return time() - self.last_attack >= 1.0 / self.speed / 2

    def double_can_attack(self):
        return time() - self.last_attack >= 1.0 / self.speed * 2

    def upgrade(self):
        if self.level == 3:
            return
        self.level += 1
        if self.level == 2:
            self.bullet_damage *= 2

        elif self.level == 3:
            self.speed *= 2
            self.bullet_damage *= 2

    def update(self, screen):
        self.bullet_speed = 300
        if self.target is not None and self.target.is_dead():
            self.target = None
        if self.target:
            self.turn()
        if self.active:
            self.draw_range()

        if self.half_can_attack():
            if self.stage == 2 or self.double_can_attack():
                self.image = images[self.tile]
                self.orig_image = images[self.tile]
                self.image = pg.transform.rotate(self.orig_image, self.angle)
                self.stage = 0

        if self.can_attack():
            if self.target is not None and self.target.alive and self.in_range(self.target.get_center()):
                self.attack(self.target)
                # recharge
                self.stage += 1
                if self.stage == 1:
                    self.image = images['306']
                    self.orig_image = images['306']
                    self.image = pg.transform.rotate(self.orig_image, self.angle)
                elif self.stage == 2:
                    self.image = images['143']
                    self.orig_image = images['143']
                    self.image = pg.transform.rotate(self.orig_image, self.angle)

                t = time()
                self.dt = t - self.last_angle
                self.last_angle = t
            else:
                min_s = 99999
                for mob in self.mob_group:
                    if self.in_range(mob.get_center()) and self.dist(mob.get_center()) < min_s:
                        self.target = mob
                        min_s = self.dist(mob.get_center())


class PVO(Tower):
    def __init__(self, pos_x, pos_y):
        super().__init__('120', pos_x, pos_y, 500, 350, 2, 120, 80)
        self.level = 1
        self.bullet_type = PVOBullet
        self.bullet_speed = 300
        self.stage = 0
        self.mob_group = air_mobs

    def upgrade(self):
        if self.level == 3:
            return
        self.level += 1
        if self.level == 2:
            self.bullet_damage *= 2

        if self.level == 3:
            self.speed *= 2
            self.image = images['119']
            self.orig_image = self.image
            self.tile = '119'
            self.rect.x = self.pos[0]
            self.rect.y = self.pos[1]
            self.bullet_damage *= 2
            self.image = pg.transform.rotate(self.orig_image, self.angle)
            self.rect = self.image.get_rect(center=self.get_center())

    def half_can_attack(self):
        return time() - self.last_attack >= 1.0 / self.speed / 2

    def double_can_attack(self):
        return time() - self.last_attack >= 1.0 / self.speed * 2

    def update(self, screen):
        if self.target and self.target.is_dead():
            self.target = None
        if self.target:
            self.turn()
        if self.active:
            self.draw_range()

        if self.half_can_attack():
            if (self.level == 1 or self.level == 2) and self.stage == 1:
                self.image = images[self.tile]
                self.orig_image = images[self.tile]
                self.image = pg.transform.rotate(self.orig_image, self.angle)
                self.stage = 0
            elif self.level == 3 and (self.stage == 2 or self.double_can_attack()):
                self.image = images[self.tile]
                self.orig_image = images[self.tile]
                self.image = pg.transform.rotate(self.orig_image, self.angle)
                self.stage = 0

        if self.can_attack():
            if self.target and self.target.alive and self.in_range(self.target.get_center()):
                self.attack(self.target)
                # recharge
                self.stage += 1
                if self.level == 3:
                    if self.stage == 1:
                        self.image = images['307']
                        self.orig_image = images['307']
                        self.image = pg.transform.rotate(self.orig_image, self.angle)
                    elif self.stage == 2:
                        self.image = images['144']
                        self.orig_image = images['144']
                        self.image = pg.transform.rotate(self.orig_image, self.angle)
                else:
                    self.image = images['145']
                    self.orig_image = images['145']
                    self.image = pg.transform.rotate(self.orig_image, self.angle)

                t = time()
                self.dt = t - self.last_angle
                self.last_angle = t
            else:
                min_s = 99999
                for mob in self.mob_group:
                    if self.in_range(mob.get_center()) and self.dist(mob.get_center()) < min_s:
                        self.target = mob
                        min_s = self.dist(mob.get_center())


class BigGun(Tower):
    def __init__(self, pos_x, pos_y):
        super().__init__('167', pos_x, pos_y, 1000, 350, 1, 200, 100)
        self.level = 1
        self.bullet_type = BigBullet
        self.bullet_im = '219'
        self.mob_group = ground_mobs

    def upgrade(self):
        if self.level == 3:
            return
        self.level += 1
        if self.level == 2:
            self.bullet_damage *= 2

        if self.level == 3:
            self.image = images['168']
            self.orig_image = self.image
            self.rect.x = self.pos[0]
            self.rect.y = self.pos[1]
            self.bullet_im = '221'
            self.bullet_damage *= 2
            self.image = pg.transform.rotate(self.orig_image, self.angle)
            self.rect = self.image.get_rect(center=self.get_center())


# Bullets

class Bullet(pg.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, damage, speed, angle=0):
        super().__init__(bullet_group, all_sprites)
        self.damage = damage
        self.speed = speed
        self.target = None
        self.image = images[tile_type]
        self.orig_image = self.image
        self.image = pg.transform.rotate(self.image, angle)
        self.orig_image = pg.transform.rotate(self.orig_image, angle)
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.mask = pg.mask.from_surface(self.image)
        self.pos = pos_x, pos_y

        # frame rate independent data
        self.last_frame = time()
        self.dt = 0
        self.fl = True

    def get_damage(self):
        return self.damage

    def set_target(self, target):
        self.target = target

    def get_center(self):
        return self.pos[0] + tile_size // 2, self.pos[1] + tile_size // 2

    def turn(self):
        x, y = self.target.get_center()
        rel_x, rel_y = x - self.rect.x, y - self.rect.y
        angle = 270 + (180 / math.pi) * -math.atan2(rel_y, rel_x)
        self.image = pg.transform.rotate(self.orig_image, int(angle) % 360)
        self.rect = self.image.get_rect(center=self.pos)

    def move(self):
        if self.target is None:
            return
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
        if self.target and self.fl:
            self.fl = False
            self.turn()
        t = time()
        self.dt = t - self.last_frame
        self.last_frame = t
        self.move()
        if self.target is None or self.target.is_dead():
            self.kill()
        elif pg.sprite.collide_mask(self, self.target):
            self.target.get_damage(self.get_damage())
            if self.target.is_dead():
                self.kill()
            self.kill()


class MGBullet(Bullet):
    def __init__(self, pos_x, pos_y, damage, speed, tile_type):
        super().__init__(tile_type, pos_x, pos_y, damage, speed)


class SmallBullet(Bullet):
    def __init__(self, pos_x, pos_y, damage, speed, tile_type='218'):
        super().__init__(tile_type, pos_x, pos_y, damage, speed)


class SmallRocketBullet(Bullet):
    def __init__(self, pos_x, pos_y, damage, speed, tile_type='305'):
        super().__init__(tile_type, pos_x, pos_y, damage, speed)

    def move(self):
        if self.target is None:
            return
        self.speed *= 1.03
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


class PVOBullet(Bullet):
    def __init__(self, pos_x, pos_y, damage, speed, tile_type='304'):
        super().__init__(tile_type, pos_x, pos_y, damage, speed)

    def move(self):
        if self.target is None:
            return
        self.speed *= 1.03
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


class BigBullet(Bullet):
    def __init__(self, pos_x, pos_y, damage, speed, tile_type):
        super().__init__(tile_type, pos_x, pos_y, damage, speed)


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
    global MONEY, LIFES, WIDTH, HEIGHT, way, waves, WAVES, MOD, REPLAY, INCREASE, waves_res
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
            else:
                s = line.split()
                REPLAY = int(s[0])
                INCREASE = float(s[1])
                WAVES = WAVES + WAVES * REPLAY
        print(waves)
        waves_res = deepcopy(waves)
        if mode == 'endless':
            WAVES = '**'
            REPLAY = 10000000
            title = LEVEL.replace('.txt', '')[:-1]
            cur.execute('''UPDATE levels
                        SET normal = 1
                        WHERE title = ?''', (title,))
            con.commit()
        elif mode == 'hardcore':
            LIFES = 1
    return level_map, decor_map


def generate_tiles():
    """Makes dict with tiles and other objects"""
    global images
    for i in range(1, 320):
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
    TowerMenu('300', 12, 10, 0, 1)
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


def generate_prices(screen, cost='', sell=''):
    """Makes prices for towers"""
    font = pg.font.Font(None, 30)
    # upgrade
    screen.blit(font.render(f'${cost}', 1, (0, 0, 0)), (512, 700))
    # sell
    screen.blit(font.render(f'${sell}', 1, (0, 0, 0)), (672, 700))
    # towers
    screen.blit(font.render('$10', 1, (0, 0, 0)), (784, 700))
    screen.blit(font.render('$30', 1, (0, 0, 0)), (880, 700))
    screen.blit(font.render('$50', 1, (0, 0, 0)), (976, 700))
    screen.blit(font.render('$150', 1, (0, 0, 0)), (1072, 700))
    screen.blit(font.render('$200', 1, (0, 0, 0)), (1168, 700))


def generate_wave():
    """Makes waves of enemies"""
    global waves, dead_group, REPLAY, TOTAL_INCREASE
    dead_group = pg.sprite.Group()
    if not waves:
        if REPLAY > 0:
            REPLAY -= 1
            waves = deepcopy(waves_res)
            TOTAL_INCREASE *= INCREASE
        else:
            game_over()
    if waves:
        for i in mobs_group:
            i.kill()
            pg.display.flip()
        cur_wave = waves[0]
        waves.pop(0)
        for mob in cur_wave:
            for k in range(mob[0]):
                if mob[1] == 'ball':
                    if way[0][0] == way[1][0]:
                        Ball(mob[2], way[0][0], way[0][1] - k, way[0][2])
                    else:
                        Ball(mob[2], way[0][0] - k, way[0][1], way[0][2])
                elif mob[1] == 'frog':
                    if way[0][0] == way[1][0]:
                        Frog(mob[2], way[0][0], way[0][1] - k, way[0][2])
                    else:
                        Frog(mob[2], way[0][0] - k, way[0][1], way[0][2])
                elif mob[1] == 'tank':
                    if way[0][0] == way[1][0]:
                        Tank(mob[2], way[0][0], way[0][1] - 1.5 * k, way[0][2])
                    else:
                        Tank(mob[2], way[0][0] - 1.5 * k, way[0][1], way[0][2])
                elif mob[1] == 'plain':
                    rng = [-2, -1, 0, 1, 2]
                    Plain(mob[2], way[0][0] - 1.5 * k, HEIGHT // 2 + choice(rng))


def generate_lifes(screen):
    """Shows your remaining lifes"""
    font = pg.font.Font(None, 50)
    screen.blit(font.render(f'LIFE: {LIFES}', 1, (255, 255, 255)), (832, 16))


def show_waves(screen):
    """Shows current wave and how many is remaining"""
    font = pg.font.Font(None, 50)
    screen.blit(font.render(f'{CURRENT_WAVE}/{WAVES}', 1, (255, 255, 255)), (448, 16))


def start_level(title):
    global LEVEL, all_sprites, screen
    screen = pg.display.set_mode((1280, 720))
    all_sprites = pg.sprite.Group()
    LEVEL = title
    main()


def game_over():
    gameover = pg.sprite.Sprite()
    if LIFES > 0:
        gameover.image = load_image('win.png')
        title = LEVEL.replace('.txt', '')[:-1]
        if mode == 'normal':
            cur.execute('''UPDATE levels
            SET normal = 1
            WHERE title = ?''', (title,))
            con.commit()
        elif mode == 'hardcore':
            cur.execute('''UPDATE levels
                        SET normal = 1
                        WHERE title = ?''', (title,))
            con.commit()
    else:
        gameover.image = load_image('lose.png')
    gameover.rect = gameover.image.get_rect()
    end_group.add(gameover)
    gameover.rect.x = 390
    gameover.rect.y = 200
    flag = True
    while flag:
        end_group.draw(screen)
        pg.display.flip()
        for ev in pg.event.get():
            if pg.key.get_pressed()[pg.K_ESCAPE]:
                flag = False
                break
            if ev.type == pg.MOUSEBUTTONDOWN:
                flag = False
                break
    pg.quit()
    menu()


def main():
    """Main game function"""
    global chosen_tower, chosen_tower_base, CURRENT_WAVE, screen, dead_group, MONEY
    size = (pg.display.Info().current_w, pg.display.Info().current_h)
    fullscreen = False
    screen.fill(pg.Color('black'))

    # make dict of tiles and other objects
    generate_tiles()
    # generate objects and groups on the main screen
    level, decor_map = load_level(LEVEL)
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
    # for i in range(14):
    #     for j in range(20):
    #         try:
    #             if decor_map[i][j] == '80':
    #                 TowerBase('90', j, i)
    #                 BigGun(j, i)
    #         except BaseException:
    #             pass
    # for i in towers_group:
    #     i.upgrade()
    #     i.upgrade()

    last_wave = None
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                '''Exit to menu'''
                running = False

            if pg.key.get_pressed()[pg.K_ESCAPE]:
                '''Pause'''
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
                        try:
                            chosen_tower.deactivate()
                        except BaseException:
                            pass
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
                                            if tower_type == 1 and MONEY >= 10:
                                                MONEY -= 10
                                                TowerBase('92', x2, y2)
                                                MashineGun(x2, y2)
                                            elif tower_type == 2 and MONEY >= 30:
                                                MONEY -= 30
                                                TowerBase('92', x2, y2)
                                                SmallGun(x2, y2)
                                            elif tower_type == 3 and MONEY >= 50:
                                                MONEY -= 50
                                                TowerBase('92', x2, y2)
                                                Rocket(x2, y2)
                                            elif tower_type == 4 and MONEY >= 150:
                                                MONEY -= 150
                                                TowerBase('92', x2, y2)
                                                PVO(x2, y2)
                                            elif tower_type == 5 and MONEY >= 200:
                                                MONEY -= 200
                                                TowerBase('92', x2, y2)
                                                BigGun(x2, y2)
                                            generate_money()
                                            break
                                tower_menu_clicked = False

                        # upgrade and sell
                        # upgrade
                        for up in upgrade_group:
                            if up.rect.collidepoint(x1, y1):
                                if chosen_tower and chosen_tower_base:
                                    if MONEY >= chosen_tower.cost and chosen_tower.level <= 2:
                                        MONEY -= chosen_tower.cost
                                        generate_money()
                                        chosen_tower.upgrade()
                                        chosen_tower_base.upgrade()
                                    break
                        # sell
                        for se in sell_group:
                            if se.rect.collidepoint(x1, y1):
                                if chosen_tower and chosen_tower_base:
                                    MONEY += chosen_tower.sell
                                    generate_money()
                                    chosen_tower.kill()
                                    chosen_tower_base.kill()
                                    break
                        # choose tower to upgrade or sell
                        for tower in towers_group:
                            if tower.rect.collidepoint(x1, y1):
                                upgrade_group.update(True)
                                sell_group.update(True)
                                chosen_tower = tower
                                chosen_tower.activate()
                                for tb in tower_base_group:
                                    if tb.rect.collidepoint(x1, y1):
                                        chosen_tower_base = tb
                                break
                        else:
                            for up in upgrade_group:
                                if up.rect.collidepoint(x1, y1):
                                    break
                            else:
                                try:
                                    chosen_tower.deactivate()
                                except BaseException:
                                    pass
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
        if chosen_tower:
            generate_prices(screen, chosen_tower.cost, chosen_tower.sell)
        else:
            generate_prices(screen)
        generate_lifes(screen)
        show_waves(screen)
        dead_group.draw(screen)
        tower_menu_group.draw(screen)
        tower_base_group.draw(screen)
        bullet_group.draw(screen)
        towers_group.draw(screen)
        money_group.draw(screen)
        upgrade_group.draw(screen)
        sell_group.draw(screen)
        shadow_group.draw(screen)
        mobs_group.draw(screen)
        mobs_group.update()
        towers_group.update(screen)
        bullet_group.update()
        pg.display.flip()
        if len(mobs_group) == 0 and last_wave is None:
            # start timer until new wave wave
            last_wave = time()
        if last_wave and time() - last_wave >= 5:
            # start new wave
            CURRENT_WAVE += 1
            generate_wave()
            show_waves(screen)
            last_wave = None
        if len(dead_group) > 15:
            dead_group = pg.sprite.Group()
        if LIFES <= 0:
            generate_lifes(screen)
            game_over()

    pg.quit()
    menu()


def menu():
    """Shows menu"""
    win.show()


if __name__ == '__main__':
    # main()
    app = QApplication(sys.argv)
    win = Menu()
    menu()
    sys.exit(app.exec_())
