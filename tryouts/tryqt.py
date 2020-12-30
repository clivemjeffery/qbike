# importing the required libraries 

import sys
import math
import random
import array
import time
from datetime import datetime, timedelta

from PyQt5 import QtGui, QtCore
import pyqtgraph as pg

class MainWindow(QtGui.QMainWindow): 
	def __init__(self): 
		super(MainWindow, self).__init__()

		# set the title 
		self.setWindowTitle("Try Qt Prototyper") 
		# self.setWindowOpacity(1)
		
		# dummy central widget to contain layout manager
		mw = QtGui.QWidget(self)
		self.setCentralWidget(mw)
		layout = QtGui.QGridLayout(mw)
		#self.setLayout(layout)

		## Create some widgets to be placed inside
		btn = QtGui.QPushButton('Useless')
		self.plot = pg.PlotWidget(axisItems = {'bottom': pg.DateAxisItem()})
		print(datetime.now(), datetime.now() + timedelta(hours=1))
		self.plot.setXRange(datetime.now().timestamp(), (datetime.now()+timedelta(hours=1)).timestamp())
		
		# organise in layout
		layout.addWidget(btn, 0 , 0)
		layout.addWidget(self.plot, 0, 1)  # plot goes on right side, spanning 3 rows
		
		# data
		self.times = array.array('d')
		self.values = array.array('f')
		self.times.append(time.time())
		self.values.append(random.uniform(2000, 3000))
		
		# timer
		self.timer = QtCore.QTimer(self)
		self.timer.timeout.connect(self.timerFunction)
		self.ticks = 0
		self.timer.start(1000)
		
	def timerFunction(self):
		self.ticks += 1
		if self.ticks == 1: # first time
			self.start_time = time.time()
			self.plot_line = self.plot.plot(self.times, self.values)
		else:
			self.plot_line.setData(self.times, self.values)
		self.times.append(time.time())
		self.values.append(random.uniform(2000, 3000))
			
		
if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	main = MainWindow()
	main.setGeometry(60, 60, 1024, 768) 
	main.show()
	sys.exit(app.exec_())
