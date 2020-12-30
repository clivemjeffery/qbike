#!/usr/bin/env python
import sys
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtGui, QtCore

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # Main UI code goes here

        # End main UI code
        self.show()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
