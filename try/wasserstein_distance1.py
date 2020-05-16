import cv2
import numpy as np
from scipy.stats import wasserstein_distance

PATH = '../tests/'


def get_histogram(img):
    '''
    Get the histogram of an image. For an 8-bit, grayscale image, the
    histogram will be a 256 unit vector in which the nth value indicates
    the percent of the pixels in the image with the given darkness level.
    The histogram's values sum to 1.
    '''
    h, w = img.shape
    hist = [0.0] * 256
    for i in range(h):
        for j in range(w):
            hist[img[i, j]] += 1
    return np.array(hist) / (h * w)


# im1 = cv2.imread(f'k1.png', cv2.IMREAD_GRAYSCALE)
# im2 = cv2.imread(f's1.png', cv2.IMREAD_GRAYSCALE)
# im3 = cv2.imread(f's2.png', cv2.IMREAD_GRAYSCALE)
im1 = cv2.imread(f'triangle1.jpg', cv2.IMREAD_GRAYSCALE)
im2 = cv2.imread(f'square1.jpg', cv2.IMREAD_GRAYSCALE)
im3 = cv2.imread(f'square2.jpg', cv2.IMREAD_GRAYSCALE)
a_hist = get_histogram(im1)
b_hist = get_histogram(im2)
c_hist = get_histogram(im3)
d1 = wasserstein_distance(a_hist, b_hist)
print(d1 * 1000)
d2 = wasserstein_distance(c_hist, b_hist)
print(d2 * 1000)
