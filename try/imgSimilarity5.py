import cv2
import numpy as np
from matplotlib import pyplot

from components.filter_colors import FilterColors

"""
canny + drawContours + matchShapes
"""

img = cv2.imread('square1.jpg', 1)
img = cv2.resize(img, (50, 50))
fc = FilterColors(img)
for i in range(3):
    pyplot.subplot(1, 5, i + 1)
    img = fc.get_filtered_color_image(i)
    feature = cv2.Canny(img, 30, 200)
    outline = np.zeros(feature.shape, dtype="uint8")
    contours, hierarchy = cv2.findContours(feature,
                                           cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    sorted_cnts = sorted(contours, key=cv2.contourArea, reverse=True)
    if len(sorted_cnts) > 0:
        cnts = sorted_cnts[0]
        cv2.drawContours(outline, [cnts], -1, 255, -1)
    pyplot.imshow(outline, cmap='gray')
pyplot.show()
