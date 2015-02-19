import Queue
from ant.core import driver, node, event, message, log
from ant.core.constants import CHANNEL_TYPE_TWOWAY_RECEIVE, TIMEOUT_NEVER

class AntHrm(event.EventCallback):

    def __init__(self):
		SERIAL = '/dev/ttyUSB0'
		NETKEY = 'B9A521FBBD72C345'.decode('hex')
		self.serial = SERIAL
		self.netkey = NETKEY
		self.antnode = None
		self.channel = None
		self.started = False
		self.queue = Queue.Queue()

    def start(self):
		print(">> TRACEIN  HRM:start")
		if not(self.started):
			self._start_antnode()
			self._setup_channel()
			self.channel.registerCallback(self)
			self.started = True
			print("start listening for hr events")
		print("<< TRACEOUT HRM:start")

    def stop(self):
		print(">> TRACEIN  HRM:stop")
		if self.started:
			if self.channel:
				self.channel.close()
				self.channel.unassign()
			if self.antnode:
				self.antnode.stop()
			self.started = False
		print("<< TRACEOUT HRM:stop")

    def _start_antnode(self):
        print(">> TRACEIN  HRM:_start_antnode")
        stick = driver.USB2Driver(self.serial)
        print("driver assigned to " + self.serial)
        self.antnode = node.Node(stick)
        print("antnode created from stick")
        self.antnode.start()
        print("antnode started")
        print("<< TRACEOUT HRM:_start_antnode")

    def _setup_channel(self):	
        print(">> TRACEIN  HRM:_setup_channel")
        key = node.NetworkKey('N:ANT+', self.netkey)
        self.antnode.setNetworkKey(0, key)
        self.channel = self.antnode.getFreeChannel()
        self.channel.name = 'C:HRM'
        self.channel.assign('N:ANT+', CHANNEL_TYPE_TWOWAY_RECEIVE)
        self.channel.setID(120, 0, 0)
        self.channel.setSearchTimeout(TIMEOUT_NEVER)
        self.channel.setPeriod(8070)
        self.channel.setFrequency(57)
        self.channel.open()
        print("<< TRACEOUT HRM:_setup_channel")

    def process(self, msg):
        if isinstance(msg, message.ChannelBroadcastDataMessage):
			hr = ord(msg.payload[-1])
			#print("heart rate is {}".format(hr))
			self.queue.put(hr)
