# Nathan Harmon
# https://github.com/nharmon/bogie-five
#
# Object following demonstration
#
from Motion import *
from Vision import *
import cv2
import sys
import time

def follow(target, speed=100):
    """Track and move toward the object specified
    
    :param target (numpy.array): Object image
    :param speed (int): 0<x<254, Maximum motor speed 
    """
    drive = Drive()
    vision = Vision()
    img = vision.shoot()

    tracker = Tracker(target, img)
    
    while True:
        # Update image tracker with new image taken
        img = vision.shoot()
        pos = tracker.track(img)
        
        # If target wasn't found, turn 0.5 radians to the right and try again.
        # Otherwise, use the X coordinate of the target position in the camera
        # as the steering input.
        # TODO: Implement a smoothening method in case the camera isn't
        #       completely straight (it never is)
        if pos == False:
            drive.turn(0.5)
        else:
            steering = ((2. * tracker.center[0]) / img.shape[1]) - 1
            #drive.drive(speed,steering)
            #time.sleep(0.5)       # Do we really need to delay?
    
    drive.shutdown()
    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        exit("Must specify target image file")
    
    try:
        target = cv2.imread(sys.argv[1])
    except:
        exit("Problem loading target image file")
    
    follow(target)
