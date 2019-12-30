from random import choice, shuffle, random
from copy import deepcopy
import sys
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLabel
from PyQt5.QtWidgets import QLineEdit, QMainWindow, QCheckBox, QPlainTextEdit
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtWidgets import QFormLayout, QListWidget, QListWidgetItem, QDialog
from PyQt5 import uic
from PyQt5.QtGui import QPalette, QImage, QBrush, QPixmap, QIcon
import pygame as pg

GRAVITY = 1
width, height = 500, 500
size = 500, 500


# screen = pg.display.set_mode(size)
# screen.fill(pg.Color('black'))


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
        self.newForm = Level(self)
        self.scroll1.setWidget(self.newForm)

    def help(self):
        self.scroll1.takeWidget()
        self.newForm = Start(self)
        self.scroll1.setWidget(self.newForm)

    def settings(self):
        self.scroll1.takeWidget()
        self.newForm = Start(self)
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
        self.play.clicked.connect(self.play1)
        self.help.clicked.connect(self.help1)
        self.settings.clicked.connect(self.settings1)

    def play1(self):
        pass

    def settings1(self):
        pass

    def help1(self):
        pass


class Level(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('start_screen.ui', self)


class Help(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('start_screen.ui', self)


class Settings(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('start_screen.ui', self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Menu()
    win.show()
    sys.exit(app.exec_())
