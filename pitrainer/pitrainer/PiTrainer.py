#!/usr/bin/python3

import socket
import socketserver
import smbus  # need to get smbus library by the following command $sudo apt-get install python-smbus
import math
import time 
import pigpio # For managing any I/O 
import datetime
import logging 
import configparser

import threading
import xml.etree.ElementTree as ElementTree
import queue


import signal

import scrollphathd
from scrollphathd.fonts import font5x7

# Custom Libraries
from Rumblers import RumbleThread
from UDPHandlers import UDPRecHandler, UDPRecThread
from CountDisplays import CountDisplayHandler

print("""
Scroll pHAT HD: Hello World

Scrolls "Hello World" across the screen
in a 5x7 pixel large font.

Press Ctrl+C to exit!

""")

# This bit just gets the pigpiod daemon up and running if it isn't already.  
import subprocess
import os 

p = subprocess.Popen(['pgrep', '-f', 'pigpiod'], stdout=subprocess.PIPE)
out, err = p.communicate()

if len(out.strip()) == 0:
    os.system("sudo pigpiod")
# End of getting pigpiod running. 
	

# Set up the Pigpiod Pi.  
pi = pigpio.pi()


# GPIO Definitions for the vibrators (3 count)
Vibrators = [17, 27, 22]


# Setting up logging - add in time to it. Create a filename using time functions
Now = datetime.datetime.now()
LogFileName = "PiTrainer_" + Now.strftime("%y%m%H%M") + ".log"

# Sets up the logging - no special settings. 
logging.basicConfig(filename=LogFileName,level=logging.DEBUG)

# Setting up to read config file
config = configparser.RawConfigParser()
config.read('PiTrainer.cfg')


#Get the sampling rate to use  
SAMPLE_SLEEP = config.getint('TIMING', 'SAMPLE_SLEEP')

# Get Display Sample - how often to update the display based on how many samples are taken before displaying
DISPLAY_FREQ = config.getint('TIMING', 'DISPLAY_FREQ')

# Get Skip Threshold - the g force that has to be exceeded to register one skip count.  
SKIP_THRESHOLD = config.getint('THRESHOLDS', 'SKIP_THRESHOLD')
	
# Get Server Information 
SERVER_HOST= config['SERVER']['SERVER_HOST']
SERVER_PORT= int (config['SERVER']['SERVER_PORT'])


# Power management registers for accelerometer
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

# Standard reading functions for Accelerometer
def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def dist(a,b):
    return math.sqrt((a*a)+(b*b))

def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)

def GetScaledAccelValues():
	try:
		# Grab Accelerometer Data 
		accel_xout = read_word_2c(0x3b)
		accel_yout = read_word_2c(0x3d)
		accel_zout = read_word_2c(0x3f)
	except:
		print("** Read failed - assume 0 accel")
		accel_xout =0
		accel_yout =0
		accel_zout =0
		
	ScaledAccel = [accel_xout / 16384.0 *8, accel_yout / 16384.0 *8, accel_zout / 16384.0*8]
	return ScaledAccel
	
	
# Start talking to accelerometer - standard I2C stuff.  
bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x68       # This is the address value read via the i2cdetect command

# Now wake the 6050 up as it starts in sleep mode
bus.write_byte_data(address, power_mgmt_1, 0)

# Write the setup to the accelerometer - value of 3 in AFS_SEL gives accel range of 16g.  The register to use is 1C (28 decimal)
bus.write_byte_data(address, 0x1C, 0b00011000)

# Adjust sensitivity of accelerometer to maximum of 16g.  

''' Not using gyro yet. - Not sure if I need/want it.  
print( "gyro data")
print( "---------")

gyro_xout = read_word_2c(0x43)
gyro_yout = read_word_2c(0x45)
gyro_zout = read_word_2c(0x47)

print ("gyro_xout: ", gyro_xout, " scaled: ", (gyro_xout / 131))
print ("gyro_yout: ", gyro_yout, " scaled: ", (gyro_yout / 131))
print ("gyro_zout: ", gyro_zout, " scaled: ", (gyro_zout / 131))

print ("accelerometer data")
print ("------------------")
'''

# Max acceleration rate in the display period
MaxAccel = 0
SampleNum = 0
SkipCount = 0 

# Creat a queue for talking between the threads
q = queue.Queue()

# Queue to send Rumble Requests.  
RumbleQ = queue.Queue()







# Start up the Rumble Thread.  
UDPRecThreadHdl = UDPRecThread(1, "UDP Rec Thread", 1) 
UDPRecThreadHdl.start()





# Start up the Rumble Thread.  
RumbleThreadHdl = RumbleThread(1, "Rumble Thread", 1) 
RumbleThreadHdl.start()


#with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as ServerSocket:
	
# Connect to server and send data
#ServerSocket.setblocking(False)
#data = "<User>pi-fighter User is {} </User>" .format(UserName)	
# Send data to the server
#ServerSocket.sendall(bytes(  data + "\n", "utf-8"))

# Receive data from the server and shut down
#received = str(sock.recv(1024), "utf-8")
	
#print("Sent:     {}".format(data))
#print("Received: {}".format(received))
for i in range(25,100,20):
	RumbleCmd = str("<Rumble><Vib0Str>{}</Vib0Str><Vib1Str>0</Vib1Str><Vib2Str>{}</Vib2Str><MsDuration>80</MsDuration></Rumble>".format(i, i))
	RumbleQ.put_nowait(RumbleCmd)

while(1):
	try:
		
		# Grab Accelerometer Data 
		ScaledAccel = GetScaledAccelValues() # X,Y,Z acceleration
		#print (ScaledAccel)
		date_string = datetime.datetime.now().date()
		time_string= datetime.datetime.now().time()

		TotalAccel = math.sqrt(ScaledAccel[0] **2 + ScaledAccel[1] **2 + ScaledAccel[2] **2 )
				
		# Set the sign of the acceleration by a simple sum of the components
		if ((ScaledAccel[0] + ScaledAccel[1] + ScaledAccel[2]) <0):
			TotalAccel = -1 * TotalAccel
		
		#print ("{},{},{:2.3},{:2.3f}, {:2.3f}" .format(date_string, time_string, ScaledAccel[0], ScaledAccel[1], ScaledAccel[2]))
		logging.info("{},{},{:2.3},{:2.3f}, {:2.3f}, {:2.3f}" .format(date_string, time_string, ScaledAccel[0], ScaledAccel[1], ScaledAccel[2], TotalAccel))
		
				
		# Update Accel if needed
		if (abs(TotalAccel) > MaxAccel):
			MaxAccel = abs(TotalAccel)
		
		# If Skip is detected due to the threshold being exceeded, then update the skip count
		# and put it into the queue for processing by the OLED thread.  OLED thread is too slow to 
		# keep up with the skipping and print to the OLED which has a low refresh rate.  
		if (SampleNum % DISPLAY_FREQ == 0):
			#print ("Max :", MaxAccel)
			if (MaxAccel > SKIP_THRESHOLD):
				SkipCount = SkipCount + 1 
				print (SkipCount)
				
				# Put into the queue for processing.  
				q.put_nowait(SkipCount)
				#OLED_Print(SkipCountStr,"Verdana.ttf", 20, disp.width, disp.height)
				#SkipCountInfo = "<Skip><Date>{}</Date><Time>{}</Time><SkipCount>{:d}</SkipCount></Skip>" .format(date_string, time_string, SkipCount)
				
				# Sending skip count to the server. 
				#if (ServerSocket != 0):
				#	ServerSocket.sendto(bytes(SkipCountInfo, "utf-8"), (SERVER_HOST, SERVER_PORT))
				#else:
				#	print ("No Server Socket")
			#DrawPattern(int(MaxAccel/2.1), Brightness[int(MaxAccel/2.1)])
			MaxAccel = 0
	
		time.sleep(SAMPLE_SLEEP/1000)
		SampleNum +=1
	
	except KeyboardInterrupt: 
		print ("Fine - quit see if I care - jerk")
		
		# Asks the thread to finish nicely.
		SkipCountDisplayThread.join()

		exit()
		
