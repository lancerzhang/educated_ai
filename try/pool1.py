import cv2
import numpy as np
import skimage.measure

img = cv2.imread('two.jpg', 0)
kernel2 = np.array([[1, 0, -1],
                    [0, 0, 0],
                    [-1, 0, 1]])
cov = cv2.filter2D(img, -1, kernel2)
pool = skimage.measure.block_reduce(cov, (2, 2), np.max)
cv2.imshow('image', cov)
cv2.waitKey(0)
cv2.destroyAllWindows()
