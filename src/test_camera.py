from Camera import *
import cv2
import sys


if __name__ == '__main__':
    if len(sys.argv) < 2:
        exit("Must specify output filename")
    
    bogiecam = BogieCamera()
    img = bogiecam.shoot()
    cv2.imwrite(sys.argv[1], img)
