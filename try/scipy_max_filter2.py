import cv2
import matplotlib.pyplot as plt
from scipy import ndimage

fig = plt.figure()
# plt.gray()  # show the filtered result in grayscale
ax1 = fig.add_subplot(121)  # left side
ax2 = fig.add_subplot(122)  # right side
img = cv2.imread('image1.jpg', 0)
# ascent = misc.ascent()
result = ndimage.maximum_filter(img, size=5)
ax1.imshow(img)
ax2.imshow(result)
plt.show()
