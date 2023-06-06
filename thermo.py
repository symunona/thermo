#!/usr/bin/python

import RPi.GPIO as GPIO
import time
import datetime
import Adafruit_MCP9808.MCP9808 as MCP9808
import os.path
import leds

import requests
import json

temp_file = 'thermo/temp' # set
current_file = 'thermo/measured' #measured
mode_file = 'thermo/mode'
log_file = 'thermo/pi.log'

# url_root = 'http://thermo.tmpx.space/'
url_root = 'http://127.0.0.1:3005/'

# limits
max_temp = 28
min_temp = 0

# reverse LSB, display ports
# these are the LEDS ports that show the binary display.
#         16   8   4  2  1
output = [26, 19, 13, 6, 5]

log_file = outputFile = open(log_file, "a", 0)

def post(route, data):
	try:
		response = requests.post(url_root + route, data=data)
		if (response.ok):
			return json.loads(response.content)
		else:
			log.write('API error ' + response)
	except:
		log.write('network connection error')

# Timestamp generator function
def ts():
	return datetime.datetime.now().isoformat()

# Logging to file
def log(srt):
	log.write('[' + ts() + '] ' + srt + '\n')
	post('log', '{"message": "' + srt + '"}')

# output relay
switch = 4

# input buttons: up, down, and display, that shows the current temperature when pressed
up_pin = 12
down_pin = 20

# @Deprecated
display_pin = 16

input = [up_pin, down_pin, display_pin]

# initial dummy
last_valid_reading = 25

# Debounce
last_button_update = datetime.datetime.now()
DEBOUNCE_TIME = 0.1

# default if there is no temp file value
temp = 16

#even if temp did not change, save the file to show that the script is running
UPDATE = 300

# Initialize communication with the sensor.
sensor = MCP9808.MCP9808()
sensor.begin()

temperatures = [10, 16, 18, 20,  22, 24, 26, 28]

# For some reason, the current temp is off by about 2 degrees.
# This value will be substracted from the actual measured temp.
TEMP_MEASURE_OFFSET = 2

def get_temp_from_sensor():
	# we need to sanitize the result, because I broke the sensor:
	# every once in a while, we get a bit off, which generates a
	# a value well outside the range. When temp is outside of reasonable
	# reading (between 10-30 degrees) let's ignore the data
	global last_valid_reading
	global TEMP_MEASURE_OFFSET

	new_value = int(round(sensor.readTempC())) - TEMP_MEASURE_OFFSET

	if new_value < 10:
		new_value = last_valid_reading
	if new_value > 30:
		new_value = last_valid_reading

	if (last_valid_reading != new_value):
		log('Measured temp updated from ' + str(last_valid_reading) + ' to ' + str(new_value))

	last_valid_reading = new_value

	return new_value

# just write the temp file and close it, so the cloud will do the rest
def save_temp():
	global temp
	file = open( temp_file, 'w' )
	file.write(str(temp))
	file.close()

# try to read the temp file. update our current value, if
# 	- our value is different from the file's (remote update)
#	- our value is passed a certain update treshold (300)
#		this is the keep alive stat so we know the last update
#		has happened, the system is up. The last write time
#		gets transfered in the file to the cloud. On the
#		cloud we read that time and send it out to the page,
#		so if the file did not get updated recently, we'll know
#		that probably the service is down.
#	- if any exception happens, e.g. file does not exist:
#		just write the current temp, so we can recover.
def update_cur():
	global UPDATE
	current = get_temp_from_sensor()
	write = False
	try:
		file = open( current_file, 'r' )
		if ( int(file.read()) != current ):
			write = True

		mtime = os.path.getmtime(current_file)
		if (time.time() - UPDATE  > mtime):
			write = True
	except:
		write = True

	if (write):
		file = open( current_file, 'w' )
		file.write( str(current) )
		file.close()

def get_current_temp_index():
	global temp
	global temperatures
	index = 0
	while (index < len(temperatures) and temp > temperatures[index]):
		index+=1
	return index

def get_up_temp():
	global temperatures
	index = get_current_temp_index()
	if (index < len(temperatures) - 1):
		return temperatures[index + 1]
	return temperatures[index]

def get_down_temp():
	global temperatures
	index = get_current_temp_index()
	if (index > 0):
		return temperatures[index - 1]
	return temperatures[index]

def btn_up( v ):
	global temp
	global last_button_update

	# Check fro debounce time
	last_button_update_diff = (datetime.datetime.now() - last_button_update)

	if (last_button_update_diff.total_seconds() < DEBOUNCE_TIME):
		return

	last_button_update = datetime.datetime.now()

	temp = get_up_temp()

	save_temp()
	display(temp)
	log('BTN Up pressed')
	post('set', '{"temp": "' + str(temp) + '", "type": "button"}')

def btn_down( v ):
	global temp
	global last_button_update

	# Check fro debounce time
	last_button_update_diff = (datetime.datetime.now() - last_button_update)

	if (last_button_update_diff.total_seconds() < DEBOUNCE_TIME):
		return

	last_button_update = datetime.datetime.now()
	temp = get_down_temp()
	save_temp()
	display(temp)
	log('BTN Down pressed')
	post('set', '{"temp": "' + str(temp) + '", "type": "button"}')

# show the temperature on the displays for a short period of time
def btn_mode( v ):
	global temp
	global display_pin
	if (GPIO.input(display_pin)):
		display( get_temp_from_sensor() )
	else:
		display ( temp )

# displays the value on the binary output
def display( val ):
	j = 0
	leds.updateSetTemp( val )
	# for out in output:
    #             GPIO.output(out, int(format(val,'05b')[j]))
    #             j = j + 1

def init_gpio():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	for out in output:
		GPIO.setup(out, GPIO.OUT)

	# to relay
	GPIO.setup( switch, GPIO.OUT )

	for out in output:
		GPIO.output(out, 1)

	time.sleep(1)

	for out in output:
		GPIO.output(out, 0)

	time.sleep(1)

def init_input():
	for i in input:
		GPIO.setup(i, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

	GPIO.add_event_detect(up_pin, GPIO.BOTH, btn_up)
	GPIO.add_event_detect(down_pin, GPIO.BOTH, btn_down)
	GPIO.add_event_detect(display_pin, GPIO.RISING, btn_mode)


def read_temp_from_file():
	global temp
	try:
		file = open( temp_file, 'r' )
		new_temp = int(file.read())
		if ( temp != new_temp ):
			log('temp changed from file from ' + str( temp ) + ' to ' + str( new_temp ) + '\n' )
		temp = new_temp
	except:
		log.write("Error reading settings file, going with default 16\n")
		temp = 16

# Hit the aPI for the new value, see if it's updated, log if it's different!
def read_temp_from_api():
	global temp
	try:
		response_json = post('status')
		new_temp = response_json['temp']
		if (new_temp != temp):
			log('API returned different value than local: ' + new_temp + ' != ' + temp)
			temp = new_temp
		return new_temp
	except:
		log('Error reading value from API')
		temp = 16
		return False

def update_switch():
	global temp
	current = get_temp_from_sensor()
	if ( temp < current ):
		if ( GPIO.input(switch) != 0 ):
			log('Reached ' + str( temp ) + ' switching OFF (current '+ str( current ) +')')

		GPIO.output(switch, 0)

	elif ( temp > current ):
		if ( GPIO.input(switch) == 0 ):
			log('Reached ' + str( temp ) + ' switching ON mode (current ' +  str( current )  +')')
		GPIO.output(switch, 1)

log('---------------------------------')
log('Init GPIO')
init_gpio()

log('Init Button Handlers')
init_input()

log('Init LEDs')
leds.init(temperatures)

log('Reading temperature from sensor...')
get_temp_from_sensor()
log('Initial temperature MEASURED: ' + last_valid_reading)

initial_request = read_temp_from_api()
if (initial_request == False):
    read_temp_from_file()
    log('Initial temperature SET from FILE: ' + last_valid_reading)
else:
	log('Initial temperature SET by API: ' + last_valid_reading)

log("Bond's Thermo Service Started")
log("---")


while True:
	update_cur()
	read_temp_from_api()

	leds.updateTemp( get_temp_from_sensor() )
	leds.updateSetTemp( temp )
	time.sleep(3)
	update_switch()

