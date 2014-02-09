Raspberry Pi Garage Door REST server

Used to control an automatic garage door opener, features include:

* Activate door open/close/stop
* Email notification when door remains open for a set period
* Sensing door state changes

[**TODO list**](https://gist.github.com/drweaver/8904740)

##Architecture & Design

* Python3 (unit test framework not compatible with python2)
* [Bottle](http://bottlepy.org/) to manage REST service
* [CherryPy](http://www.cherrypy.org) for HTTP server
* [RPIO](https://pypi.python.org/pypi/RPIO) Raspberry Pi GPIO to control/sense door state 
* Pyhon finite state machine [fysom](https://github.com/oxplot/fysom) to manage door states and events
* sqlite database to store state
* Google Web Toolkit (GWT) browser interface [Garage Control](https://github.com/drweaver/gwt_garage_control)
* Google OAuth reverse proxy (written in GO) for authentication and authorisation [google_auth_proxy](https://github.com/drweaver/google_auth_proxy)

```
user ----> router [port forward] ----> oauth proxy ----> py_garage_server ----> garage.db
                                                                        \-----> GPIO -----> Relay/Sensors
```

If not requiring external access or for testing can go directly from 
user to py_garage_server by disabling auth in config (see below) without
the need for google_auth_proxy
																		
##Electronics

To build the electronics - see README and diagrams in the [electronics folder](electronics/README.md)

##Browser app

Download [garagecontrol-client.zip](https://github.com/drweaver/gwt_garage_control/releases/latest)

Put file in www folder and unzip: 
```bash
unzip garagecontrol-client.zip .
```

Should create following file structure:
```
www/GarageControl.html
www/ico/[several images]
www/garagecontrol/[gwt javascript files] 
```

##Dependencies

Can be installed with following commands
```bash
sudo apt-get install python3 python3-pip
sudo pip-3.2 install bottle RPi.GPIO geopy CherryPy mock
```
