#!/home/mendel/.virtualenvs/cv/bin/python

from periphery import Serial
import time


uart3 = Serial("/dev/ttymxc2", 9600)


def output_uart():
    uart3.write(b'popo');
	time.sleep(5)
    uart3.write(b'popo');
