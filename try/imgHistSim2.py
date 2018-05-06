import util,cv2

im1=cv2.imread('head1.jpg',1)
im2=cv2.imread('head2.jpg',1)
print "{:.1%}".format(util.compareColorHist(im1,im2))