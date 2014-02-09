from garage_config import GarageConfig
import unittest
import os, os.path

file='garage_config_test.json'

class GarageConfigTest(unittest.TestCase):

	def setUp(self):
		if os.path.exists(file): os.remove(file)

	def tearDown(self):
		if os.path.exists(file): os.remove(file)
		
	def test_load_and_reload(self):
		with open(file, 'w') as f:
			f.write('{ "key1": "value1", "key2": "value2" }')
		
		c = GarageConfig(file=file)
		self.assertEqual('value1', c['key1'])
		self.assertEqual('value2', c['key2'])
		self.assertIsNone( c['key3'] )
	
		if os.path.exists(file): os.remove(file)
		with open(file, 'w') as f:
			f.write('{ "key1": "value3", "key2": "value4" }')
		
		c.reload()
		
		self.assertEqual('value3', c['key1'])
		self.assertEqual('value4', c['key2'])
		self.assertIsNone( c['key3'] )

	def test_initial_load_failure(self):
		with open(file, 'w') as f:
			f.write('{ "key1": "value1" "key2": "value2" }')
		
		with self.assertRaises(Exception):
			c = GarageConfig(file=file)

	def test_reload_failure(self):
		with open(file, 'w') as f:
			f.write('{ "key1": "value1", "key2": "value2" }')
		
		c = GarageConfig(file=file)
		if os.path.exists(file): os.remove(file)
		with open(file, 'w') as f:
			f.write('{ "key1": "value3" "key2": "value4" }')
			
		c.reload()
		self.assertEqual('value1', c['key1'])
		self.assertEqual('value2', c['key2'])
		self.assertIsNone( c['key3'] )