import cv2
import util

img1 = cv2.imread('head1.jpg',1)
img1 = cv2.resize(img1, (1, 1))
print(util.colorSorter(img1[0,0]))

img2 = cv2.imread('head2.jpg',1)
img2 = cv2.resize(img2, (1, 1))
print(util.colorSorter(img2[0,0]))

img3 = cv2.imread('head3.jpg',1)
img3 = cv2.resize(img3, (1, 1))
print(util.colorSorter(img3[0,0]))

img4 = cv2.imread('head4.jpg',1)
img4 = cv2.resize(img4, (1, 1))
print(util.colorSorter(img4[0,0]))

img5 = cv2.imread('head5.jpg',1)
img5 = cv2.resize(img5, (1, 1))
print(util.colorSorter(img5[0,0]))
