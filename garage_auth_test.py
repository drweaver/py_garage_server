import unittest
from mock import MagicMock
from garage_auth import GarageAuth, AuthError
from io import StringIO

file='garage_auth_test.json'

class GarageAuthTest(unittest.TestCase):

	def setUp(self):
		
		def getitem(key):
			config = { "client_id": "12345", "authorised": ["persona","personb"], "distance_limit_miles": 10, "lat": 0, "lng": 0 }
			return config[key]
			
		self._config = MagicMock()
		self._config.__getitem__.side_effect = getitem
		self._config.reload = MagicMock()

	def test_forwarded_user_nobody(self):
		auth = GarageAuth(self._config)
		with self.assertRaises(AuthError):
			auth.user("nobody")
			
	def test_forwarded_user_none(self):
		auth = GarageAuth(self._config)
		with self.assertRaises(AuthError):
			auth.user(None)
	
	def test_forwarded_user_persona(self):
		auth = GarageAuth(self._config)
		self.assertEqual("persona",auth.user("persona"))
	
	def test_forwarded_user_persona(self):
		auth = GarageAuth(self._config)
		self.assertEqual("personb",auth.user("personb"))
	
	def test_token_error(self):
		urlopenmock = MagicMock(return_value='{ "error": "some error"} ')
		auth = GarageAuth(self._config, urlopen=urlopenmock)
		with self.assertRaises(AuthError):
			auth.token("mytoken")
		
	def test_token_error_with_response(self):
		urlopenmock = MagicMock(return_value="<html><body>rubbish</body></html> ")
		auth = GarageAuth(self._config, urlopen=urlopenmock)
		with self.assertRaises(AuthError):
			auth.token("mytoken")

	def test_token_invalid_audience(self):
		urlopenmock = MagicMock(return_value='{ "audience": "54321", "email": "persona" } ')
		auth = GarageAuth(self._config, urlopen=urlopenmock)
		with self.assertRaises(AuthError):
			auth.token("mytoken")
	
	def test_token_email_not_auth(self):
		urlopenmock = MagicMock(return_value='{ "audience": "12345", "email": "personc" } ')
		auth = GarageAuth(self._config, urlopen=urlopenmock)
		with self.assertRaises(AuthError):
			auth.token("mytoken")

	def test_token_audience_not_exist(self):
		urlopenmock = MagicMock(return_value='{ "audiences": "12345", "email": "persona" } ')
		auth = GarageAuth(self._config, urlopen=urlopenmock)
		with self.assertRaises(AuthError):
			auth.token("mytoken")
			
	def test_token_email_not_exist(self):
		urlopenmock = MagicMock(return_value='{ "audience": "12345", "emails": "persona" } ')
		auth = GarageAuth(self._config, urlopen=urlopenmock)
		with self.assertRaises(AuthError):
			auth.token("mytoken")
	
	def test_token_response_1(self):
		urlopenmock = MagicMock(return_value='{ "audience": "12345", "email": "persona" } ')
		auth = GarageAuth(self._config, urlopen=urlopenmock)
		self.assertEqual("persona", auth.token("mytoken"))
		self._config.reload.assert_called_with()

	def test_token_response_2(self):
		urlopenmock = MagicMock(return_value='{ "audience": "12345", "email": "personb" } ')
		auth = GarageAuth(self._config, urlopen=urlopenmock)
		self.assertEqual("personb", auth.token("mytoken"))
		self._config.reload.assert_called_with()
	
	def test_location_too_far(self):
		auth = GarageAuth(self._config)
		with self.assertRaises(AuthError):
			auth.location( (0,0.2) )

	def test_location_ok(self):
		auth = GarageAuth(self._config)
		self.assertEqual(6, int(auth.location( (0,0.1) )))
		self._config.reload.assert_called_with()


if __name__ == '__main__':
    unittest.main()