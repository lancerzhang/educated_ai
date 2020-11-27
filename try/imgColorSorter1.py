import cv2

from src import util

img1 = cv2.imread('head1.jpg', 1)
img1 = cv2.resize(img1, (1, 1))
print((util.sort_color(img1[0, 0])))

img2 = cv2.imread('head2.jpg', 1)
img2 = cv2.resize(img2, (1, 1))
print((util.sort_color(img2[0, 0])))

img3 = cv2.imread('head3.jpg', 1)
img3 = cv2.resize(img3, (1, 1))
print((util.sort_color(img3[0, 0])))

img4 = cv2.imread('head4.jpg', 1)
img4 = cv2.resize(img4, (1, 1))
print((util.sort_color(img4[0, 0])))

img5 = cv2.imread('head5.jpg', 1)
img5 = cv2.resize(img5, (1, 1))
print((util.sort_color(img5[0, 0])))
