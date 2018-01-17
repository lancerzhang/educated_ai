import numpy as np
import cv2

img = cv2.imread('image2.jpg',0)
g=np.array([[-1,0,1],[-2,0,2],[-1,0,1]],dtype='float32')
cov=cv2.filter2D(img,-1,g)

cv2.imshow('image',cov)
cv2.waitKey(0)
cv2.destroyAllWindows()