# Nathan Harmon
# https://github.com/nharmon/bogie-five
#
# Navigation module
#
import numpy as np

class graphSLAM:
    """Implementation of a graph-based Simultaneous Localization and 
       Mapping (SLAM) algorithm.
    """
    def __init__(self, measurement_noise=2, motion_noise=2):
        """Initialize the graphs
        
        Instantiates:
            self.Omega (numpy.array): Pose and landmark estimation matrix
            self.Xi (numpy.array): Vector matrix
        """
        self.Omega = np.zeros((3,3)) ###TODO: How to initialize landmarks
        self.Xi = np.zeros((3,1))    ###      Grow landmark matrix?
        self.measurement_noise = measurement_noise
        self.motion_noise = motion_noise
        
    def process(self, measurements, motion):
        """Updates Omega and Xi using new measurements and movement
        
        Parameters:
            measurements (list): Measurement vectors
            motion (list): Motion displacement vectors
        """
        for measurement in measurements:
            m = 2 * (1 + measurement[0])
            for i in range(2):
                self.Omega[i,i] += 1. / self.measurement_noise
                self.Omega[i+m,i] += -1. / self.measurement_noise
                self.Omega[i,i+m] += -1. / self.measurement_noise
                self.Omega[i+m,i+m] += 1. / self.measurement_noise
                self.Xi[i][0] += -measurement[i+1] / self.measurement_noise
                self.Xi[i+m][0] += measurement[i+1] / self.measurement_noise
        
        for i in range(2):
            self.Omega = np.insert(Omega, 2, 0, axis=0)
            self.Omega = np.insert(Omega, 2, 0, axis=1)
            self.Xi = np.insert(Xi, 2, 0, axis=0)
        
        for i in range(2):
            self.Omega[i][i] += 1. / self.motion_noise
            self.Omega[i,i+2] += -1. / self.motion_noise
            self.Omega[i+2,i] += -1. / self.motion_noise
            self.Omega[i+2][i+2] += 1. / self.motion_noise
            self.Xi[i][0] += -motion[i] / self.motion_noise
            self.Xi[i+2][0] += motion[i] / self.motion_noise
        
        a = self.Omega[:2,2:]
        b = np.linalg.inv(self.Omega[:2,:2])
        c = self.Xi[:2]

        self.Omega = self.Omega[2:,2:] - np.dot(np.dot(a.transpose(), b), a)
        self.Xi = self.Xi[2:] - np.dot(np.dot(a.transpose(), b), c)
        return True
    
    def calc_mu(self):
        """Calculate the estimated pose and landmark matrix
        
        Returns:
            mu (numpy.array): estimated localization and mapping matrix
        """
        mu = np.dot(np.linalg.inv(Omega), Xi)
        return mu
