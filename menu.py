from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLabel
from PyQt5.QtWidgets import QLineEdit, QMainWindow
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5 import uic
from PyQt5.QtGui import QPalette, QImage, QBrush, QPixmap, QIcon
import os
import sqlite3
import sys
import subprocess

# Menu
con = sqlite3.connect('levels_state.db')
cur = con.cursor()


class Menu(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('menu.ui', self)
        self.setFixedSize(1300, 900)
        self.setWindowIcon(QIcon('data/Tiles/171.png'))
        self.setWindowTitle('Tower Defence')
        self.music = True
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
            lvl = Level(self.main, i[1][1:], i[2], i[3], i[4], i[5])
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
            self.diff.setPixmap(QPixmap('data/hard.png'))
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
        if self.main.music:
            mus = '1'
        else:
            mus = '0'
        subprocess.Popen(['python.exe', 'main.py', self.name, mode, mus])


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
            self.main.music = False
            self.is_sound = False
            self.sound.setIcon(QIcon('data/nosound.png'))
        else:
            self.main.music = True
            self.is_sound = True
            self.sound.setIcon(QIcon('data/sound.png'))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Menu()
    win.show()
    sys.exit(app.exec_())
