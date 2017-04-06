# Nathan Harmon
# https://github.com/nharmon/bogie-five
#
# Panorama Script
#
from Camera import *
from Motion import *

def gatherPhotos(angle):
    '''Gather images for a panorama
    
    :param angle (float): How wide of a panorama in radians, from 0 to 2*pi
    :return photos (list): List of numpy.array images
    '''
    drive = Drive()
    num_shots = np.ceil(angle / 0.5)
    photos = []
    
    # Position the camera to the left limit
    drive.turn(-angle/2.)
    
    for i in range(num_shots-1)
        photos.append(bogiecam.shoot())
        turn = min(0.5,angle-(0.5 * i))
        drive.turn(turn)
    
    # Return the rober to the original heading
    drive.turn(-angle)
    
    return photos


if __name__ == '__main__':
    if len(sys.argv) < 2:
        exit("Must specify an angle (in radians)")
    
    bogiecam = BogieCamera()
    try:
        photos = gatherPhotos(float(sys.argv[1]))
    except:
        exit("Invalid angle")
    
    pano = bogiecam.makePanorama(photos)
    cv2.imwrite("pano.jpg", pano)
