[![Build Status](https://travis-ci.org/drweaver/py_garage_server.png?branch=master)](https://travis-ci.org/drweaver/py_garage_server)

Raspberry Pi Garage Door REST server

Used to control an automatic garage door opener, features include:

* Activate door open/close/stop
* Email notification when door remains open for a set period
* Sensing door state changes

See the [**Blog Post**](http://drweaveruk.blogspot.co.uk/2014/02/raspberry-pi-garage-door-opener.html)

See the [**ToDo list**](https://gist.github.com/drweaver/8904740)

##Architecture & Design

* Python3 (unit test framework not compatible with python2)
* [Bottle](http://bottlepy.org/) to manage REST service
* [CherryPy](http://www.cherrypy.org) for HTTP server
* [RPIO](https://pypi.python.org/pypi/RPIO) Raspberry Pi GPIO to control/sense door state 
* Pyhon finite state machine [fysom](https://github.com/oxplot/fysom) to manage door states and events
* sqlite database to store state
* Smart browser interface [Garage Control](https://github.com/drweaver/dart_garage_control)
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

Download [garagecontrol-client.zip](https://github.com/drweaver/dart_garage_control/releases/latest)

Put file in application folder and unzip to www: 
```bash
unzip garagecontrol-client.zip -d www
```

Should create following file structure:
```
www/GarageControl.html
www/ico/[several images]
www/[more .dart and .js files]
```

Once setup, the browser app can be accessed from URL:

```
http[s]://<IP or domain>:<port>/gc/
```

##REST URLs

Available URLs which respond to POST requests
```
/gc/garagedoor/state => get the current state
/gc/garagedoor/open  => open the door
/gc/garagedoor/close => close the door
/gc/garagedoor/stop  => stop the door
/gc/garagedoor/authlocation => check location is authorised for open command
```

Calling a command will trigger the door switch or have no effect if the transition is not allowed (e.g. calling stop in opened state)

The ```open``` and ```authlocation``` commands require 2 parameters: ```lat``` and ```lng```.

All responses are by JSON e.g.:
```
{ 'auth': 'OK', 'state': 'opening' }
```


##Dependencies

Can be installed with following commands
```bash
sudo apt-get install python3 python3-pip
sudo pip-3.2 install bottle RPi.GPIO geopy CherryPy mock
```

##Configuration

Application settings should be placed in garage_config.json.  Make a copy of the [template file](_garage_config.json) and edit with required configuration:

```bash
cp _garage_config.json garage_config.json
```

Most settings are editable at runtime
e.g. changing authorised list can be made without restarting the server.

For GPIO port numbering [see here](http://pi.gadgetoid.com/pinout/gpio)

* **door_switch_enabled** Set to false during testing - disables invoking relay GPIO
* **notify_enabled** Set to true to enable email notification
* **state_monitor_enabled** Set to true to enable periodic check/notification of door open status
* **port** HTTP Port to listen on
* **authorised** List of gmail addresses authorised (see [google_auth_proxy](https://github.com/drweaver/google_auth_proxy) - address is sent in the X-Forwarded-For header)
* **smtp_server** / **smtp_port** SMTP server / port
* **smtp_sender** email of sender, usually your address
* **smtp_recipient** email of person/people to notify 
* **smtp_pwd_file** location of file containing password to email server
* **lat** / **lng** Latitude/Longitude of your garage used during location authorisation.  [Use this](http://itouchmap.com/latlong.html) to find out
* **relay_channel** GPIO port used to control the relay
* **closed_channel** / **opened_channel** GPIO port used to detect sensor on door closed / opened
* **debounce_timeout_ms** De-bounce timeout
* **distance_limit_miles** Distance allowed from lat/lnb coords given above allowed to use Open command
* **state_monitor_limit_mins** Limit in minutes before sending notification of open state
* **state_monitor_interval_mins** Period to check door state
* **logfile** Location to write log file

##Running

The service must be run as root to bind to the GPIO ports.  The included run.sh can be used to start the server.
```bash
./run.sh &
tail -f nohup.out
```

Alternatively, install and register as a system service.  The advantage is if your RPi is rebooted, the service wil automatically be started when the system returns.  See the [init.d](init.d) folder for instructions.
