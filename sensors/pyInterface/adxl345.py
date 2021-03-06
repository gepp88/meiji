#!/usr/bin/python
import time
from time import sleep
import smbus
import math
import numpy as np

logpath = 'log/acc.csv'
logpathRaw = 'log/accRaw.csv'

class Adxl(object):
	
	# Initialized Adxl345
	#	
	# PARAM:
	#	bus_nr   : number of i2c adapter to access
	# 	address  : device address to communicate with
	#	gRange   : Acceleration resolution
	#			 0 -> 2g
	#			 1 -> 4g
	#			 2 -> 8g
	#			 3 -> 16g
	def __init__(self, bus_nr, address, gRange):

		self.bus = smbus.SMBus(bus_nr)
		self.address = address
		
		self.gRange = gRange
		
		self.gainAccx2g = 0.0039
		self.gainAccy2g = 0.0039
		self.gainAccz2g = 0.0039

		self.gainAccx4g = 0.0078
		self.gainAccy4g = 0.0078
		self.gainAccz4g = 0.0078

		self.gainAccx8g = 0.0156
		self.gainAccy8g = 0.0156
		self.gainAccz8g = 0.0156

		self.gainAccx16g = 0.0312
		self.gainAccy16g = 0.0312
		self.gainAccz16g = 0.0312

		self.EARTH_GRAVITY_MS2   = 9.80665		
		
		# Power management registers
		self.power_mgmt_1 = 0x6b
		self.adxl345_power_ctl = 0x2d
		self.power_mgmt_2 = 0x6c
		self.adxl345_res_ctl = 0x31

		# Resolution modes:
		self.AFS_2g = 0
		self.AFS_4g = 1
		self.AFS_8g = 2
		self.AFS_16g = 3
		
		# Acc registers
		self.accx0 = 0x32
		self.accy0 = 0x34
		self.accz0 = 0x36

		#Start register
		self.AXES_DATA  = 0x32
		
		self.offx = 0.4666
		self.offy = -0.1594
		self.offz = -0.7343
	
		# This is the address read via i2cdetect
		self.address = address
		
		# Now wake the 6050 up as it starts in sleep mode
		self.bus.write_byte_data(self.address, self.adxl345_power_ctl, 8)
		if gRange == self.AFS_2g:
			afs_scale = self.AFS_2g
		elif gRange == self.AFS_4g:
			afs_scale = self.AFS_4g
		elif gRange == self.AFS_8g:
			afs_scale = self.AFS_8g
		elif gRange == self.AFS_16g:
			afs_scale = self.AFS_16g
		data_format =  afs_scale
		self.bus.write_byte_data(self.address, self.adxl345_res_ctl, data_format)
		sleep(0.500)

	# Returns the reading for each axis. 
	#
        # PARAM:
	#	@ gforce:
        #    	False (default): result is returned in m/s^2
        #    	True           : result is returned in gs
	#  	@ round:
	#	False	       : raw value
	#  	True	       : Rounds to 4th digit from dec point
   	def getAxes(self, gforce = False, roundAcc = True):
        	bytes = self.bus.read_i2c_block_data(self.address, self.AXES_DATA, 6)
        
	        x = bytes[0] | (bytes[1] << 8)
	        if(x & (1 << 16 - 1)):
       		    x = x - (1<<16)

	        y = bytes[2] | (bytes[3] << 8)
        	if(y & (1 << 16 - 1)):
	            y = y - (1<<16)

        	z = bytes[4] | (bytes[5] << 8)
	        if(z & (1 << 16 - 1)):
	            z = z - (1<<16)

		if self.gRange == self.AFS_2g:
		        x = x * self.gainAccx2g
        		y = y * self.gainAccx2g
	        	z = z * self.gainAccx2g
		elif self.gRange == self.AFS_4g:
		        x = x * self.gainAccx4g
        		y = y * self.gainAccx4g
	        	z = z * self.gainAccx4g
		elif self.gRange == self.AFS_8g:
		        x = x * self.gainAccx8g
        		y = y * self.gainAccx8g
	        	z = z * self.gainAccx8g
		elif self.gRange == self.AFS_16g:
		        x = x * self.gainAccx16g
        		y = y * self.gainAccx16g
	        	z = z * self.gainAccx16g
	        
		if gforce == False:
	            x = x * self.EARTH_GRAVITY_MS2
	            y = y * self.EARTH_GRAVITY_MS2
	            z = z * self.EARTH_GRAVITY_MS2

		if roundAcc:		
        		x = round(x, 4)
	        	y = round(y, 4)
	        	z = round(z, 4)
		
	 	x = x - self.offx
		y = y - self.offy
		z = z - self.offz

        	return {"x": x, "y": y, "z": z}	

	def getRoll(self):
		acc = self.getAxes()
		return self.get_x_rotation(acc['x'],acc['y'],acc['z'])		
	def getPitch(self):
		acc = self.getAxes()
		return self.get_y_rotation(acc['x'],acc['y'],acc['z'])

	def get_y_rotation(self,x,y,z):
		radians = math.atan2(x, self.dist(y,z))
		return -math.degrees(radians)

	def get_x_rotation(self,x,y,z):
		radians = math.atan2(y, self.dist(x,z))
		return math.degrees(radians)

	def dist(self,a,b):
	    return math.sqrt((a*a)+(b*b))
	
	def toG(self,axes):
		G = {"x": "N", "y": "N", "z": "N"}
		if len(axes) == 3:
			G['x'] = round(axes['x']*1/self.EARTH_GRAVITY_MS2,4)
			G['y'] = round(axes['y']*1/self.EARTH_GRAVITY_MS2,4)
			G['z'] = round(axes['z']*1/self.EARTH_GRAVITY_MS2,4)
		else :
			print "Warning - toG() wrong type received"
		return G

if __name__ == "__main__":
        try:
	    f = open(logpath,'wa')
        except OSError as e:
            if e.errno == errno.ENOENT:
                # do your FileNotFoundError code here
                print("File does not exist")
                f = open(logpath, 'w')
            else:
                print("File does not exist")
                raise
	F = open(logpathRaw,'wa+')
	shutdown = 0
	N = 200

	# adxl(i2c_adapter,bus_nr,resolution)
	#	[0,1,2,3] for [2g,4g,8g,16g]
	adx = Adxl(1,0x53,0)	
	print "Resolution: " ,adx.gRange 
	
	while not shutdown == N:
		shutdown = shutdown + 1
		
		axes = adx.getAxes()
		axesG = adx.toG(axes)
		print "\n\nAcc X: ", axes['x'] , "m/s^2"
		print "Acc X: ", axesG['x'], "G\t"
	
		print "\n\nAcc Y: ", axes['y'] , "m/s^2"
		print "Acc Y: ", axesG['y'], "G\t"

		print "\n\nAcc Z: ", axes['z'] , "m/s^2"
		print "Acc Z: ", axesG['z'], "G\t"

		print "\n\nx rotation: " , adx.getRoll()
		print "y rotation: " , adx.getPitch()		
		
		F.write('A,')
		F.write(str(axes['x']))
		F.write(',') 
		F.write(str(axes['y']))
		F.write(',') 
		F.write(str(axes['z']))
		F.write(',')
		F.write(str(shutdown))
		F.write(',z\n')

		f.write('A,')
		f.write(str(axes['x']))
		f.write(',') 
		f.write(str(axes['y']))
		f.write(',') 
		f.write(str(axes['z']))
		f.write(',')
		f.write(str(shutdown))
		f.write(',z\n')
		time.sleep(0.1)
	
	f.close()
	F.close()
