import cv2
import numpy as np
import skimage.measure

PATH = '../tests/'
SIZE = 14


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
    return normalize1(img)


def cal_shapes(i, j):
    im1 = cv2.imread(f'{PATH}p{i}-{j}.jpg', cv2.IMREAD_GRAYSCALE)
    im1 = normalize(im1)
    for k in range(1, 5):
        for l in range(1, 3):
            im2 = cv2.imread(f'{PATH}p{k}-{l}.jpg', cv2.IMREAD_GRAYSCALE)
            im2 = normalize(im2)
            res = cv2.matchTemplate(im1, im2, cv2.TM_SQDIFF_NORMED)
            distance = 1 - res
            print(f'p{i}{j} vs p{k}{l} distance {distance}')


for i in range(1, 5):
    for j in range(1, 3):
        print(f'p{i}-{j} ')
        cal_shapes(i, j)
        print(f' ')
