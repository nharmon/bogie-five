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
            self.steering (float): 
        """
        self.mh = Adafruit_MotorHAT(addr=hataddr)
        self.speed = 0
        self.steering = 0
        self.stop()
        
        # Auto-disable motors on program exit
        atexit.register(self.shutdown)
    
    def drive(self, speed=self.speed, steering=self.steering):
        """Propel the vehicle
        
        Parameters:
            speed (float): -255 to 255, negative vals move backward
            steering (float): -1 to 1, negative vals steer left
        """
        self.speed = speed
        self.steering = steering
        
        if self.speed == 0:    # Stop
            self.stop()
            return True
        elif self.speed > 0:    # Move forward
            self.mh.getMotor(1).run(Adafruit_MotorHAT.FORWARD)
            self.mh.getMotor(2).run(Adafruit_MotorHAT.FORWARD)
        else:    # move backward
            self.mh.getMotor(1).run(Adafruit_MotorHAT.BACKWARD)
            self.mh.getMotor(2).run(Adafruit_MotorHAT.BACKWARD)
        
        if self.steering == 0:    # Straight ahead
            self.mh.getMotor(1).setSpeed(self.speed)
            self.mh.getMotor(2).setSpeed(self.speed)
        elif self.steering > 0:    # Turn to the right
            self.mh.getMotor(1).setSpeed(self.speed)
            self.mh.getMotor(2).setSpeed((1-np.abs(self.steering))*self.speed)
        else:    # Turn to the left
            self.mh.getMotor(2).setSpeed(self.speed)
            self.mh.getMotor(1).setSpeed((1-np.abs(self.steering))*self.speed)
    
    def shutdown(self):
        """Shuts down all motors
        """
        self.mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        self.mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
        self.mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
        self.mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
    
    def stop(self):
        """Stop the robot
        """
        self.speed = 0
        self.mh.getMotor(1).setSpeed(0)
        self.mh.getMotor(2).setSpeed(0)
        
    
    def turn(self, angle=0):
        """Perform an in-place heading adjustment
        
        Parameters:
            angle (numeric): Degrees positive or negative to turn
        """
        self.stop()
        dir = np.abs(angle) / angle
        if dir > 0:    # Turn right
            self.mh.getMotor(1).run(Adafruit_MotorHAT.FORWARD)
            self.mh.getMotor(2).run(Adafruit_MotorHAT.BACKWARD)
        
        else:    # Turn left
            self.mh.getMotor(1).run(Adafruit_MotorHAT.BACKWARD)
            self.mh.getMotor(2).run(Adafruit_MotorHAT.FORWARD)
            
        self.mh.getMotor(1).setSpeed(32)
        self.mh.getMotor(2).setSpeed(32)
        time.sleep(0.05 * np.abs(angle))
        self.stop()
