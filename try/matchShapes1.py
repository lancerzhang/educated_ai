import cv2
import numpy as np
import skimage.measure

# PATH = '../tests/'
PATH = '../debug/img/'
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


CONTOURS_MATCH_I = cv2.CONTOURS_MATCH_I2
# im1 = cv2.imread(f'k1.png', cv2.IMREAD_GRAYSCALE)
# im2 = cv2.imread(f's1.png', cv2.IMREAD_GRAYSCALE)
# im3 = cv2.imread(f's2.png', cv2.IMREAD_GRAYSCALE)
im1 = ~cv2.imread(f'triangle1.jpg', cv2.IMREAD_GRAYSCALE)
im2 = ~cv2.imread(f'square1.jpg', cv2.IMREAD_GRAYSCALE)
im3 = ~cv2.imread(f'square2.jpg', cv2.IMREAD_GRAYSCALE)
# im1 = ~cv2.imread(f'{PATH}f5c2ea9c781e435f1646784db8f564292aae3a40.jpg', cv2.IMREAD_GRAYSCALE)
# im1 = util.np_2d_array_nonzero_box(im1)
# im2 = util.np_2d_array_nonzero_box(im2)
# im3 = util.np_2d_array_nonzero_box(im3)
im1 = normalize(im1)
im2 = normalize(im2)
im3 = normalize(im3)
d1 = cv2.matchShapes(im1, im2, CONTOURS_MATCH_I, 0)
print(f'd1 {d1}')
d2 = cv2.matchShapes(im3, im2, CONTOURS_MATCH_I, 0)
print(f'd2 {d2}')
# cv2.imshow('h', im1)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
