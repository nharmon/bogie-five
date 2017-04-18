# Nathan Harmon
# https://github.com/nharmon/bogie-five
#
# Vision module
#
import cv2
import numpy as np
import random
import time


class Tracker:
    """Class for tracking a visual target using a particle filter.
    """
    def __init__(self, target, img, num_particles=100):
        """Initialize
        
        :param target (numpy.array): template for target we're tracking
        :param img (numpy.array): first image for tracking
        :param particles (int): number of particles to use
        :inst self.target (numpy.array): target template
        :inst self.img (numpy.array): current image
        :inst self.maxrw (float): current maximum raw weight
        :inst self.particles (list): initial set of filtered particles
        :inst self.weights (list): particle weights (via self.track)
        :inst self.center (tuple): best guess of where target is in image
        """
        self.target = cv2.GaussianBlur(target,(15,15),7)
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
    
    def getImageSection(self, center, shape):
        """Return a section of the current image, of size `shape` centered at
           `center`
        
        :param center (tuple): Coordinate where the subimage is centered
        :param shape (tuple): Width and height of subimage
        :return subimage (numpy.ndarray): Cropped image section, or False if
                                          there is an error.
        """
        s_top = int(center[0] - np.floor(shape[0]/2.))
        s_bottom = int(center[0] + np.ceil(shape[0]/2.))
        s_left = int(center[1] - np.floor(shape[1]/2.))
        s_right = int(center[1] + np.ceil(shape[1]/2.))
        try:
            subimage = self.img[s_top:s_bottom,s_left:s_right]
        except:
            return False
        
        if subimage.shape == shape:
            return subimage
        
        return False
    
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
            
            # Adding random noise to particles
            x = particles[index][0] + random.randint(-10,10)
            y = particles[index][1] + random.randint(-10,10)
            new_particles.append([x,y])
        
        return new_particles
    
    def track(self, img):
        """Guesses where our target is in the new image
        
        :param img (np.array): New image
        :return center (tuple): Best guess of target's center
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
        
        # Update self.target using new center.
        self.target = getImageSection(self, self.center, self.target.shape)

        #TODO: Update self.target in a way that accounts for size changes
        #      in the target. Should we blend the new self.target above with
        #      the old one to do this? How would that degrade over time?
        
        return self.center
    
    def weigh_particles(self):
        """Produces a list of particle weights
        
        :return weights (list): weight of each particle
        """
        weights = []
        for i in range(len(self.particles)):
            p_frame = self.getImageSection(self, self.particles[i], 
                                           self.target.shape)
            if p_frame == False:
                weights.append(0.)
                continue
            
            similarity = self.compareMSE(p_frame, self.target)
            weights.append(similarity)
        
        self.maxrw = np.max(weights)
        return self.normWeights(weights)
