from os import listdir

import cv2
import numpy as np
import skimage.measure

from components import util

SIZE = 50
images = ['head1.jpg', 'head2.jpg', 'head3.jpg', 'head4.jpg', 'head5.jpg', 'head10.jpg', 'head11.jpg', 'gb1.jpg',
          'image1.jpg', 'image2.jpg', 'l1-1.jpg', 'l1-2.jpg', 'manu.jpg', 'rgb1.jpg', 'rgb2.jpg', 's1.png', 's2.png',
          'square1.jpg', 'square2.jpg', 'square3.jpg', 'triangle1.jpg']


def normalize1(img):
    img = cv2.resize(img, (SIZE, SIZE))
    ret, img = cv2.threshold(img, 127, 255, 0)
    return img


def normalize2(img):
    img = skimage.measure.block_reduce(img, (2, 2), np.max)
    img = cv2.resize(img, (SIZE, SIZE))
    # ret, img = cv2.threshold(img, 127, 255, 0)
    img = cv2.Canny(img, 30, 200)
    return img


def normalize(img):
    return normalize2(img)


def filter_image(img):
    return img


for file1 in images:
    im1 = ~cv2.imread(file1, cv2.IMREAD_GRAYSCALE)
    im1 = normalize(im1)
    similarity = []
    for file2 in images:
        if file1 == file2:
            continue
        im2 = ~cv2.imread(file2, cv2.IMREAD_GRAYSCALE)
        im2 = normalize(im2)
        d1 = cv2.matchShapes(im1, im2, cv2.CONTOURS_MATCH_I2, 0)
        similarity.append((d1, file2))
    sorted_similarity = sorted(similarity, key=lambda x: x[0], reverse=False)
    most_similar = sorted_similarity[0]
    print(f'{file1} is similar to {most_similar[1]}, distance is {most_similar[0]}')
