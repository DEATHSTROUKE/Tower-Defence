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
LIVES = 0
LEVEL = 0

wigth, height = 20, 13
images = {}
way = []
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
            self.image = images['142']


class Rocket(Tower):
    def __init__(self, pos_x, pos_y):
        super().__init__('118', pos_x, pos_y)
        self.level = 1

    def upgrade(self):
        pass


class PVO(Tower):
    def __init__(self, pos_x, pos_y):
        super().__init__('120', pos_x, pos_y)
        self.level = 1

    def upgrade(self):
        self.level += 1
        if self.level == 2:
            self.image = images['119']


class BigGun(Tower):
    def __init__(self, pos_x, pos_y):
        super().__init__('167', pos_x, pos_y)
        self.level = 1

    def upgrade(self):
        self.level += 1
        if self.level == 2:
            self.image = images['168']


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
    global MONEY, LIVES, width, heigth, way
    fname = "data/Maps/" + fname
    with open(fname, 'r') as mapf:
        level_map = []
        decor_map = []
        for i, line in enumerate(mapf):
            if i == 0:
                MONEY = int(line.strip())
            elif i == 1:
                LIVES = int(line.strip())
            elif i == 2:
                t = line.split()
                width, height = int(t[0]), int(t[1])
            elif 3 <= i < height + 3:
                level_map.append(line.split())
            elif i == height + 3:
                h = int(line.strip())
            elif height + 3 < i < height + h + 3:
                decor_map.append(line.split())
            elif i == height + h + 3:
                corners = int(line.strip())
            elif height + h + 3 < i < height + h + 3 + corners:
                way.append([int(j) for j in line.split()])
        print(way)

    max_width = max(map(len, level_map))
    return level_map, decor_map


def generate_level(level):
    """Makes level"""
    for x in range(len(level)):
        for y in range(len(level[x])):
            Tile(level[x][y], y, x)


def generate_decor(level):
    """Make decorations on level"""
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
    print(width, height)
    for x in range(width):
        for y in range(height):
            if x * tile_size <= mouse_pos[0] <= (x + 1) * tile_size and \
                    y * tile_size <= mouse_pos[1] <= (y + 1) * tile_size:
                return x, y
    return None


def generate_money():
    """Make start money"""
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
                        for up in upgrade_group:
                            if up.rect.collidepoint(x1, y1):
                                if chosen_tower:
                                    chosen_tower.upgrade()
                                    chosen_tower_base.upgrade()
                                    break
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

            if event.type == pg.MOUSEBUTTONUP:
                pass

            if pg.key.get_pressed()[pg.K_F11]:
                '''Change screen size'''
                if fullscreen:
                    screen = pg.display.set_mode((1280, 720))
                    fullscreen = False
                else:
                    size = (pg.display.Info().current_w, pg.display.Info().current_h)
                    screen = pg.display.set_mode(size, pg.FULLSCREEN)
                    fullscreen = True

        tiles_group.draw(screen)
        obj_group.draw(screen)
        decors_group.draw(screen)
        if tower_menu_clicked:
            tower_place_group.draw(screen)
        pg.draw.rect(screen, pg.Color('#66cdaa'), (512, 640, 704, 64)), 768, 640
        tower_menu_group.draw(screen)
        tower_base_group.draw(screen)
        towers_group.draw(screen)
        money_group.draw(screen)
        upgrade_group.draw(screen)
        sell_group.draw(screen)
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
