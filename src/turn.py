#!/usr/bin/python
# Nathan Harmon
# https://github.com/nharmon/bogie-five
#
# Turn program
#
from Motion import *
import sys

if __name__ == '__main__':
    if len(sys.argv) < 2:
        exit("Must specify target image file")
    
    try:
        drive = Drive()
        drive.turn(float(sys.argv[1]))
    except:
        exit("Specify direction change")
