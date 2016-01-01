#!/usr/bin/env python

import sys
import array
import Queue
import time
import datetime
import math
import random

import session
import sensors

from PyQt4 import QtGui, QtCore
from PyQt4.pyqtconfig import Configuration
import pyqtgraph as Pg

class QBikeMainWindow(QtGui.QMainWindow):
	def __init__(self):
		super(QBikeMainWindow, self).__init__()
		self.setWindowTitle('QBike')
		
		# beginnings of athlete data
		self.threshold_heart_rate = 173
		self.active_recovery = self.threshold_heart_rate * 0.68
		self.endurance = self.threshold_heart_rate * 0.83
		self.tempo = self.threshold_heart_rate * 0.94
		self.threshold = self.threshold_heart_rate * 1.05
		self.vo2max = self.threshold_heart_rate * 1.21

		# CTS Zones (note overlaps)
		self.cts_endurance_low = 87
		self.cts_endurance_high = 158
		self.cts_tempo_low = 153
		self.cts_tempo_high = 157
		self.cts_steady_low = 160
		self.cts_steady_high = 164
		self.cts_climb_high = 169
		self.cts_power_low = 174
		
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
		
		# ANT sensor(s) - first stage = heart rate
		self.hr_sensor = sensors.AntHrm()
		
		# training session data
		self.session = session.Session()
		
		# setup the application's own heartbeat once per second
		self.seg_updates = 0 # counter for updates
		timer = QtCore.QTimer(self)
		timer.timeout.connect(self.timerFunction)
		timer.start(1000)
		
	def addWidgets(self):
		
		ml = self.mainLayout
		
		ml.setRowStretch(0, 1)	# row stretch factors to keep hr_current big
 		ml.setRowStretch(1, 3)
		ml.setRowStretch(2, 3)
		ml.setRowStretch(3, 3)
		ml.setRowStretch(4, 6)  # it's on this row
		#ml.setRowStretch(5, 6)
		
		ml.setColumnStretch(0, 1) # force all same?
		ml.setColumnStretch(1, 1)
		ml.setColumnStretch(2, 1)
		ml.setColumnStretch(3, 1)
		
		# From design in notebook
		# Title row widgets
		t1 = QtGui.QLabel("QBike Heart Rate Trainer")
		t2 = QtGui.QLabel("SEGMENT")
		ml.addWidget(t1, 0, 0)
		ml.addWidget(t2, 0, 3)
		
		# 2nd row: plots and max heart rates
		## session plot
		self.plot_session = Pg.PlotWidget(background=QtGui.QColor(30,30,60))
		self.plot_session.setYRange(140, 180) # reasonable heart rate range
		# thresholds
		self.plotCTSThresholdLines(self.plot_session)
		ml.addWidget(self.plot_session, 1, 0, 3, 2)
		## segment plot
		self.plot_segment = Pg.PlotWidget(background=QtGui.QColor(10,10,30))
		self.plot_segment.setYRange(140, 180) # reasonable heart rate range
		self.plot_segment.setXRange(0, 60)
		#self.plot_segment.getPlotItem().hideAxis('left')
		
		ml.addWidget(self.plot_segment, 1, 2, 3, 1)
		# max heart rate in the segment
		self.hr_seg_max = QtGui.QLCDNumber()
		self.hr_seg_max.setDigitCount(3)
		self.hr_seg_max.display("HS")
		ml.addWidget(self.hr_seg_max, 1, 3)
		ml.addWidget(QtGui.QLabel("Max HR"), 1, 3, alignment=QtCore.Qt.AlignTop)
		
		# 3rd row: avg heart rates
		# avg heart rate in the segment
		self.hr_seg_avg = QtGui.QLCDNumber()
		self.hr_seg_avg.setDigitCount(3)
		self.hr_seg_avg.display("US")
		ml.addWidget(self.hr_seg_avg, 2, 3)
		ml.addWidget(QtGui.QLabel("Avg HR"), 2, 3, alignment=QtCore.Qt.AlignTop)
		
		# 4th row: min heart rates
		## avg heart rate in the segment
		self.hr_seg_min = QtGui.QLCDNumber()
		self.hr_seg_min.setDigitCount(3)
		self.hr_seg_min.display("LS")
		ml.addWidget(self.hr_seg_min, 3, 3)
		ml.addWidget(QtGui.QLabel("Min HR"), 3, 3, alignment=QtCore.Qt.AlignTop)
		
		# 5th row: timers, current heart rate
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
		self.hr_current = QtGui.QLCDNumber()
		self.hr_current.setDigitCount(3)
		self.hr_current.display("0B")
		ml.addWidget(self.hr_current, 4, 3)
		ml.addWidget(QtGui.QLabel("HR"), 4, 3, alignment=QtCore.Qt.AlignTop)
		
		# 6th row - speed and cadence - coming whenever!
		## speed
		#self.speed = QtGui.QLCDNumber()
		#self.speed.setDigitCount(4)
		#self.speed.display(25.4)
		#ml.addWidget(self.speed, 5, 1, 1, 2)
		#ml.addWidget(QtGui.QLabel("MPH"), 5, 1, alignment=QtCore.Qt.AlignTop)
		## cadence
		#self.cadence = QtGui.QLCDNumber()
		#self.cadence.setDigitCount(3)
		#self.cadence.display("85")
		#ml.addWidget(self.cadence, 5, 3, 1, 2)
		#ml.addWidget(QtGui.QLabel("Cadence"), 5, 3, alignment=QtCore.Qt.AlignTop)
		
		# Bottom row: buttons
		## start button
		self.startbutton = QtGui.QPushButton("Start")
		self.connect(self.startbutton, QtCore.SIGNAL("clicked()"), self.slotStart)
		ml.addWidget(self.startbutton, 6, 0)
		## stop button
		self.stopbutton = QtGui.QPushButton("Stop")
		self.connect(self.stopbutton, QtCore.SIGNAL("clicked()"), self.slotStop)
		ml.addWidget(self.stopbutton, 6, 1)
		
	def addThresholdName(self, name, colour, ypos):
		ti = Pg.TextItem(name + ' ' + str(ypos), colour)
		self.plot_session.addItem(ti)
		ti.setPos(0, ypos)
		
	def timerFunction(self):
		self.collectData()
		self.updateDisplay()
		
	def collectData(self):
		# simulation
		"""
		heart =  int(math.floor(random.uniform(140, 180)))
		cadence = int(math.floor(random.uniform(70, 100)))
		speed = random.uniform(15.2, 25.9)
		self.session.thisSegment().addData(datetime.datetime.now(), heart, cadence, speed)
		"""
		# real
		hr_avg = 0
		hr = array.array('I') # array for heart rates from queue
		while self.hr_sensor.queue.qsize(): # empty the queue into hr array
			try:
				hr.append(self.hr_sensor.queue.get(0))
			except Queue.Empty:
				pass
		if len(hr) > 0: # average the values from the queue
			hr_avg = int(sum(hr)/len(hr))
		self.session.thisSegment().addData(datetime.datetime.now(), hr_avg, 0, 0)
		
	def updateDisplay(self):
		self.seg_updates += 1
		# overall session time; now back to first segment's start
		now_dt = datetime.datetime.today()
		self.session_time.display(str(now_dt - self.session.segments[0].start_time).split('.',2)[0])
		
		# This segment
		seg = self.session.thisSegment()
		# time:
		self.segup.display(str(now_dt - seg.start_time).split('.',2)[0])
		
		# data and analysis LCDs:
		self.hr_current.display(seg.acc_heart.last_value)
		self.hr_seg_avg.display(seg.acc_heart.mean())
		self.hr_seg_max.display(seg.acc_heart.max_value)
		self.hr_seg_min.display(seg.acc_heart.min_value)
		#self.cadence.display(seg.acc_cadence.last_value)
		#self.speed.display(seg.acc_speed.last_value)

		# plot
		if self.seg_updates % 60 == 0:
			self.plot_segment.setXRange(0, int(self.seg_updates+60))
		self.plot_segment.getPlotItem().plot(seg.heart, clear=True)
		
		# threshold lines
		# self.plotAllThresholdLines(self.plot_segment) -- too slow
		
	def plotInactiveSegments(self):
		if len(self.session.segments) > 1:
			self.plot_session.getPlotItem().plot(self.session.getAllButActiveHeart(), clear=True)
			self.plotCTSThresholdLines(self.plot_session)

	def plotThresholdLine(self, plot, ypos, colour):
		plot.addItem(Pg.InfiniteLine(ypos, 0, colour))
		
	def plotCTSThresholdLines(self, plot):
		self.addThresholdName('Endurance', 'g', self.cts_endurance_high)
		self.addThresholdName('Tempo', 'c', self.cts_tempo_low)
		self.addThresholdName('Steady State', 'm', self.cts_steady_high)
		self.addThresholdName('Climbing', 'y', self.cts_climb_high)
		self.addThresholdName('Power', 'r', self.cts_power_low)
		self.plotThresholdLine(plot, self.cts_endurance_low, 'g')
		self.plotThresholdLine(plot, self.cts_endurance_high, 'g')
		self.plotThresholdLine(plot, self.cts_tempo_low, 'c')
		self.plotThresholdLine(plot, self.cts_tempo_high, 'c')
		self.plotThresholdLine(plot, self.cts_steady_low, 'm')
		self.plotThresholdLine(plot, self.cts_steady_high, 'm')
		self.plotThresholdLine(plot, self.cts_climb_high, 'y')
		self.plotThresholdLine(plot, self.cts_power_low, 'r')

	def plotBritishCyclingThresholdLines(self, plot):
		self.addThresholdName('Active recovery', 'g', self.active_recovery)
		self.addThresholdName('Endurance', 'c', self.endurance)
		self.addThresholdName('Tempo', 'y', self.tempo)
		self.addThresholdName('FTHR', (255,165,0), self.threshold_heart_rate)
		self.addThresholdName('Threshold', (255,165,0), self.threshold)
		self.addThresholdName('VO2Max', 'r', self.vo2max)
		self.plotThresholdLine(plot, self.active_recovery, 'g')
		self.plotThresholdLine(plot, self.endurance, 'c')
		self.plotThresholdLine(plot, self.tempo, 'y')
		self.plotThresholdLine(plot, self.threshold_heart_rate, Pg.mkPen(color=(255, 165, 0), style=QtCore.Qt.DashLine))
		self.plotThresholdLine(plot, self.threshold, (255, 165, 0))
		self.plotThresholdLine(plot, self.vo2max, 'r')
		
	def slotStart(self):
		self.hr_sensor.start()
		
	def slotStop(self):
		self.hr_sensor.stop()
		
	def keyPressEvent(self, e):
		if e.key() == QtCore.Qt.Key_Space:
			self.session.addSegment()
			self.seg_updates = 0
			self.plot_segment.setXRange(0,60)
			self.plotInactiveSegments()
			
		
	def closeEvent(self, event):
		self.slotStop()

class QBikeApp(QtGui.QApplication):
	
	def __init__(self, args):
		super(QBikeApp, self).__init__(args)
		print ("Qt version:", QtCore.QT_VERSION_STR)
		cfg = Configuration()
		print ("SIP version:", cfg.sip_version_str)
		print ("PyQt version:", cfg.pyqt_version_str)
		
		
if __name__ == "__main__":
	app = QBikeApp(sys.argv)
	main = QBikeMainWindow()
	main.move(25, 0)
	main.resize(640,480)
	main.show()
	rc = app.exec_()
	exit(rc)
