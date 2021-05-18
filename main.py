"""
Some code is used from https://www.mfitzp.com/tutorials/bitmap-graphics/
Inspiration from https://github.com/stephencwelch/Imaginary-Numbers-Are-Real
"""

import sys

import numpy as np
from sklearn.decomposition import KernelPCA
from sklearn.datasets import make_circles

from PyQt5 import QtCore, QtGui, QtWidgets

COLORS = [
            '#000000', '#141923', '#414168', '#3a7fa7', '#35e3e3', '#8fd970',
            '#5ebb49', '#458352', '#dcd37b', '#fffee5', '#ffd035', '#cc9245',
            '#a15c3e', '#a42f3b', '#f45b7a', '#c24998', '#81588d', '#bcb0c2',
            '#ffffff',
         ]


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        title = "original <-> feature spaces"
        # set the title
        self.setWindowTitle(title)

        self.canvas_input = Canvas()
        self.canvas_input.space = 'input'
        self.canvas_output = Canvas()
        self.canvas_output.space = 'output'

        self.canvas_input.transformed_space = self.canvas_output
        self.canvas_output.transformed_space = self.canvas_input

        self.canvas_input.plot_dataset(X)
        self.canvas_output.plot_dataset(X)

        w = QtWidgets.QWidget()
        l = QtWidgets.QHBoxLayout()
        w.setLayout(l)
        l.addWidget(self.canvas_input)
        l.addWidget(self.canvas_output)

        palette = QtWidgets.QVBoxLayout()
        self.add_palette_buttons(palette)
        l.addLayout(palette)
        self.setCentralWidget(w)

    def add_palette_buttons(self, layout):
        reset_buton = QPaletteButton('#ffffff', 'Clean')
        reset_buton.pressed.connect(self.clear_all)
        layout.addWidget(reset_buton)

        for c in COLORS:
            b = QPaletteButton(c)
            b.pressed.connect(lambda c=c: (self.canvas_input.set_pen_color(c),
                              self.canvas_output.set_pen_color(c)))
            layout.addWidget(b)

    def clear_all(self):
        self.canvas_input.plot_dataset(X)
        self.canvas_output.plot_dataset(X)


class Canvas(QtWidgets.QLabel):

    def __init__(self):
        super().__init__()
        self.pixmap_size = (650, 650)
        pixmap = QtGui.QPixmap(*self.pixmap_size)
        self.setPixmap(pixmap)
        self.last_x, self.last_y = None, None
        self.pen_color = QtGui.QColor('#000000')

    def plot_dataset(self, data):
        painter = QtGui.QPainter(self.pixmap())
        painter.fillRect(0, 0, *self.pixmap_size, QtGui.QColor('#ffffff'))
        pen = QtGui.QPen()
        pen.setWidth(2)
        painter.setPen(pen)
        if self.space == 'input':
            for i in data:
                x, y = self.data_to_pixel(i[0], i[1], self.pixmap_size)
                painter.drawPoint(x, y)
                # x, y = self.coord_transform(x, y)
                # x, y = self.coord_transform(x, y, inverse=True)
                # painter.drawPoint(x, y)
        else:
            for i in data:
                x, y = self.data_to_pixel(i[0], i[1], self.pixmap_size)
                x, y = self.coord_transform(x, y)
                painter.drawPoint(x, y)

        painter.end()
        self.update()

    def set_pen_color(self, c):
        self.pen_color = QtGui.QColor(c)

    def mouseMoveEvent(self, e):
        if self.last_x is None:  # First event.
            self.last_x = e.x()
            self.last_y = e.y()
            return  # Ignore the first time.

        painter = QtGui.QPainter(self.pixmap())
        p = painter.pen()
        p.setWidth(2)
        p.setColor(self.pen_color)
        painter.setPen(p)
        painter.drawLine(self.last_x, self.last_y, e.x(), e.y())
        painter.end()
        self.update()
        self.update_transformed_space(e)

        # Update the origin for next time.
        self.last_x = e.x()
        self.last_y = e.y()

    def mouseReleaseEvent(self, e):
        self.last_x = None
        self.last_y = None

    def update_transformed_space(self, e):
        painter = QtGui.QPainter(self.transformed_space.pixmap())
        p = painter.pen()
        p.setWidth(2)
        p.setColor(self.pen_color)
        painter.setPen(p)

        if self.space == 'input':
            x, y = self.coord_transform(e.x(), e.y())
            last_x, last_y = self.coord_transform(self.last_x, self.last_y)
        else:
            x, y = self.coord_transform(e.x(), e.y(), inverse=True)
            last_x, last_y = self.coord_transform(self.last_x, self.last_y,
                                                  inverse=True)
        painter.drawLine(last_x, last_y, x, y)
        painter.end()
        self.transformed_space.update()

    def pixel_to_data(self, x, y, pixmap_size):
        mean_x = pixmap_size[0] / 2
        mean_y = pixmap_size[1] / 2
        std_x = pixmap_size[0] / 2
        std_y = pixmap_size[1] / 2
        return (x - mean_x)/std_x, (y - mean_y)/std_y

    def data_to_pixel(self, x, y, pixmap_size):
        mean_x = pixmap_size[0] / 2
        mean_y = pixmap_size[1] / 2
        std_x = pixmap_size[0] / 2
        std_y = pixmap_size[1] / 2
        x, y = x*std_x + mean_x, y*std_y + mean_y
        return np.int32(x), np.int32(y)

    def coord_transform(self, x, y, inverse=False):
        x, y = self.pixel_to_data(x, y, self.pixmap_size)
        if inverse:
            x, y = kpca.inverse_transform([[x, y]])[0]
        else:
            x, y = kpca.transform([[x, y]])[0]
        x, y = self.data_to_pixel(x, y, self.transformed_space.pixmap_size)
        return x, y


class QPaletteButton(QtWidgets.QPushButton):

    def __init__(self, color, text=''):
        super().__init__()
        self.setFixedSize(QtCore.QSize(24, 24))
        self.color = color
        self.setStyleSheet("background-color: %s;" % color)
        if text != '':
            self.setText(text)
            self.setFixedSize(QtCore.QSize(40, 24))


def main():

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()


X, y = make_circles(n_samples=400, factor=.3, noise=0.05, random_state=0)

kpca = KernelPCA(kernel="rbf", fit_inverse_transform=True, gamma=10,
                 n_components=2)
kpca = kpca.fit(X)


if __name__ == '__main__':
    main()
