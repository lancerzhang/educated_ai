import cv2
from matplotlib import pyplot as plt

img = cv2.imread('image1.jpg', 1)
plt.imshow(img, cmap='gray')
plt.show()
