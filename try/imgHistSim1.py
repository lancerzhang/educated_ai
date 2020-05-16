import cv2
import histogram as his
import histogram2 as his2
import histogramCv as hisCv
from PIL import Image

img1 = Image.open("head1.jpg")
img2 = Image.open("head3.jpg")
print("{:.1%}".format(his.classfiy_histogram(img1, img2)))
print("{:.1%}".format(his2.classfiy_histogram_with_split(img1, img2)))
im1 = cv2.imread('head1.jpg', 1)
im2 = cv2.imread('head2.jpg', 1)
print("{:.1%}".format(hisCv.classfiy_histogram(im1, im2)))
