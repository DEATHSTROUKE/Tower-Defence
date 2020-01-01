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

pg.init()


class Menu(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('menu.ui', self)
        self.setFixedSize(1300, 900)
        self.setWindowIcon(QIcon('data/Tiles/171.png'))
        self.setWindowTitle('Tower Defence')
        self.update_bg()
        self.start()

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

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pg.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def start_level(level):
    LEVEL = level
    main()


def main():
    size = (pg.display.Info().current_w, pg.display.Info().current_h)
    print(size)
    screen = pg.display.set_mode(size, pg.FULLSCREEN)
    fullscreen = True
    screen.fill(pg.Color('green'))
    clock = pg.time.Clock()
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                '''Exit to menu'''
                running = False
            if event.type == pg.KEYDOWN:
                pass
            if pg.key.get_pressed()[pg.K_ESCAPE]:
                '''Pause'''
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

        screen.fill(pg.Color('green'))
        pg.display.flip()

    pg.quit()
    # menu()


def menu():
    pass
    # win.show()


if __name__ == '__main__':
    main()
    # app = QApplication(sys.argv)
    # win = Menu()
    # menu()
    # sys.exit(app.exec_())
