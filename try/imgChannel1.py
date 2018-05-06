import numpy as np
import cv2

bgr = cv2.imread('image2.jpg')
blue=bgr.copy()
blue[:, :, 1]=0
blue[:, :, 2]=0
# b,g,r = cv2.split(bgr)
yuv=cv2.cvtColor(bgr,cv2.COLOR_BGR2YUV)
# y,u,v=cv2.split(yuv)
channel2=yuv.copy()
channel2[:, :, 2]=0
channel2[:, :, 0]=0
result=cv2.cvtColor(channel2,cv2.COLOR_YUV2BGR)

cv2.imshow('image', result)
cv2.waitKey(0)
cv2.destroyAllWindows()