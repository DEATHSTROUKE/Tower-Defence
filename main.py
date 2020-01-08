from random import choice, shuffle, random
from copy import deepcopy
import sys
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLabel
from PyQt5.QtWidgets import QLineEdit, QMainWindow, QCheckBox, QPlainTextEdit
from PyQt5.QtWidgets import QFormLayout, QListWidget, QListWidgetItem, QDialog
from PyQt5 import uic
from PyQt5.QtGui import QPalette, QImage, QBrush, QPixmap, QIcon
import pygame as pg
import os
from time import time


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

# constant
MONEY = 0
LIFES = 0
LEVEL = 0
CURRENT_WAVE = 1
WAVES = 1
FPS = 30

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
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(mobs_group, all_sprites)
        self.image = images[tile_type]
        self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)
        self.health = self.max_health = 100
        self.speed = 20

        # controle points
        self.destinations = deepcopy([i[:3] for i in way])
        print(self.destinations)
        self.visited = 0

        self.last = time()
        self.healthbar = None

    def get_damage(self, damage):
        self.health -= damage

    def is_alive(self):
        return self.health > 0

    def dead(self):
        self.image = images['114']
        self.speed = 0

    def is_dead(self):
        return self.health <= 0

    def has_destination(self):
        return self.visited < len(self.destinations)

    def move(self):
        steps = self.speed
        while steps > 0 and self.has_destination():
            x, y = self.position
            destination = self.destinations[self.visited]
            if self.position == destination:
                self.visited += 1
                continue
            sign_x = -1
            if destination[0] > x:
                sign_x = 1
            elif destination[0] == x:
                sign_x = 0
            sign_y = -1
            if destination[1] > y:
                sign_y = 1
            elif destination[1] == y:
                sign_y = 0

            x += sign_x
            y += sign_y
            self.position = (x, y)
            steps -= 1

    def game_logic(self):
        t = time()
        self.dt = t - self.last_frame
        self.last_frame = t

        if self.health <= 0:
            self.dead()
        self.move()


class Ball(Mob):
    def __init__(self, level, pos_x, pos_y, angle):
        tile_type = ''
        if level == 1:
            tile_type = '193'
        elif level == 2:
            tile_type = '195'
        elif level == 3:
            tile_type = '194'
        elif level == 4:
            tile_type = '196'
        super().__init__(tile_type, pos_x, pos_y)
        self.image = pg.transform.rotate(self.image, angle)


class Frog(Mob):
    def __init__(self, level, pos_x, pos_y, angle):
        tile_type = ''
        if level == 1:
            tile_type = '163'
        elif level == 2:
            tile_type = '165'
        elif level == 3:
            tile_type = '166'
        elif level == 4:
            tile_type = '164'
        super().__init__(tile_type, pos_x, pos_y)
        self.image = pg.transform.rotate(self.image, angle)


class Tank(Mob):
    def __init__(self, level, pos_x, pos_y, angle):
        tile_type = ''
        if level == 1:
            tile_type = '188'
        elif level == 2:
            tile_type = '189'
        super().__init__(tile_type, pos_x, pos_y)
        self.image = pg.transform.rotate(self.image, angle)


class Plain(Mob):
    def __init__(self, level, pos_x, pos_y):
        tile_type = ''
        if level == 1:
            tile_type = '190'
        elif level == 2:
            tile_type = '192'
        super().__init__(tile_type, pos_x, pos_y)


# Towers

class Tower(pg.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(towers_group, all_sprites)
        self.image = images[tile_type]
        self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)


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
        super().__init__('300', pos_x, pos_y)
        self.level = 1

    def upgrade(self):
        self.level += 1
        if self.level == 2:
            self.image = images['301']
        elif self.level == 3:
            self.image = images['302']


class SmallGun(Tower):
    def __init__(self, pos_x, pos_y):
        super().__init__('117', pos_x, pos_y)
        self.level = 1

    def upgrade(self):
        self.level += 1
        if self.level == 2:
            pass
        elif self.level == 3:
            self.image = images['142']


class Rocket(Tower):
    def __init__(self, pos_x, pos_y):
        super().__init__('118', pos_x, pos_y)
        self.level = 1

    def upgrade(self):
        self.level += 1
        if self.level == 2:
            pass
        elif self.level == 3:
            pass


class PVO(Tower):
    def __init__(self, pos_x, pos_y):
        super().__init__('120', pos_x, pos_y)
        self.level = 1

    def upgrade(self):
        self.level += 1
        if self.level == 2:
            pass
        if self.level == 3:
            self.image = images['119']


class BigGun(Tower):
    def __init__(self, pos_x, pos_y):
        super().__init__('167', pos_x, pos_y)
        self.level = 1

    def upgrade(self):
        self.level += 1
        if self.level == 2:
            pass
        if self.level == 3:
            self.image = images['168']


# Bullets

class Bullet(pg.sprite.Sprite):
    pass


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
    global MONEY, LIFES, WIDTH, HEIGHT, way, waves, WAVES
    fname = "data/Maps/" + fname
    with open(fname, 'r') as mapf:
        level_map = []
        decor_map = []
        for i, line in enumerate(mapf):
            if i == 0:
                MONEY = int(line.strip())
            elif i == 1:
                LIFES = int(line.strip())
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
                way.append([int(j) for j in line.split()])
            elif i == HEIGHT + h + 3 + corners:
                w = int(line.strip())
                WAVES = w
            elif HEIGHT + h + 3 + corners < i < HEIGHT + h + 3 + corners + w:
                waves.append([int(line.split()[0]), line.split()[1], int(line.split()[2])])
        print(waves)
    max_width = max(map(len, level_map))
    return level_map, decor_map


def generate_tiles():
    """Makes dict with tiles and other objects"""
    global images
    for i in range(1, 303):
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


def generate_way():
    """Makes way for enemies"""
    global way
    full_way = []
    for c in range(len(way) - 1):
        full_way.append(way[c])
        if way[c][0] == way[c + 1][0]:
            if way[c][1] < way[c + 1][1]:
                for i in range(way[c][1] + 1, way[c + 1][1]):
                    full_way.append([way[c][0], i, way[c][2]])
            else:
                for i in range(way[c][1] - 1, way[c + 1][1], -1):
                    full_way.append([way[c][0], i, way[c][2]])
        else:
            if way[c][0] < way[c + 1][0]:
                for i in range(way[c][0] + 1, way[c + 1][0]):
                    full_way.append([i, way[c][1], way[c][2]])
            else:
                for i in range(way[c][0] - 1, way[c + 1][0], -1):
                    full_way.append([i, way[c][1], way[c][2]])
    full_way.append(way[-1])
    way = full_way
    print(way)


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


def generate_waves():
    """Makes waves of enemies"""


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


def main():
    """Main game function"""
    global chosen_tower, chosen_tower_base
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
    generate_way()
    pg.display.flip()

    # create flags
    tower_menu_clicked = False
    tower_type = 0

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
        pg.display.flip()

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
