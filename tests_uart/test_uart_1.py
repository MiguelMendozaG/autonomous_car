#!/home/mendel/.virtualenvs/cv/bin/python
import cv2 as cv
import time
from periphery import Serial


serial = Serial("/dev/ttymxc2", 9600)
#i2c2 = I2C("/dev/i2c-1")
#pwm = PWM(0, 0)

while(1):
    time.sleep(5)
    serial.write(b"2!")
    print ("2")
