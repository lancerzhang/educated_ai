import cv2
import matplotlib.pyplot as plt
import numpy as np

from components.img_palette import ImgPalette

fc = ImgPalette('square3.jpg')
# print(fc.palettes_hsv)

idx = 1
for k in fc.palettes_hsv:
    img = fc.get_filtered_gray_image(k)

    outline = np.zeros(img.shape, dtype="uint8")
    cannied = cv2.Canny(img, 30, 200)
    contours, hierarchy = cv2.findContours(cannied,
                                           cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    sorted_cnts = sorted(contours, key=cv2.contourArea, reverse=True)
    if len(sorted_cnts) > 0:
        cnts = sorted_cnts[0]
        cv2.drawContours(outline, [cnts], -1, 255, -1)

    plt.subplot(3, 3, idx)
    idx += 1
    plt.imshow(outline, cmap='gray')
plt.show()
