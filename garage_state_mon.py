from threading import Thread, Event
from time import sleep
from garage import Garage
import logging
from time import time

logger = logging.getLogger('garage_state_mon')

class LastStateTransitionMonitor(Thread):

	def __init__(self, dao, config, state=Garage.closed, notify_callback=None):
		Thread.__init__(self)
		self._dao = dao
		self._config = config
		self._notify_callback = notify_callback
		self._state = state
		self._stop_event = Event()
		
	
	def check_now(self):
		last_time = self._dao.last_state_transition_from(self._state)
		if last_time is None:
			logger.info("No notification required, already in "+self._state+" state")
			return
		if last_time == 0: 			
			msg = 'Garage Door has never been '+self._state
		else:
			diff = int(( time() - last_time ) / 60)
			self._config.reload()
			limit = self._config['state_monitor_limit_mins']
			if diff < limit: return
			if diff > 99: diff_msg = str(round(diff/60))+' hours'
			elif diff > 48: diff_msg = str(round(diff/3600))+' days'
			else: diff_msg = str(diff)+' minutes'
			msg = 'Garage Door has not been '+self._state+' for '+diff_msg
		logger.info(msg)
		if self._notify_callback and self._config['state_monitor_enabled']: self._notify_callback(msg)

	def run(self):
		while 1:
			self.check_now()
			self._config.reload()
			self._stop_event.wait(self._config['state_monitor_interval_mins'] * 60)
			if( self._stop_event.is_set() ): break
		
	def stop(self):
		self._stop_event.set()
	
if __name__ == '__main__':
	from garage_dao import GarageDao
	from garage_config import GarageConfig
	def callback(msg):
		print(msg)
	logging.basicConfig(filename=__file__+'.log',level=logging.DEBUG)
	LastStateTransitionMonitor(GarageDao(),GarageConfig(), state=Garage.opening, notify_callback=callback).run()