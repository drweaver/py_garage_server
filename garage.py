from fysom import Fysom

def dummy_door_switch_callback(e):
	pass
	
def dummy_notify_callback(e):
	pass
				  
class Garage(Fysom):
	opened = 'opened'
	closed = 'closed'
	stopped_on_opening = 'stopped on opening'
	stopped_on_closing = 'stopped on closing'
	opening = 'opening'
	closing = 'closing'
    
	close = 'close'
	open = 'open'
	stop = 'stop'


		
	def __init__(self, initial='closed', door_switch_callback=dummy_door_switch_callback):
		super(Garage,self).__init__({ 'initial': initial,
              'events': [
                  {'name': Garage.close, 'src': [Garage.opened, Garage.stopped_on_opening], 'dst': Garage.closing},
                  {'name': Garage.open, 'src': [Garage.closed, Garage.stopped_on_closing], 'dst': Garage.opening},
				  
				  {'name': Garage.stop, 'src': Garage.opening, 'dst': Garage.stopped_on_opening},
                  {'name': Garage.stop, 'src': Garage.closing, 'dst': Garage.stopped_on_closing},

				  
				  ],
			  'callbacks': {
					'onbeforeclose': door_switch_callback,
					'onbeforeopen': door_switch_callback,
					'onbeforestop': door_switch_callback,
			  }
				  })
				  
	
		
