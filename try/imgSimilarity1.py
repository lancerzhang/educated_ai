from os import listdir
import cv2
import numpy as np
import skimage.measure
from components import util

SIZE = 14


def normalize1(img):
    img = cv2.resize(img, (SIZE, SIZE))
    ret, img = cv2.threshold(img, 127, 255, 0)
    return img


def normalize2(img):
    img = skimage.measure.block_reduce(img, (2, 2), np.max)
    img = cv2.resize(img, (SIZE, SIZE))
    ret, img = cv2.threshold(img, 127, 255, 0)
    return img


def normalize(img):
    return normalize2(img)


def filter_image(img):
    return img


PATH = '../debug/img/'
file1 = '0a83840db259c334447b7b9537d9cc088bfd5707.jpg'
im1 = ~cv2.imread(f'{PATH}{file1}', cv2.IMREAD_GRAYSCALE)
im1 = util.np_2d_array_nonzero_box(im1)
im1 = normalize(im1)

for file in listdir(PATH):
    if file == '.DS_Store':
        continue
    im2 = ~cv2.imread(f'{PATH}{file}', cv2.IMREAD_GRAYSCALE)
    im2 = util.np_2d_array_nonzero_box(im2)
    im2 = normalize(im2)
    d1 = cv2.matchShapes(im1, im2, cv2.CONTOURS_MATCH_I2, 0)
    if d1 < 0.01:
        print(f'{file1} compared with {file}')
        print(f'd1 {d1}')
