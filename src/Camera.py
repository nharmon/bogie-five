# Nathan Harmon
# https://github.com/nharmon/bogie-five
#
# Camera module
#
import cv2
import numpy as np
import picamera
import picamera.array
import random
import time

class BogieCamera:
    """Interface to the rover's raspberry pi camera.
    """
    def __init__(self, res=(640, 480), framerate=24):
        """Initialize the vision class
        
        :inst self.camera (picamera class): Camera object
        """
        self.camera = picamera.PiCamera()
        self.camera.resolution = res
        self.camera.framerate = framerate
        time.sleep(2)
        #self.camera.shutter_speed = 150000
        #self.camera.iso = 800
    
    def makePanorama(self, images):
        """Generate a panorama from multiple images
        
        :param images (list): List of np.array images
        
        :return result (numpy.array): Panorama
        """
        #TODO: implement stiching and warping from cv2
        
        
        return result
    
    def shoot(self):
        """Takes a photo from the camera
        
        :return output (numpy.array): Photograph in array form
        """
        # Image buffer must be multiple of 32 in x, multiple of 16 in y
        buffer_y = int(32 * np.ceil(self.camera.resolution[0] / 32.))
        buffer_x = int(16 * np.ceil(self.camera.resolution[1] / 16.))
        output = np.empty((buffer_x * buffer_y * 3,), dtype=np.uint8)
        self.camera.capture(output, 'rgb')
        output = output.reshape((buffer_x, buffer_y, 3))
        output = output[:self.camera.resolution[0],
                        :self.camera.resolution[1],
                        :]
        return output
