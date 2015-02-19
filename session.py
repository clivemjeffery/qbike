# python classes for QBike session and segment

import array
import datetime

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
		
		# max and min data (initialised to trigger first set)
		self.max_heart = 0 # remember they're unsigned so not -1
		self.min_heart = 400
		self.max_cadence = 0
		self.min_cadence = 400
		self.max_speed = -0.1
		self.min_speed = 99.9
			
		# moving average data (cumulative values stored for efficiency)
		self.avg_heart = 0.0
		self.cum_heart = 0.0
		self.avg_cadence = 0.0
		self.cum_cadence = 0.0
		self.avg_speed = 0.0
		self.cum_speed = 0.0
		
	def addData(self, clocktime, heart, cadence=0, speed=0):
		# store data
		self.last_heart = heart
		self.last_cadence = cadence
		self.last_speed = speed
		delta = clocktime - self.start_time
		self.seconds.append(delta.total_seconds())
		self.heart.append(heart)
		self.cadence.append(cadence)
		self.speed.append(speed)
		# check for new min and max (within sensible limits for me)
		if (self.max_heart < heart) and (heart < 250):
			self.max_heart = heart
		if (self.min_heart > heart) and (heart > 30):
			self.min_heart = heart
		if self.max_cadence < cadence:
			self.max_cadence = cadence
		if self.min_cadence > cadence:
			self.min_cadence = cadence
		if self.max_speed < speed:
			self.max_speed = speed
		if self.min_speed > speed:
			self.min_speed = speed
		# accumulate to efficiently calculate means
		self.cum_heart += heart
		self.cum_cadence += cadence
		self.cum_speed += speed
		# calculate mean averages
		n = len(self.seconds) # can't be zero, appended at least once
		self.avg_heart = self.cum_heart / n
		self.avg_cadence = self.cum_cadence / n
		self.avg_speed = self.cum_speed / n
		
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
	
