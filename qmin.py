#!/usr/bin/python
# Minimal event loop just using sensors (no Qt, no windows)
import array
import time
import Queue
import math
import sensors

def main():

	hr_sensor = sensors.AntHrm()
	print "Starting HR Sensor..."
	hr_sensor.start()
	print "Started! Entering loop (Ctrl-C to halt)."
	
	try:
		while True:
			hr_avg = 0
			hr = array.array('I') # array for heart rates from queue
			while hr_sesnsor.queue.qsize():
				try:
					hr_sensor.queue.get(0)
				except Queue.Empty:
					pass
			if len(hr) > 0:
				hr_avg = int(sum(hr)/len(hr))
			print hr_avg
			time.sleep(1)

	except KeyboardInterrrupt:
		print "Interrupted by user at keyboard. Halting..."
		hr_sensor.stop()
		print "Halted."

if __name__ == "__main__":
	main()
