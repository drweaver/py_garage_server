from bottle import install, route, post, static_file, run, redirect, get, request
from garage import Garage
from time import sleep
from garage_notify import GarageNotify
import RPIO as GPIO
from threading import Lock, Thread
from garage_auth import GarageAuth, AuthError
import logging, logging.handlers
from garage_dao import GarageDao
from garage_config import GarageConfig
from os.path import dirname, join
from garage_state_mon import LastStateTransitionMonitor

config = GarageConfig()
auth = GarageAuth(config)
dao = GarageDao()

logger = logging.getLogger("garage_service")

door_switch_lock = Lock()
sensor_callback_lock = Lock()

_AUTH_ERROR={ 'auth': "Authorisation Error" }
_AUTH_OK={ 'auth': 'OK' }

_WEB_ROOT='/gc'

def auth_ok(response):
	response.update(_AUTH_OK)
	return response

def door_switch_callback(e):
	config.reload()
	if door_switch_lock.acquire():
		logger.info("Operating door switch relay")
		if config[GarageConfig.door_switch_enabled]: GPIO.output(relay_channel, GPIO.HIGH)
		sleep(1)
		if config[GarageConfig.door_switch_enabled]: GPIO.output(relay_channel, GPIO.LOW)
		sleep(0.5)
		door_switch_lock.release()
		return True
	return False

def update_from_sensor(channel,state,reason,notify):
	if state:
		if channel==closed_channel:  dao.update_status(reason, Garage.closed)
		if channel==opened_channel:  dao.update_status(reason, Garage.opened)
	else:
		if channel==closed_channel:  dao.update_status(reason, Garage.opening)
		if channel==opened_channel:  dao.update_status(reason, Garage.closing)
	new_state = dao.door_status()
	logger.info('Door state changed to '+new_state)
	config.reload()
	if (notify and config[GarageConfig.notify_enabled]): GarageNotify('Garage Door is now '+new_state).start()
	
def sensor_changed_callback(channel, state):
	try: 
		with sensor_callback_lock:
			global closed_channel_last_state, opened_channel_last_state
			
			if ( (channel==closed_channel and state==closed_channel_last_state) or 
				(channel==opened_channel and state==opened_channel_last_state) ):
				logger.debug("Callback received but already in that state, ignoring...")
				return
			
			if channel==closed_channel:
				closed_channel_last_state = state
			if channel==opened_channel:
				opened_channel_last_state = state
			
			update_from_sensor(channel,state,"callback",True)
	except Exception as detail:
		logger.error("Error during sensor callback: " + str(detail))
	
def door_status_to_json(door_status):
	logger.debug("Door State = " + door_status )
	return { 'state': door_status }

@route(_WEB_ROOT+'/<filepath:path>')
def server_static(filepath):
	return static_file(filepath, root=join(dirname(__file__),'www'))
@route(_WEB_ROOT+'/')
def redirect_to_index():
	return static_file('GarageControl.html', root=join(dirname(__file__),'www'))
	
@post(_WEB_ROOT+'/garagedoor/state')
def door_status():
	try:
		auth.user(request.get_header('X-Forwarded-User'))
		return auth_ok(door_status_to_json( dao.door_status() ))
	except AuthError as detail:
		logger.info("Authorisation failed: " + detail)
		return _AUTH_ERROR

def door_trigger(token,trigger):
	user = auth.user(request.get_header('X-Forwarded-User'))
	garage = Garage(initial=dao.door_status(), door_switch_callback=door_switch_callback)
	update_db = garage.current not in (Garage.opened, Garage.closed )
	if garage.can(trigger):
		getattr(garage, trigger)()
		if update_db: dao.update_status("user:"+user,garage.current)
	return auth_ok(door_status_to_json( dao.door_status() ))

@post(_WEB_ROOT+'/garagedoor/open')
def door_open():
	try:
		auth.location( (request.query.get("lat"), request.query.get("lng")) )
		return door_trigger(request.query.get("token"),Garage.open)
	except AuthError as detail:
		logger.info("Authorisation failed: " + detail)
		return _AUTH_ERROR
	
@post(_WEB_ROOT+'/garagedoor/close')
def door_close():
	try:
		return door_trigger(request.query.get("token"),Garage.close)
	except AuthError as detail:
		logger.info("Authorisation failed: " + detail)
		return _AUTH_ERROR
	
@post(_WEB_ROOT+'/garagedoor/stop')
def door_stop():
	try:
		return door_trigger(request.query.get("token"),Garage.stop)
	except AuthError as detail:
		logger.info("Authorisation failed: " + detail)
		return _AUTH_ERROR

@post(_WEB_ROOT+'/garagedoor/authtoken')
def auth_token():
	try:
		auth.user(request.get_header('X-Forwarded-User'))
		return _AUTH_OK
	except AuthError as detail:
		logger.info("Authorisation failed: "+ detail)
		return _AUTH_ERROR

@post(_WEB_ROOT+'/garagedoor/authlocation')
def auth_location():
	try:
		auth.user(request.get_header('X-Forwarded-User'))
		auth.location( (request.query.get("lat"), request.query.get("lng")) )
		return _AUTH_OK
	except AuthError as detail:
		logger.info("Authorisation failed: " + detail )
		return _AUTH_ERROR
		
if __name__ == '__main__':
	lh = logging.handlers.RotatingFileHandler(config['logfile'],maxBytes=1000000,backupCount=3)
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	lh.setFormatter(formatter)

	root = logging.getLogger()
	root.addHandler(lh)
	root.setLevel(logging.DEBUG)
	
	relay_channel=config[GarageConfig.relay_channel]
	closed_channel=config[GarageConfig.closed_channel]
	opened_channel=config[GarageConfig.opened_channel]
	debounce_timeout_ms=config[GarageConfig.debounce_timeout_ms]
	
	logger.debug("Setting up GPIO")
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)

	GPIO.setup(relay_channel, GPIO.OUT, initial=GPIO.LOW)
	GPIO.setup(closed_channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.setup(opened_channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

	closed_channel_last_state = GPIO.input(closed_channel)
	opened_channel_last_state = GPIO.input(opened_channel)

	last_state = dao.door_status()
	if (not last_state): update_from_sensor(closed_channel,GPIO.LOW,"startup",False)
	elif (GPIO.input(closed_channel) and last_state != Garage.closed): update_from_sensor(closed_channel,GPIO.HIGH,"startup",False)
	elif (GPIO.input(opened_channel) and last_state != Garage.opened): update_from_sensor(opened_channel,GPIO.HIGH,"startup",False)

	logger.debug("last execution state = "+last_state+" current = "+ dao.door_status())
	
	GPIO.add_interrupt_callback(closed_channel, sensor_changed_callback, pull_up_down=GPIO.PUD_DOWN, debounce_timeout_ms=debounce_timeout_ms)
	GPIO.add_interrupt_callback(opened_channel, sensor_changed_callback, pull_up_down=GPIO.PUD_DOWN, debounce_timeout_ms=debounce_timeout_ms)
	GPIO.wait_for_interrupts(threaded=True)		
	
	def garage_notify(msg): GarageNotify(config, msg).start()
	monitor = LastStateTransitionMonitor(dao, config, state=Garage.closed, notify_callback=garage_notify)
	monitor.start()
	
	logger.debug("Starting the server")
	run(server='cherrypy', host='0.0.0.0', port=config[GarageConfig.port])

	logger.debug("Cleaning up GPIO")
	GPIO.cleanup()
	
	logger.debug("Stopping Monitor")
	monitor.stop()
