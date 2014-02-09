import unittest
from garage import Garage

class TestGarageDoorStateMachine(unittest.TestCase):

	def door_switch_count_increment(self, e):
		self.door_switch_count+=1
		return self.door_switch_successful

	def setUp(self):
		self.door_switch_count = 0
		self.door_switch_successful = True
		self.fsm = Garage(door_switch_callback=self.door_switch_count_increment)

	def test_initial_state(self):
		self.assertEqual(Garage.closed, self.fsm.current)

	def test_open(self):
		self.fsm.open()
		self.assertEqual(Garage.opening, self.fsm.current)		
		self.assertEqual(1, self.door_switch_count)
		
	def test_cannot_trigger(self):
		self.assertEqual(Garage.closed, self.fsm.current)
	
		self.assertTrue(self.fsm.cannot(Garage.stop))
		
		self.assertTrue(self.fsm.cannot(Garage.close))

		self.fsm = Garage(initial=Garage.opened,door_switch_callback=self.door_switch_count_increment)
		self.assertEqual(Garage.opened, self.fsm.current)
		
		self.assertTrue(self.fsm.cannot(Garage.stop))
		
		self.assertTrue(self.fsm.cannot(Garage.open))
		
		self.assertEqual(0, self.door_switch_count)
		

	def test_full_cycle_from_closed(self):
		
		self.fsm.open()
		self.assertEqual(Garage.opening, self.fsm.current)
		
		self.fsm.stop()
		self.assertEqual(Garage.stopped_on_opening, self.fsm.current)
		
		self.fsm.close()
		self.assertEqual(Garage.closing, self.fsm.current)
		
		self.assertEqual(3, self.door_switch_count)

	def test_full_cycle_from_open(self):
		

		self.fsm = Garage(initial=Garage.opened,door_switch_callback=self.door_switch_count_increment)

		self.assertEqual(Garage.opened, self.fsm.current)
		
		self.fsm.close()
		self.assertEqual(Garage.closing, self.fsm.current)
		
		self.fsm.stop()
		self.assertEqual(Garage.stopped_on_closing, self.fsm.current)
		
		self.fsm.open()
		self.assertEqual(Garage.opening, self.fsm.current)
		
		self.assertEqual(3, self.door_switch_count)
			
	def test_door_switch_fails(self):
		self.door_switch_successful = False
		self.fsm.open()
		self.assertEqual(Garage.closed, self.fsm.current)
	
	def test_initil(self):
		self.assertEqual(Garage.closed, self.fsm.current)
		self.fsm = Garage(initial=Garage.opened)
		self.assertEqual(Garage.opened, self.fsm.current)

	
if __name__ == '__main__':
	unittest.main()
	
