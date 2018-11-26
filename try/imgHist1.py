import numpy as np
import cv2
import matplotlib.pyplot as plt

img = cv2.imread('head10.jpg',0)
hist_cv = cv2.calcHist([img],[0],None,[256],[0,256])
hist_np,bins = np.histogram(img.ravel(),bins=256, range=[0, 256])
imgravel=img.ravel()
hist_np2 = np.bincount(imgravel,minlength=256)
plt.subplot(221),plt.imshow(img,'gray')
plt.subplot(222),plt.plot(hist_cv)
plt.subplot(223),plt.plot(hist_np)
plt.subplot(224),plt.plot(hist_np2)
plt.show()

cv2.waitKey(0)
cv2.destroyAllWindows()
