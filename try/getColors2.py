import cv2

import components.rgb_top_colors as mc

img = cv2.imread('square1.jpg', 1)
hist = mc.find_colors(img)
for h in hist:
    print(h)
