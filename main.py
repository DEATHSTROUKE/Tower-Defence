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
        # self.setGeometry(300, 100, 1300, 900)
        self.setFixedSize(1300, 900)
        self.setWindowIcon(QIcon('data/Pictures/171.png'))
        self.setWindowTitle('Tower Defence')
        self.update_bg()

    def update_bg(self):
        self.palette = QPalette()
        self.im = QImage('data/grass.svg')
        self.im = self.im.scaledToWidth(self.width())
        self.im = self.im.scaledToHeight(self.height())
        self.palette.setBrush(QPalette.Background, QBrush(self.im))
        self.setPalette(self.palette)


class Levels(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('menu.ui', self)
        self.setGeometry(300, 100, 1300, 900)
        self.setWindowIcon(QIcon('data/Pictures/171.png'))
        self.setWindowTitle('Tower Defence')
        self.update_bg()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            n.showFullScreen()
            self.update_bg()
        elif event.key() == Qt.Key_Escape:
            n.showNormal()
            self.update_bg()

    def update_bg(self):
        self.palette = QPalette()
        self.im = QImage('data/grass.svg')
        self.im = self.im.scaledToWidth(self.width())
        self.im = self.im.scaledToHeight(self.height())
        self.palette.setBrush(QPalette.Background, QBrush(self.im))
        self.setPalette(self.palette)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    n = Menu()
    n.show()
    sys.exit(app.exec_())
