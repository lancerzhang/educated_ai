import numpy as np
import cv2
import statistics
import skimage.measure
from matplotlib import pyplot as plt

PATH = '../tests/'

# im1 = cv2.imread(f'k1.png', cv2.IMREAD_GRAYSCALE)
# im2 = cv2.imread(f's1.png', cv2.IMREAD_GRAYSCALE)
# im3 = cv2.imread(f's2.png', cv2.IMREAD_GRAYSCALE)
im1 = cv2.imread(f'{PATH}p1-1.jpg', cv2.IMREAD_GRAYSCALE)
im2 = cv2.imread(f'{PATH}p3-1.jpg', cv2.IMREAD_GRAYSCALE)
im3 = cv2.imread(f'{PATH}p3-2.jpg', cv2.IMREAD_GRAYSCALE)

# Initiate STAR detector
orb1 = cv2.ORB_create()
kp1 = orb1.detect(im1, None)
kp1, des1 = orb1.compute(im1, kp1)

orb2 = cv2.ORB_create()
kp2 = orb2.detect(im2, None)
kp2, des2 = orb2.compute(im2, kp2)

orb3 = cv2.ORB_create()
kp3 = orb3.detect(im3, None)
kp3, des3 = orb3.compute(im3, kp3)

# bf1 = cv2.BFMatcher_create(cv2.NORM_HAMMING, crossCheck=True)
# m1 = bf1.match(des1, des2)
# d1 = statistics.mean([m.distance for m in m1])
# print(d1)
#
# bf2 = cv2.BFMatcher_create(cv2.NORM_HAMMING, crossCheck=True)
# m2 = bf2.match(des3, des2)
# d2 = statistics.mean([m.distance for m in m2])
# print(d2)

# draw only keypoints location,not size and orientation
img2 = cv2.drawKeypoints(im1, kp1, outImage=None, color=(0, 255, 0), flags=0)
plt.imshow(img2), plt.show()

# cv2.imshow('h', im1)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
