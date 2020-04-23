import numpy as np
import cv2
import statistics
import skimage.measure
from matplotlib import pyplot as plt

PATH = '../tests/'
SIZE = 56


def normalize1(img):
    img = cv2.resize(img, (SIZE, SIZE))
    # ret, thresh = cv2.threshold(img, 127, 255, 0)
    return img


def normalize2(img):
    img = skimage.measure.block_reduce(img, (2, 2), np.max)
    img = cv2.resize(img, (SIZE, SIZE))
    # ret, thresh = cv2.threshold(img, 127, 255, 0)
    return img


def normalize(img):
    return normalize1(img)


# im1 = cv2.imread(f'k1.png', cv2.IMREAD_GRAYSCALE)
# im2 = cv2.imread(f's1.png', cv2.IMREAD_GRAYSCALE)
# im3 = cv2.imread(f's2.png', cv2.IMREAD_GRAYSCALE)
im1 = cv2.imread(f'{PATH}p1-1.jpg', cv2.IMREAD_GRAYSCALE)
im2 = cv2.imread(f'{PATH}p1-2.jpg', cv2.IMREAD_GRAYSCALE)
im3 = cv2.imread(f'{PATH}p4-2.jpg', cv2.IMREAD_GRAYSCALE)
im1 = normalize(im1)
im2 = normalize(im2)
im3 = normalize(im3)

ffd = cv2.FastFeatureDetector_create()
br = cv2.BRISK_create()
kp1 = ffd.detect(im1, None)
kp1, des1 = br.compute(im1, kp1)

kp2 = ffd.detect(im2, None)
kp2, des2 = br.compute(im2, kp2)

kp3 = ffd.detect(im3, None)
kp3, des3 = br.compute(im3, kp3)

bf = cv2.BFMatcher_create(cv2.NORM_HAMMING, crossCheck=True)
m1 = bf.match(des1, des2)
# d1 = statistics.mean([m.distance for m in m1])
# print(d1)
#
# m2 = bf.match(des3, des2)
# d2 = statistics.mean([m.distance for m in m2])
# print(d2)

# draw only keypoints location,not size and orientation
# img2 = cv2.drawKeypoints(im2, kp2, outImage=None, color=(0, 255, 0), flags=0)
# plt.imshow(img2), plt.show()

# cv2.imshow('h', im1)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

img3 = cv2.drawMatches(im1, kp1, im2, kp2, m1[:10], outImg=None, flags=2)
plt.imshow(img3), plt.show()
