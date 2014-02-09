import json
import logging
import threading
from os.path import dirname, join


logger = logging.getLogger('garage_config')

class GarageConfig():

	door_switch_enabled='door_switch_enabled'
	notify_enabled='notify_enabled'
	port='port'
	client_id='client_id'
	authorised='authorised'
	smtp_server='smtp_server'
	smtp_port='smtp_port'
	smtp_sender='smtp_sender'
	smtp_recipient='smtp_recipient'
	smtp_pwd_file='smtp_pwd_file'
	lat='lat'
	lng='lng'
	relay_channel='relay_channel'
	closed_channel='closed_channel'
	opened_channel='opened_channel'
	debounce_timeout_ms='debounce_timeout_ms'
	distance_limit_miles='distance_limit_miles'
	

	def __init__(self, file=join(dirname(__file__),"garage_config.json")):
		self._file = file
		self._lock = threading.Lock()
		self.reload(ignoreError=False)
	
	def reload(self, ignoreError=True):
		logger.debug('loading config from file: '+self._file)
		try:
			with open(self._file, 'r') as f:
				with self._lock:
					self._data = json.load(f)
		except Exception as e:
			logger.error('Config file error: '+str(e))
			if ignoreError:
				logger.info('Ignoring error, retaining old values')
				return
			raise e
		
	def __getitem__(self,key):
		with self._lock:
			return self._data[key] if key in self._data else None
