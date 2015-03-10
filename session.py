# python classes for QBike session and segment

import array
import datetime

class Accumulator():
	def __init__(self, lowlimit, highlimit):
		self.last_value = 0
		self.value = 0.0
		self.max_value = lowlimit 
		self.min_value = highlimit
		self.n = 0
		self.lowlimit = lowlimit
		self.highlimit = highlimit
		
	def addValue(self, value):
		self.last_value = value
		if (value >= self.lowlimit) and (value <= self.highlimit):
			self.value += value
			self.n += 1
			if (self.max_value < value):
				self.max_value = value
			if (self.min_value > value):
				self.min_value = value
		
	def mean(self):
		if self.n > 0:
			return self.value / self.n
		else:
			return 0

class Segment():

	def __init__(self):	
		# start time
		self.start_time = datetime.datetime.now()
		
		# last data added
		self.last_heart = 0
		self.last_cadence = 0
		self.last_speed = 0.0
		
		# basic data arrays
		self.seconds = array.array('f') # seconds since start
		self.heart = array.array('I') # heart rate (bpm)
		self.cadence = array.array('I') # cadence (revs/m)
		self.speed = array.array('f') # speed (mph or kph)
					
		# mean averages of data (cumulative values stored for efficiency)
		self.acc_heart = Accumulator(30, 250)
		self.acc_cadence = Accumulator(0, 200)
		self.acc_speed = Accumulator(-0.1,99.9)
		
	def addData(self, clocktime, heart, cadence=0, speed=0):
		# store data
		delta = clocktime - self.start_time
		self.seconds.append(delta.total_seconds())
		self.heart.append(heart)
		self.cadence.append(cadence)
		self.speed.append(speed)
		# accumulate to efficiently calculate means
		self.acc_heart.addValue(heart)
		self.acc_cadence.addValue(cadence)
		self.acc_speed.addValue(speed)
		
class Session():
	def __init__(self):
		self.segments = [Segment()] # list of at least one segments
	
	def addSegment(self):
		self.segments.append(Segment())
		
	def thisSegment(self):
		return self.segments[len(self.segments)-1]
		
	def getAllButActiveHeart(self):
		h = array.array('I')
		for i in range(len(self.segments)-1):
			h.extend(self.segments[i].heart)
		return h
	
