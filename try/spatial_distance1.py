import cv2
from scipy import spatial
import numpy as np
import skimage.measure

PATH = '../tests/'
SIZE = 28


def normalize1(img):
    img = cv2.resize(img, (SIZE, SIZE))
    ret, thresh = cv2.threshold(img, 127, 255, 0)
    return thresh


def normalize2(img):
    img = skimage.measure.block_reduce(img, (2, 2), np.max)
    img = cv2.resize(img, (SIZE, SIZE))
    ret, thresh = cv2.threshold(img, 127, 255, 0)
    return thresh


def normalize(img):
    return normalize2(img)


# im1 = cv2.imread(f'k1.png', cv2.IMREAD_GRAYSCALE)
# im2 = cv2.imread(f's1.png', cv2.IMREAD_GRAYSCALE)
# im3 = cv2.imread(f's2.png', cv2.IMREAD_GRAYSCALE)
im1 = cv2.imread(f'triangle1.jpg', cv2.IMREAD_GRAYSCALE)
im2 = cv2.imread(f'square1.jpg', cv2.IMREAD_GRAYSCALE)
im3 = cv2.imread(f'square2.jpg', cv2.IMREAD_GRAYSCALE)
im1 = normalize(im1)
im2 = normalize(im2)
im3 = normalize(im3)
im1 = im1.flatten()
im2 = im2.flatten()
im3 = im3.flatten()
d1 = spatial.distance.cosine(im1, im2)
print(d1)
d2 = spatial.distance.cosine(im2, im3)
print(d2)
