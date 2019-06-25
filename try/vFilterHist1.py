import numpy as np
import cv2, time
import matplotlib.pyplot as plt

# read image with color
# img = cv2.imread('image2.jpg')

# read image with grey
img = cv2.imread('image2.jpg', 0)

# edge detection
filter1 = np.array([[1, 0, -1],
                    [0, 0, 0],
                    [-1, 0, 1]])

filter2 = np.array([[-1, 0, 1],
                    [0, 0, 0],
                    [1, 0, -1]])

# black
filter3 = np.array([[-1, -1, 0],
                    [0, -1, -1],
                    [1, 0, 0]])

cov = cv2.filter2D(img, -1, filter3)

time1 = time.clock()
hist_cv = cv2.calcHist([cov], [0], None, [256], [0, 256])
# hist_cv = np.bincount(cov.ravel(),minlength=256)
time2 = time.clock()
print('use:', (time2 - time1) * 1000)
print(hist_cv[0][0])
print(np.sum(hist_cv))
print(hist_cv[0][0] / np.sum(hist_cv))
plt.subplot(221), plt.imshow(cov, 'gray')
plt.subplot(222), plt.plot(hist_cv)
plt.show()

cv2.waitKey(0)
cv2.destroyAllWindows()
