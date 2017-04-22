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
    tracker = Tracker(target, img, 250)
    img_index = 0
    i = 0
    while True:
        img = bogiecam.shoot()
        for _ in range(25): # Attempt max 25 iterations of PF
            found = tracker.track(img)

            # Testing / Diagnostic
            img_index += 1
            t_img = genTrackingImg(img, tracker)
            t_target = tracker.target
            t_img[0:t_target.shape[0],0:t_target.shape[1]] = t_target
            cv2.imwrite('../../output/'+str(img_index)+'.jpg',t_img)
            cv2.imwrite('../../output/latest.jpg',t_img)
            #cv2.imwrite('../../output/'+str(img_index)+'_raw.jpg',img)
            #cv2.imwrite('../../output/latest_raw.jpg',img)
            print img_index, tracker.minrw, tracker.maxrw
            # End Testing / Diagnostic
            
            # If target is locked on, proceed.
            if found:
                break

            drive.stop()
            
        else: # Target not found, turn 0.5 radians to the right
            drive.turn(0.5)
            tracker.genNewParticles(100)
            continue
        
        # If target is found, Use the X coordinate of the target position in 
        # the camera as the steering input.
        # TODO: May need to implement PID if camera isn't perfectly straight
        steering = ((2. * tracker.center[1]) / img.shape[1]) - 1
        print steering
        drive.drive(speed,steering)
        
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
    target = tracker.target
    if center is not None:
        cv2.rectangle(out, (int(center[1]) - target.shape[1]/2,
                            int(center[0]) - target.shape[0]/2),
                           (int(center[1]) + target.shape[1]/2,
                            int(center[0]) + target.shape[0]/2),
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
