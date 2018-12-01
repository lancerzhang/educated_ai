import numpy as np
import cv2

bgr = cv2.imread('l1-1.jpg', 1)
yuv = cv2.cvtColor(bgr, cv2.COLOR_BGR2YUV)
y, u, v = cv2.split(yuv)

cv2.imshow('y', y)
cv2.imshow('u', u)
cv2.imshow('v', v)
cv2.waitKey(0)
cv2.destroyAllWindows()
