import json
import urllib.request
import logging
from garage_config import GarageConfig
from geopy import distance


class AuthError(Exception):
	def __init__(self,value):
		self.value = value
	def __str__(self):
		return repr(self.value)
	def __add__(self, other):
		return str(self) + other
	def __radd__(self, other):
		return other + str(self)

logger = logging.getLogger("garage_auth")

class GarageAuth:

	_AUTH_URL='https://www.googleapis.com/oauth2/v1/tokeninfo?access_token='

	def __init__(self, config, urlopen=None ):
		self._config = config
		def myurlopen(url):	return urllib.request.urlopen(url).readall().decode('utf-8')
		#self._urlopen = lambda url: urllib.request.urlopen(url).readall().decode('utf-8') if urlopen is None else urlopen
		self._urlopen = myurlopen if urlopen is None else urlopen
	
	def token(self,token):

		self._config.reload()
		logger.debug("token="+token)
		try:
			data = json.loads(self._urlopen(GarageAuth._AUTH_URL+token))
		except Exception as e:
			raise AuthError("Error validating token: " + str(e))
		
		if( 'error' in data ):			raise AuthError("Token validation error: " + data['error'])
		if( 'audience' not in data ): 	raise AuthError("Missing Audience in token validation response")
		if( 'email' not in data ): 		raise AuthError("Missing email in token validation response")
		if( data['audience'] != self._config['client_id'] ): raise AuthError("Invalid audience: " + data['audience'])
		if( data['email'] not in self._config['authorised'] ): raise AuthError("Invalid user: " + data['email'])
		
		logger.info("Token verified, user authorised: " + data['email']) 
		return data['email']

	def location(self,origin):

		self._config.reload()

		dest = ( self._config[GarageConfig.lat], self._config[GarageConfig.lng] )
		d = distance.distance(origin, dest).miles
		logger.debug("Distance of requester = "+str(d)+" miles, allowed limit = "+str(self._config[GarageConfig.distance_limit_miles]))
		if d > self._config[GarageConfig.distance_limit_miles]:
			raise AuthError("Distance beyond limit: " + str(d))
		logger.info("Distance verified: "+str(d)+" is <= " + str(self._config[GarageConfig.distance_limit_miles]) + " miles")
		return d
	
	def user(self,username):
		self._config.reload()
		if username is None: raise AuthError("Invalid user")
		logger.debug("user="+username)
		if( username not in self._config['authorised'] ) : raise AuthError("Invalid user: " + username)
		return username