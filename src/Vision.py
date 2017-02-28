# Nathan Harmon
# https://github.com/nharmon/bogie-five
#
# Vision module
#
import cv2
import numpy as np
import picamera
import picamera.array

class RobotVision:
    """Provides a computer vision capability to the rover using the
       raspberry pi camera.
    """
    def __init__(self, res=(320, 240), framerate=24):
        """Initialize the vision class
        
        Instantiates:
            self.camera (picamera class): Camera object
        """
        self.camera = picamera.PiCamera()
        self.camera.resolution = res
        self.camera.framerate = framerate
    
    def shoot():
        """Takes a photo from the camera
        
        Returns:
            output (np.array): Photograph in array form
        """
        buffer_x = 32 * np.ceil(self.camera.resolution[0] / 32)
        buffer_y = 16 * np.ceil(self.camera.resolution[1] / 16)
        output = np.empty((buffer_x * buffer_y * 3,), dtype=np.uint8)
        self.camera.capture(output, 'rgb')
        output = output.reshape((buffer_x, buffer_y, 3))
        output = output[:self.camera.resolution[0],
                        :self.camera.resolution[1],
                        :]
        return output
    
    def track(object):
        """Locate and track an object in the camera's field of view.
        
        Parameters:
            object (np.array): Subimage of object to be located
        
        Returns:
            center (np.array): Coordinates of the object's center
        """
        img = self.shoot()
        #TODO: implement a particle filter to locate the object
        self.particles = []
        self.weights = []
        
        
        
        return center
    
    def makePanorama(images):
        """Generate a panorama from multiple images
        
        Parameters:
             images (list): List of np.array images
        
        Returns:
             result (np.array): Panorama
        """
        #TODO: implement stiching and warping from cv2
        
        
        return result
