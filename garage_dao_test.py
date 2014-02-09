import unittest
import os
import os.path
import io

from garage_dao import GarageDao

class TestGarageDao(unittest.TestCase):

	_db_file="garage_dao_test.db"

	def setUp(self):
		if os.path.exists(TestGarageDao._db_file): os.remove(TestGarageDao._db_file)
		self.garage_dao = GarageDao(db_file=TestGarageDao._db_file)
		
	def tearDown(self):
		if os.path.exists(TestGarageDao._db_file): os.remove(TestGarageDao._db_file)
	
	def test_state_none_on_creation(self):
		self.assertIsNone( self.garage_dao.door_status() )
		
		
	def test_state_after_update(self):
		self.garage_dao.update_status("test", "closing")
		self.garage_dao.update_status("test", "opened")
		self.garage_dao.update_status("test", "closed")
		self.assertEqual( "closed", self.garage_dao.door_status() )

	def test_last_state_transition_from(self):
		self.assertEqual(0, self.garage_dao.last_state_transition_from('closed') )
		self.garage_dao.update_status("test","closing", update_time=0)
		self.assertEqual(0, self.garage_dao.last_state_transition_from('closed') )
		self.garage_dao.update_status("test","closed", update_time=1)
		self.assertIsNone( self.garage_dao.last_state_transition_from('closed') )
		self.garage_dao.update_status("test","opening", update_time=2)
		self.assertEqual(2, self.garage_dao.last_state_transition_from('closed') )
		self.garage_dao.update_status("test","opened", update_time=3)
		self.assertEqual(2, self.garage_dao.last_state_transition_from('closed') )
		self.garage_dao.update_status("test","closing", update_time=4)
		self.assertEqual(2, self.garage_dao.last_state_transition_from('closed') )
		self.garage_dao.update_status("test","closed", update_time=5)
		self.assertIsNone( self.garage_dao.last_state_transition_from('closed') )

		self.assertEqual(5, self.garage_dao.last_state_transition_from('closing') )
		self.assertEqual(3, self.garage_dao.last_state_transition_from('opening') )

	def test_audit_history(self):
		self.garage_dao.update_status("test","closing", update_time=5)
		self.garage_dao.update_status("test","closed", update_time=3600)
		self.garage_dao.update_status("test","closed", update_time=4640)

		expected = """|1|test|closing|Thu Jan  1 00:00:05 1970|
|2|test|closed|Thu Jan  1 01:00:00 1970|
|3|test|closed|Thu Jan  1 01:17:20 1970|
"""
		
		output = io.StringIO()
		self.garage_dao.audit_history(output)
		self.assertEqual(expected, output.getvalue())
		output.close()



	
if __name__ == '__main__':
	unittest.main()