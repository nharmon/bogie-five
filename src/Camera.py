# Nathan Harmon
# https://github.com/nharmon/bogie-five
#
# Camera module
#
import cv2
import io
import numpy as np
import picamera
import random
import time

class BogieCamera:
    """Interface to the rover's raspberry pi camera.
    """
    def __init__(self, res=(740, 480), framerate=30):
        """Initialize the vision class
        
        :inst self.camera (picamera class): Camera object
        """
        self.camera = picamera.PiCamera()
        self.camera.resolution = res
        self.camera.framerate = framerate
        self.camera.start_preview()
        time.sleep(2)
    
    def shoot(self):
        """Takes a photo from the camera
        
        :return output (numpy.array): Photograph in array form
        """
        stream = io.BytesIO()
        self.camera.capture(stream, format='jpeg')
        data = np.fromstring(stream.getvalue(), dtype=np.uint8)
        output = cv2.imdecode(data, 1)
        return output
