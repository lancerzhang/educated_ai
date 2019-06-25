import cv2
from components import util

im1=cv2.imread('head1.jpg',1)
im2=cv2.imread('head2.jpg',1)
print("{:.1%}".format(util.color_hist_similarity(im1, im2)))