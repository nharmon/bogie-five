# Nathan Harmon
# https://github.com/nharmon/bogie-five
#
# Motion module
#
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
import atexit
import numpy as np
import time

class Drive:
    """Provides the driving functions for the robot using the Adafruit DC and
       Stepper Motor HAT.
    """
    def __init__(self, hataddr=0x60):
        """Initialize the drive class
        
        Instantiates:
            self.mh (instance): Motor hat object
        """
        self.mh = Adafruit_MotorHAT(addr=hataddr)
        self.stop()
        
        # Auto-disable motors on program exit
        atexit.register(self.shutdown)
    
    def drive(self, speed=0, steering=0., distance=0):
        """Command the rover to move
        
        Parameters:
            speed (int): -255 to 255, negative vals move backward
            steering (float): -1 to 1, negative vals steer left
            distance (float): Calibrated to centimeters, Nonpositive vals
                              drive until told to stop.
        """
        speed = int(speed)
        
        if speed == 0:    # Stop
            self.stop()
            return True
        elif speed > 0:    # Move forward
            self.mh.getMotor(1).run(Adafruit_MotorHAT.FORWARD)
            self.mh.getMotor(2).run(Adafruit_MotorHAT.FORWARD)
        else:    # Move backward
            self.mh.getMotor(1).run(Adafruit_MotorHAT.BACKWARD)
            self.mh.getMotor(2).run(Adafruit_MotorHAT.BACKWARD)
        
        if steering == 0:    # Straight ahead
            self.mh.getMotor(1).setSpeed(np.abs(speed))
            self.mh.getMotor(2).setSpeed(np.abs(speed))
        elif steering > 0:    # Turn to the right
            tspeed = int((1-np.abs(steering))*np.abs(speed))
            self.mh.getMotor(1).setSpeed(np.abs(speed))
            self.mh.getMotor(2).setSpeed(tspeed)
        else:    # Turn to the left
            tspeed = int((1-np.abs(steering))*np.abs(speed))
            self.mh.getMotor(1).setSpeed(tspeed)
            self.mh.getMotor(2).setSpeed(np.abs(speed))
        
        if distance > 0:
            time.sleep(0.011 * distance) ## TODO: Calibrate
            self.stop()
        
        return True
    
    def shutdown(self):
        """Shuts down all motors
        """
        for i in range(1,5):
            self.mh.getMotor(i).run(Adafruit_MotorHAT.RELEASE)
        
        return True
    
    def stop(self):
        """Stop the robot
        """
        for i in range(1,3):
            self.mh.getMotor(i).setSpeed(0)
        
        return True
    
    def turn(self, angle=0):
        """Perform an in-place heading adjustment
        
        Parameters:
            angle (numeric): Turn angle in radians, negative is to the left
        """
        self.stop()
        dir = np.abs(angle) / angle
        if dir > 0:    # Turn right
            self.mh.getMotor(1).run(Adafruit_MotorHAT.FORWARD)
            self.mh.getMotor(2).run(Adafruit_MotorHAT.BACKWARD)
        
        else:    # Turn left
            self.mh.getMotor(1).run(Adafruit_MotorHAT.BACKWARD)
            self.mh.getMotor(2).run(Adafruit_MotorHAT.FORWARD)
        
        self.mh.getMotor(1).setSpeed(128)
        self.mh.getMotor(2).setSpeed(128)
        time.sleep(0.011 * np.abs(angle))
        self.stop()
        return True
