import cv2
import matplotlib.pyplot as plt
import numpy as np
from colorthief import ColorThief

threshold = 50
import colorsys


def get_filtered_color_image(file):
    color_thief = ColorThief(file)
    img = cv2.imread(file, 1)
    grey = cv2.imread(file, 0)
    dominant_color = color_thief.get_color(quality=1)
    palettes = color_thief.get_palette(color_count=6, quality=1)
    print(palettes)
    idx = 1
    for palette in palettes:
        r, g, b = palette
        palette_hsv = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        h, s, v = palette_hsv
        print(h * 360, s, v)
        mask = cv2.inRange(img, (b - threshold, g - threshold, r - threshold),
                           (b + threshold, g + threshold, r + threshold))
        mask = mask.astype('bool')
        masked = grey * mask
        outline = np.zeros(masked.shape, dtype="uint8")
        cannied = cv2.Canny(masked, 30, 200)
        contours, hierarchy = cv2.findContours(cannied,
                                               cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        sorted_cnts = sorted(contours, key=cv2.contourArea, reverse=True)
        if len(sorted_cnts) > 0:
            cnts = sorted_cnts[0]
            cv2.drawContours(outline, [cnts], -1, 255, -1)
        # filled_rate = outline.sum() / (outline.shape[0] * outline.shape[1] * 255)
        plt.subplot(3, 3, idx)
        idx += 1
        plt.imshow(masked, cmap='gray')
    plt.show()


get_filtered_color_image('l1-1.jpg')
# cv2.imshow("Result", get_filtered_color_image('triangle1.jpg'))
#
# cv2.waitKey(0)
# cv2.destroyAllWindows()
