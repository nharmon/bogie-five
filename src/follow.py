# Nathan Harmon
# https://github.com/nharmon/bogie-five
#
# Follow object test
#
from Camera import *
from Motion import *
from Vision import *
import numpy as np
import cv2
import sys
import time

def follow(target, speed=50):
    """Track and move toward the object specified
    
    :param target (numpy.array): Object image
    :param speed (int): 0<x<254, Maximum motor speed 
    """
    drive = Drive()
    bogiecam = BogieCamera()
    img = bogiecam.shoot()
    tracker = Tracker(target, img)
    img_index = 0
    i = 0
    while True:
        # Testing / Diagnostic
        t_img = genTrackingImg(img, tracker)
        cv2.imwrite('../../output/'+str(img_index)+'.jpg',t_img)
        cv2.imwrite('../../output/latest.jpg',t_img)
        cv2.imwrite('../../output/raw.jpg',img)
        print tracker.maxrw
        img_index += 1
        # End Testing / Diagnostic
        
        # Update image tracker with new image taken
        img = bogiecam.shoot()
        pos = tracker.track(img)
        
        # If target wasn't found, try again (the particle filter will have
        # generated new random particles). After 5 attempts, turn 0.5 radians
        # to the right and start again.
        if pos == False:
            drive.stop()
            if i < 5:
                i += 1
                continue
            
            drive.turn(0.5)
            i = 0
            continue
        
        # If target is found, Use the X coordinate of the target position in 
        # the camera as the steering input.
        # TODO: May need to implement PID if camera isn't perfectly straight
        steering = ((2. * tracker.center[0]) / img.shape[1]) - 1
        drive.drive(speed,steering)
        #time.sleep(0.5)
        
    drive.shutdown()
    return True

def genTrackingImg(img, tracker):
    """Generate an image of the tracking progress
    
    :param img (numpy.array): camera image
    :return out (numpy.array): camera image with particles and
                               best guess rectangle
    """
    # Draw the particles
    out = np.copy(img)
    for u,v in tracker.particles:
        if 0 < u < img.shape[0] and 0 < v < img.shape[1]:
            cv2.circle(out, (v,u), 2, (0,255,255), -1)
    
    center = tracker.center
    object = tracker.object
    if center is not False:
        cv2.rectangle(out, (int(center[1]) - object.shape[1]/2,
                            int(center[0]) - object.shape[0]/2),
                           (int(center[1]) + object.shape[1]/2,
                            int(center[0]) + object.shape[0]/2),
                      (255,255,255), 3)
    
    return out


if __name__ == '__main__':
    if len(sys.argv) < 2:
        exit("Must specify target image file")
    
    try:
        target = cv2.imread(sys.argv[1])
    except:
        exit("Problem loading target image file")
    
    follow(target)
