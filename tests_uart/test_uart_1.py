#!/home/mendel/.virtualenvs/cv/bin/python
import cv2 as cv
from periphery import  PWM


#serial = Serial("/dev/ttymxc0", 9600)
#i2c2 = I2C("/dev/i2c-1")
pwm = PWM(0, 0)

while(1):
    
    print ("2")
