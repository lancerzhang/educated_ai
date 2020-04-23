import cv2
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


im1 = cv2.imread(f'triangle1.jpg', cv2.IMREAD_GRAYSCALE)
im2 = cv2.imread(f'square1.jpg', cv2.IMREAD_GRAYSCALE)
im3 = cv2.imread(f'square2.jpg', cv2.IMREAD_GRAYSCALE)

im1 = normalize(im1)
im2 = normalize(im2)
im3 = normalize(im3)

r1 = cv2.matchTemplate(im1, im2, cv2.TM_SQDIFF_NORMED)
d1 = 1 - r1
print(f'{d1}')
r2 = cv2.matchTemplate(im3, im2, cv2.TM_SQDIFF_NORMED)
d2 = 1 - r2
print(f'{d2}')
