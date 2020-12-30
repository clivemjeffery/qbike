#!/usr/bin/env python

import sys
import array
# import Queue
import time
import datetime
import math
import random
import argparse

import session
import zones

from libAnt.drivers.serial import SerialDriver
from libAnt.node import Node
from libAnt.profiles.factory import Factory
from libAnt.profiles.factory import SpeedAndCadenceProfileMessage
from libAnt.profiles.factory import HeartRateProfileMessage

from PyQt5 import QtGui, QtCore
import pyqtgraph as Pg

class QBikeMainWindow(QtGui.QMainWindow):
	def __init__(self):
		super(QBikeMainWindow, self).__init__()
		self.setWindowTitle('QBike')

		# beginnings of athlete data
		self.heart_zones = zones.HeartRateZones.loadZones('hr_zones.json')

		# dummy central widget to contain layout manager
		self.mainWidget = QtGui.QWidget(self)
		self.setCentralWidget(self.mainWidget)

		# colours
		p = self.palette()
		## prototype colour and style
		p.setColor(p.WindowText, QtGui.QColor(200,200,255))
		p.setColor(p.Background, QtGui.QColor(30,30,60))
		self.setPalette(p)

		# layout
		self.mainLayout = QtGui.QGridLayout(self.mainWidget)
		self.addWidgets()

		# Locals for last value read from node
		self.node_hr = 0
		self.node_cadence = 0.0
		self.node_speed_mph = 0.0
		
		# training session data
		self.session = session.Session()
		
		# timer to start from buttons
		self.timer = QtCore.QTimer(self)
		
		# ANT node and callback: TODO; stop hardcoding the port
		self.node = Node(SerialDriver('/dev/ttyUSB0'), 'MoveStickNode')
		self.node.enableRxScanMode()
		self.factory = Factory(self.readNodeMessage)
	
	def addWidgets(self):

		ml = self.mainLayout

		ml.setRowStretch(0, 1)	# row stretch factors to keep hr_inst big
		ml.setRowStretch(1, 3)
		ml.setRowStretch(2, 3)
		ml.setRowStretch(3, 3)
		ml.setRowStretch(4, 6)  # it's on this row
		#ml.setRowStretch(5, 6)

		ml.setColumnStretch(0, 1) # force all same?
		ml.setColumnStretch(1, 1)
		ml.setColumnStretch(2, 1)
		ml.setColumnStretch(3, 1)
		ml.setColumnStretch(4, 1)
		ml.setColumnStretch(5, 1)

		# From design in notebook
		# Title row widgets
		t1 = QtGui.QLabel("QBike Heart Rate Trainer")
		t2 = QtGui.QLabel("SEGMENT")
		ml.addWidget(t1, 0, 0)
		ml.addWidget(t2, 0, 3)

		# 2nd row: plots and max heart rates
		## session plot
		self.plot_session = Pg.PlotWidget(
			background=QtGui.QColor(30,30,60),
			axisItems = {'bottom': Pg.DateAxisItem()}
			)
		# self.plot_session.setYRange(60, 180) # reasonable heart rate range
		self.plot_session.setXRange(0, 3600)
		# thresholds
		self.plotHeartZones(self.plot_session)
		ml.addWidget(self.plot_session, 1, 0, 3, 3)

		# max data displays: col 3, hr
		self.hr_seg_max = QtGui.QLCDNumber()
		self.hr_seg_max.setDigitCount(3)
		ml.addWidget(self.hr_seg_max, 1, 3)
		ml.addWidget(QtGui.QLabel("Max HR"), 1, 3, alignment=QtCore.Qt.AlignTop)
		## col 4, speed
		self.speed_seg_max = QtGui.QLCDNumber()
		self.speed_seg_max.setDigitCount(4)
		ml.addWidget(self.speed_seg_max, 1, 4)
		ml.addWidget(QtGui.QLabel("Max MPH"), 1, 4, alignment=QtCore.Qt.AlignTop)
		## col 5, cadence
		self.cadence_seg_max = QtGui.QLCDNumber()
		self.cadence_seg_max.setDigitCount(3)
		ml.addWidget(self.cadence_seg_max, 1, 5)
		ml.addWidget(QtGui.QLabel("Max Cadence"), 1, 5, alignment=QtCore.Qt.AlignTop)

		# 3rd row: avg heart rates
		# avg heart rate in the segment
		self.hr_seg_avg = QtGui.QLCDNumber()
		self.hr_seg_avg.setDigitCount(3)
		ml.addWidget(self.hr_seg_avg, 2, 3)
		ml.addWidget(QtGui.QLabel("Avg HR"), 2, 3, alignment=QtCore.Qt.AlignTop)
		# col 4, speed
		self.speed_seg_avg = QtGui.QLCDNumber()
		self.speed_seg_avg.setDigitCount(3)
		ml.addWidget(self.speed_seg_avg, 2, 4)
		ml.addWidget(QtGui.QLabel("Avg MPH"), 2, 4, alignment=QtCore.Qt.AlignTop)
		# col 5, cadence
		self.cadence_seg_avg = QtGui.QLCDNumber()
		self.cadence_seg_avg.setDigitCount(3)
		ml.addWidget(self.cadence_seg_avg, 2, 5)
		ml.addWidget(QtGui.QLabel("Avg Cadence"), 2, 5, alignment=QtCore.Qt.AlignTop)

		# 4th row: min heart rate and distance
		self.hr_seg_min = QtGui.QLCDNumber()
		self.hr_seg_min.setDigitCount(3)
		ml.addWidget(self.hr_seg_min, 3, 3)
		ml.addWidget(QtGui.QLabel("Min HR"), 3, 3, alignment=QtCore.Qt.AlignTop)
		self.distance = QtGui.QLCDNumber()
		self.distance.setDigitCount(4)
		ml.addWidget(self.distance, 3, 4, 1, 2)
		ml.addWidget(QtGui.QLabel("Distance"), 3, 4, alignment=QtCore.Qt.AlignTop)

		# 5th row: timers, instant displays
		## session time - increasing
		self.session_time = QtGui.QLCDNumber()
		self.session_time.setDigitCount(5)
		self.session_time.display("00:00")
		ml.addWidget(self.session_time, 4, 0)
		ml.addWidget(QtGui.QLabel("Session Time"), 4, 0, alignment=QtCore.Qt.AlignTop)
		## segment time - increasing
		self.segup = QtGui.QLCDNumber()
		self.segup.setDigitCount(5)
		self.segup.display("59:59")
		self.segup.setSegmentStyle(QtGui.QLCDNumber.Flat)
		ml.addWidget(self.segup, 4, 1, 1, 2)
		ml.addWidget(QtGui.QLabel("Segment Time"), 4, 1, alignment=QtCore.Qt.AlignTop)
		## current heart rate
		self.hr_inst = QtGui.QLCDNumber()
		self.hr_inst.setDigitCount(3)
		self.hr_inst.display("0B")
		ml.addWidget(self.hr_inst, 4, 3)
		ml.addWidget(QtGui.QLabel("HR"), 4, 3, alignment=QtCore.Qt.AlignTop)
		## col 4, speed
		self.speed_inst = QtGui.QLCDNumber()
		self.speed_inst.setDigitCount(4)
		ml.addWidget(self.speed_inst, 4, 4)
		ml.addWidget(QtGui.QLabel("MPH"), 4, 4, alignment=QtCore.Qt.AlignTop)
		## col 5, cadence
		self.cadence_inst = QtGui.QLCDNumber()
		self.cadence_inst.setDigitCount(3)
		ml.addWidget(self.cadence_inst, 4, 5)
		ml.addWidget(QtGui.QLabel("Cadence"), 4, 5, alignment=QtCore.Qt.AlignTop)

		# Bottom row: buttons
		self.simCheck = QtGui.QCheckBox("Simulate")
		ml.addWidget(self.simCheck)
		ml.addWidget(self.simCheck, 6, 0)
		## start button
		self.startbutton = QtGui.QPushButton("Start")
		self.startbutton.clicked.connect(self.slotStart)
		ml.addWidget(self.startbutton, 6, 1)
		## stop button
		self.stopbutton = QtGui.QPushButton("Stop")
		self.stopbutton.clicked.connect(self.slotStop)
		ml.addWidget(self.stopbutton, 6, 2)

	def timerFunction(self):
		if self.simCheck.isChecked():
			self.simulateData()
		self.session.thisSegment().addData(datetime.datetime.now(),
										   self.node_hr,
										   self.node_cadence,
										   self.node_speed_mph)
		self.updateDisplay()

	def readNodeMessage(self, msg):
		# print (msg)
		if isinstance(msg, HeartRateProfileMessage):
			self.node_hr = msg.heartrate
		if isinstance(msg, SpeedAndCadenceProfileMessage):
			self.node_cadence = msg.cadence
			self.node_speed_mph = msg.speed(2096) * 2.2369

	def simulateData(self):
		self.node_hr =  int(math.floor(random.uniform(140, 180)))
		self.node_cadence = int(math.floor(random.uniform(70, 100)))
		self.node_speed_mph = random.uniform(15.2, 25.9)

	def updateDisplay(self):
		self.seg_updates += 1
		# overall session time; now back to first segment's start
		now_dt = datetime.datetime.today()
		self.session_time.display(str(now_dt - self.session.segments[0].start_time).split('.',2)[0])

		# This segment
		seg = self.session.thisSegment()
		# time:
		self.segup.display(str(now_dt - seg.start_time).split('.',2)[0])

		# instant value LCDs:
		self.hr_inst.display(seg.acc_heart.last_value)
		self.speed_inst.display(seg.acc_speed.last_value)
		self.cadence_inst.display(seg.acc_cadence.last_value)
		self.distance.display(seg.distance)

		# average LCDs:
		self.hr_seg_avg.display(seg.acc_heart.mean())
		self.speed_seg_avg.display(seg.acc_speed.mean())
		self.cadence_seg_avg.display(seg.acc_cadence.mean())

		# max LCDs:
		self.hr_seg_max.display(seg.acc_heart.max_value)
		self.speed_seg_max.display(seg.acc_speed.max_value)
		self.cadence_seg_max.display(seg.acc_cadence.max_value)

		# min LCDs: (only heart rate)
		self.hr_seg_min.display(seg.acc_heart.min_value)

		# plot
		if self.seg_updates == 1: # first time
			self.line_session = self.plot_session.plot(seg.seconds, seg.heart, pen='r')
		else:
			self.line_session.setData(seg.seconds, seg.heart)

	def addZoneTextAt(self, text, ypos, colour):
		ti = Pg.TextItem(text, colour)
		self.plot_session.addItem(ti)
		ti.setPos(0, ypos)

	def plotHeartZones(self, plot):
		for name, zone in self.heart_zones.zones.items():
			bDoText = True
			if zone.min is not None:
				self.addZoneTextAt(f'{name} {zone}', zone.min, zone.colour)
				bDoText = False
				self.plot_session.addItem(Pg.InfiniteLine(zone.min, 0, zone.colour))
			if zone.max is not None:
				if bDoText:
					self.addZoneTextAt(f'{name} {zone}', zone.max, zone.colour)
				self.plot_session.addItem(Pg.InfiniteLine(zone.max, 0, zone.colour))

	def antErrorCallback(self, e):
		raise e

	def slotStart(self):
		# setup the application's own heartbeat once per second
		self.seg_updates = 0 # counter for updates
		self.timer.timeout.connect(self.timerFunction)
		self.timer.start(1000)
		if self.simCheck.isChecked() == False:
			self.node.start(self.factory.parseMessage, self.antErrorCallback)

	def slotStop(self):
		self.timer.stop()
		self.node.stop()

	def closeEvent(self, event):
		self.slotStop()

class QBikeApp(QtGui.QApplication):

	def __init__(self, args):
		super(QBikeApp, self).__init__(args)
		print ("Qt version:", QtCore.QT_VERSION_STR)


if __name__ == "__main__":
	app = QBikeApp(sys.argv)
	main = QBikeMainWindow()
	main.move(25, 0)
	main.resize(1024,768)
	main.show()
	rc = app.exec_()
	exit(rc)
