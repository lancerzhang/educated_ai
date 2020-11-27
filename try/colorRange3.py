import matplotlib.pyplot as plt
import cv2
from src import util
from src.hsv_color_shapes import ColorShape


img = cv2.imread('square2.jpg', 1)
cs = ColorShape(img)

idx = 1
for k in cs.top_colors_hsv:
    img = cs.get_grey_shape(k)
    # ret, img = cv2.threshold(img, 64, 255, cv2.THRESH_BINARY)
    # img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
    # img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    img = util.get_filled_shape(img)
    if img is not None:
        plt.subplot(3, 3, idx)
        idx += 1
        plt.imshow(img, cmap='gray')
plt.show()
