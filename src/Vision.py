# Nathan Harmon
# https://github.com/nharmon/bogie-five
#
# Vision module
#
import cv2
import numpy as np
import picamera
import picamera.array
import random
import time

class Vision:
    """Provides a vision capability using the raspberry pi camera.
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


class Tracker:
    """Class for tracking a visual object using a particle filter.
    """
    def __init__(self, object, img, num_particles=100):
        """Initialize
        
        :param object (numpy.array): template for object we're tracking
        :param img (numpy.array): first image for tracking
        :param particles (int): number of particles to use
        
        :inst self.object (numpy.array): object template
        :inst self.img (numpy.array): current image
        :inst self.maxrw (float): current maximum raw weight
        :inst self.particles (list): initial set of filtered particles
        :inst self.weights (list): particle weights (via self.track)
        :inst self.center (tuple): best guess of where object is in image
        """
        self.object = cv2.GaussianBlur(object,(15,15),7)
        self.img = cv2.GaussianBlur(img,(15,15),7)
        self.maxrw = 0.
        
        # Generate particles randomly
        self.particles = self.genNewParticles(100)
        self.center = self.track(self.img)
    
    def compareMSE(self, img1, img2, sigma=10.):
        """Calculate the similarity of two images using Mean Squared Error.
        
        :param img1 (numpy.array): First image
        :param img2 (numpy.array): Second image
        :param sigma (float): MSE weight
        
        :return similarity (float): <=1.0 where 1.0 means images are equal
        """
        # If different shape, throw an error
        if img1.shape != img2.shape:
            raise ValueError('Images must have the same dimensions')
            return False
        
        # Calculate the Mean Squared Error between the images
        mse = np.sum((img1.astype('float') - img2.astype('float'))**2)
        mse /= float(img1.shape[0] * img1.shape[1])
        similarity = np.exp(-mse / (2 * (sigma ** 2)))
        return similarity
    
    def genNewParticles(self, num_particles=100):
        """Generate a new set particles
        
        :return (numpy.array): Array of new particles
        """
        particles = np.random.rand(num_particles,2)
        particles[:,0] *= self.img.shape[0]
        particles[:,1] *= self.img.shape[1]
        return particles.astype(int).tolist()
    
    def getParticleWeightedMean(self, particles, weights):
        """Produce the weighted mean of particles
        
        :param particles (numpy.array): Array of particle coordinates
        :param weights (numpy.array): Particle weights
        
        :return (tuple): Weighted mean
        """
        u_weighted_mean = 0.
        v_weighted_mean = 0.
        for i in range(len(particles)):
            u_weighted_mean += particles[i][0] * weights[i]
            v_weighted_mean += particles[i][1] * weights[i]

        return (int(u_weighted_mean), int(v_weighted_mean))
    
    def normWeights(self, weights):
        """Normalizes particle weights
        
        :param weights (numpy.array): Particle weights
        :returns (numpy.array): Normalized weights
        """
        if np.sum(weights) == 0: # None of the particles were valid?
            return np.ones(len(weights)) / len(weights)
        
        return weights / np.sum(weights)
    
    def resample(self, particles, weights):
        """Resample particles using a sampling wheel
        Reference: https://www.youtube.com/watch?v=wNQVo6uOgYA
        
        :param particles (list): (row,col) locations of each particle
        :param weights (list): weight of each particle
        
        :return new_particles (list): resampled particles
        """
        new_particles = []
        N = len(particles)
        index = int(random.random() * N)
        beta = 0.
        mw = max(weights)
        for i in range(N):
            beta += random.random() * 2. * mw
            while beta > weights[index]:
                beta -= weights[index]
                index = (index + 1) % N
            
            x = particles[index][0] + random.randint(-10,10)
            y = particles[index][1] + random.randint(-10,10)
            new_particles.append([x,y])
        
        return new_particles
    
    def track(self, img):
        """Guesses where our object is in the new image
        
        :param img (np.array): New image
        
        :return center (tuple): Best guess of object's center
        """
        self.img = cv2.GaussianBlur(img,(15,15),7)
        self.weights = self.weigh_particles()
        if self.maxrw < 0.1: # Wasn't found
            self.particles = self.genNewParticles(100)
            return False
        
        self.particles = self.resample(self.particles, self.weights)
        self.weights = self.weigh_particles()
        if self.maxrw < 0.1: # Wasn't found
            return False
        
        self.center = self.getParticleWeightedMean(self.particles, 
                                                   self.weights)
        return self.center
    
    def weigh_particles(self):
        """Produces a list of particle weights
        
        :return weights (list): weight of each particle
        """
        weights = []
        for i in range(len(self.particles)):
            # Construct our particle frame
            #print i
            p_t = int(self.particles[i][0] - np.floor(self.object.shape[0]/2.))
            p_b = int(self.particles[i][0] + np.ceil(self.object.shape[0]/2.))
            p_l = int(self.particles[i][1] - np.floor(self.object.shape[1]/2.))
            p_r = int(self.particles[i][1] + np.ceil(self.object.shape[1]/2.))
            try:
                p_frame = self.img[p_t:p_b,p_l:p_r]
            except:
                weights.append(0.)
                continue
            
            if p_frame.shape <> self.object.shape:    # Frame is off the image
                weights.append(0.)
            else: 
                similarity = self.compareMSE(p_frame, self.object)
                weights.append(similarity)
        
        self.maxrw = np.max(weights)
        return self.normWeights(weights)

