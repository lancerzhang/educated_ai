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


def cal_shapes(i, j, t):
    im1 = ~cv2.imread(f'{PATH}p{i}-{j}.jpg', cv2.IMREAD_GRAYSCALE)
    im1 = normalize(im1)
    for k in range(1, 5):
        for l in range(1, 3):
            im2 = ~cv2.imread(f'{PATH}p{k}-{l}.jpg', cv2.IMREAD_GRAYSCALE)
            im2 = normalize(im2)
            distance = cv2.matchShapes(im1, im2, t, 0)
            print(f'CONTOURS_MATCH_I{t} p{i}{j} vs p{k}{l} distance {distance}')


def normalize(img):
    # normalize1 is better than normalize2
    # normalize1 is smoother than normalize2
    return normalize1(img)


for i in range(1, 5):
    for j in range(1, 3):
        print(f'p{i}-{j} ')
        for t in range(1, 4):
            cal_shapes(i, j, t)
            print(f' ')

# im1 = ~cv2.imread(f'{PATH}p1-2.jpg', cv2.IMREAD_GRAYSCALE)
# im1 = normalize(im1)
# print(f'img size {im1.shape[:2]}')
# cv2.imshow('h', im1)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
