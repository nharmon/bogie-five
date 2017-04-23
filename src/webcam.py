# Nathan Harmon
# https://github.com/nharmon/bogie-five
# 
# Webcam Program
# 
from Camera import *
import cv2
import sys
import time

def compareMSE(img1, img2, sigma=10.):
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


if __name__ == '__main__':
    if len(sys.argv) < 2:
        exit("Must specify output directory")
    
    bogiecam = BogieCamera()
    res = bogiecam.camera.resolution
    pixels = float(res[0] * res[1])
    picture = bogiecam.shoot()
    picture_edges = cv2.Canny(picture,100,200)
    filename = sys.argv[1]+'/'+str(int(time.time()))+'.jpg'
    cv2.imwrite(filename, picture)
    
    while True:
        img = bogiecam.shoot()
        img_edges = cv2.Canny(img,100,200)
        diff = len(img_edges[img_edges != picture_edges]) / pixels
        print diff
        if diff > 0.005:
            print time.time()
            filename = sys.argv[1]+'/'+str(int(time.time()))+'.jpg'
            cv2.imwrite(filename, img)
        
        picture = img
        picture_edges = img_edges

