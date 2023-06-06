#!/usr/bin/env python

# This file shows utility functions for expressing how cold it is on a led strip.

import time
from neopixel import Adafruit_NeoPixel, Color

import argparse
import multiprocessing
import math

# LED strip configuration:
LED_COUNT      = 9      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 10	     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


BLACK = Color (0, 0, 0)
COLD_WHITE = Color(150, 150, 255)
WHITE = Color(255, 255, 255)
BLUE = Color(20, 20, 255)
GREEN = Color(200, 50, 50)
RED = Color(0, 255, 0)
ORANGE = Color(70, 200, 0)

RAINBOW = Color(255, 0, 0)

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)

# Intialize the library (must be called once before other functions).
strip.begin()


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def setTemp(n, marker_color):
	led_index = (n-1) % 8 + 1
	strip.setPixelColor(led_index, marker_color)
	strip.show()

def clear():
	for i in range(LED_COUNT):
		strip.setPixelColor(i, BLACK)

def displayTemp(temp):
	clear()
	if ( temp <= 0 ):
		# Super cold it is set to, just show white on the bottom and the top led.
		strip.setPixelColor(1, COLD_WHITE)
		strip.setPixelColor(LED_COUNT-1, COLD_WHITE)
		strip.show()
		return
	if ( temp <= 8 ):
		for i in range( temp + 1 ):
	                strip.setPixelColor(i, WHITE)
		strip.show()
		return
	if ( temp <= 16):
		for i in range(temp - 8 + 1):
                        strip.setPixelColor(i, BLUE)
		strip.show()
		return
	if ( temp <= 24):
		for i in range(temp - 16 + 1):
                        strip.setPixelColor(i, GREEN)
		strip.show()
		return
	if ( temp <= 32):
		for i in range(temp - 24 + 1):
                        strip.setPixelColor(i, RED)
		strip.show()
		return
	if ( temp > 32):
                strip.setPixelColor(1, ORANGE)
                strip.setPixelColor(LED_COUNT-1, ORANGE)
		strip.show()
		return


def displayTemp2(temp, setTemp, temperatures, rainbow):
	clear()
	if ( temp <= 0 ):
                strip.setPixelColor(1, COLD_WHITE)
                strip.setPixelColor(LED_COUNT-1, COLD_WHITE)
                strip.show()
                return
	if ( temp > 32):
                strip.setPixelColor(1, ORANGE)
                strip.setPixelColor(LED_COUNT-1, ORANGE)
                strip.show()
                return
	ledMeasured = 1


	# Where is the actual color?
	while ((ledMeasured < LED_COUNT) and temp > temperatures[ledMeasured-1]):		
		# print(setTemp < temperatures[led-1])
		# print(setTemp)
		# print(temperatures[led-1])

		color = wheel( (8-ledMeasured) * 8 )
		strip.setPixelColor(ledMeasured, color)

		# strip.setPixelColor(led, COLD_WHITE)
		# strip.show()
		# print('led ' + str(led) + ' - X')
		ledMeasured+=1
	
	ledSet = 1

	while ((ledSet < LED_COUNT) and setTemp > temperatures[ledSet-1]):
		ledSet+=1
	
	# If the actual temperature is lower 
	if (ledMeasured < ledSet):
		strip.setPixelColor(ledSet, rainbow)
	else:
		strip.setPixelColor(ledSet, WHITE)

	
	strip.show()

	# base = int(math.floor( (temp - 1) / 8 ) * 8)
	# offset = 160
	# where = (temp-1) % 8 + 1
	# for i in range(where):
	# 	color = wheel( -( offset + (base + offset + i) * 6 ) % 256 )
    #             strip.setPixelColor(i, color)
	# strip.show()
        # return



def displayTemp3(temp, sTemp, rainbow):
	clear()
	if ( temp <= 0 ):
                strip.setPixelColor(1, COLD_WHITE)
                strip.setPixelColor(LED_COUNT-1, COLD_WHITE)
                strip.show()
                return
	if ( temp > 32):
                strip.setPixelColor(1, ORANGE)
                strip.setPixelColor(LED_COUNT-1, ORANGE)
                strip.show()
                return

	from_temp = int(math.floor( (sTemp - 1) / 8 ) * 8)
	to_temp = from_temp + 8

	rng = range(8)
	if from_temp < temp and to_temp >= temp:
		rng = (temp-1) % 8 + 1
	else:
		if temp < from_temp:
			rng = 0
		else:
			if temp > to_temp:
				rng = 9

	base = int(math.floor( (sTemp - 1) / 8 ) * 8)
	offset = 160
	for i in range(rng):
		color = wheel( -( offset + (base + offset + i) * 6 ) % 256 )
                strip.setPixelColor(i, color)

	if temp > sTemp:
		setTemp(sTemp, WHITE)
	else:
		setTemp(sTemp, rainbow)

	strip.show()
        return


def display_loop(ns, event):
	w = 0

	for i in range(33):		
		displayTemp(i)
		#print i
		time.sleep(0.05)


	while True:
		rainbow = wheel(w % 256)
		displayTemp2(ns.temp, ns.setTemp, ns.temperatures, rainbow)
		time.sleep(0.05)
		w = w + 1


def fork_rainbow_status():
    mgr = multiprocessing.Manager()
    namespace = mgr.Namespace()
    event = multiprocessing.Event()
    p = multiprocessing.Process(target=display_loop, args=(namespace, event))
    namespace.temp = 0
    namespace.setTemp = 0
    namespace.temperatures = []
    p.start()
    return namespace

ns = fork_rainbow_status()

def updateTemp(temp):
	global ns
	ns.temp = temp

def updateSetTemp(setTemp):
	global ns
	ns.setTemp = setTemp

def init(temperatures):
	global ns
	ns.temperatures = temperatures
	print('Temp presets: ')
	print(' '.join(map(str, temperatures)))
	clear()
	strip.show()
	





# Main program logic follows:
if __name__ == '__main__':
	init()
