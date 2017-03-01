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
    def __init__(self, res=(320, 240), framerate=24):
        """Initialize the vision class
        
        Instantiates:
            self.camera (picamera class): Camera object
        """
        self.camera = picamera.PiCamera()
        self.camera.resolution = res
        self.camera.framerate = 1
        time.sleep(2)
        self.camera.shutter_speed = 150000
        self.camera.iso = 800
    
    def makePanorama(self, images):
        """Generate a panorama from multiple images
        
        Parameters:
             images (list): List of np.array images
        
        Returns:
             result (np.array): Panorama
        """
        #TODO: implement stiching and warping from cv2
        
        
        return result
    
    def shoot(self):
        """Takes a photo from the camera
        
        Returns:
            output (np.array): Photograph in array form
        """
        # Image buffer must be multiple of 32 in x, multiple of 16 in y
        buffer_y = 32. * np.ceil(self.camera.resolution[0] / 32.)
        buffer_x = 16. * np.ceil(self.camera.resolution[1] / 16.)
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
        
        Parameters:
            object (numpy.array): template for object we're tracking
            img (numpy.array): first image for tracking
            particles (int): number of particles to use
        
        Instantiates:
            self.object (numpy.array): object template
            self.img (numpy.array): current image
            self.particles (list): initial set of filtered particles
            self.weights (list): particle weights
            self.center (tuple): best guess of where 
        """
        self.object = object
        self.img = img
        
        # Generate particles randomly
        particles = np.random.rand(num_particles,2)
        particles[:,0] *= self.frame.shape[0]
        particles[:,1] *= self.frame.shape[1]
        self.particles = particles.astype(int).tolist()
        self.weights = self.weigh_particles()
        self.center = self.track(self.img)
    
    def compareMSE(self, img1, img2, sigma=10.):
        """Calculate the similarity of two images using Mean Squared Error.
        
        Parameters:
            img1 (numpy.array): First image
            img2 (numpy.array): Second image
            sigma (float): MSE weight
        
        Returns:
            similarity (float): <=1.0 where 1.0 means the images are alike.
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
    
    def resample(self, particles, weights):
        """Resample particles using a sampling wheel
        Reference: https://www.youtube.com/watch?v=wNQVo6uOgYA
        
        Parameters:
            particles (list): (row,col) locations of each particle
            weights (list): weight of each particle
        
        Returns:
            new_particles (list): resampled particles
            new_weights (list): weights of resampled particles
        """
        new_particles = []
        new_weights = []
        N = len(particles)
        index = int(random.random() * N)
        beta = 0.
        mw = max(weights)
        for i in range(N):
            beta += random.random() * 2. * mw
            while beta > weights[index]:
                beta -= weights[index]
                index = (index + 1) % N
            
            new_particles.append(particles[index])
            new_weights.append(weights[index])
        
        return new_particles, new_weights
    
    def weigh_particles(self):
        """Produces a list of particle weights
        
        Returns:
            weights (list): weight of each particle
        """
        weights = []
        for i in range(len(self.particles)):
            # Construct our particle frame
            p_t = int(self.particles[i,0] - np.floor(self.object.shape[0]/2.))
            p_b = int(self.particles[i,0] + np.ceil(self.object.shape[0]/2.))
            p_l = int(self.particles[i,1] - np.floor(self.object.shape[1]/2.))
            p_r = int(self.particles[i,1] + np.ceil(self.object.shape[1]/2.))
            try:
                p_frame = self.img[p_t:p_b,p_l:p_r]
            except:
                weights.append(0.)
                continue
            
            if p_frame.shape <> self.object.shape:    # Frame is off the image
                weights.append(0.)
            else: 
                similarity = compareMSE(p_frame, self.object)
                weights.append(similarity)
        
        # Normalize the weights
        if np.sum(weights) > 0:
            weights /= np.sum(weights)
        else: # None of the particles were valid?
            weights = np.ones(len(weights)) / len(weights)
        
        return weights
    
    def track(img):
        """Guesses where our object is in the new image
        
        Parameters:
            img (np.array): New image
        
        Returns:
            center (tuple): Best guess of object's center
        """
        self.img = img
        self.weights = weigh_particles()
        self.particles, self.weights = resample(self.particles, self.weights)
        if max(self.weights) == 1./len(self.particles):    # Wasn't found
            return False
        
        u_weighted_mean = 0
        v_weighted_mean = 0
        for i in range(len(self.particles)):
            u_weighted_mean += self.particles[i, 0] * self.weights[i]
            v_weighted_mean += self.particles[i, 1] * self.weights[i]
        
        self.center = (u_weighted_mean, v_weighted_mean)
        ### TODO: Update the object template with the new appearance
        
        return self.center
