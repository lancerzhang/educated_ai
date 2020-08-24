import colorsys

import cv2
import matplotlib.pyplot as plt
from colorthief import ColorThief

from components import util

threshold = 50


def get_filtered_color_image(file):
    color_thief = ColorThief(file)
    img = cv2.imread(file, 1)
    grey = cv2.imread(file, 0)
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
        outline = util.get_filled_shape(masked)
        plt.subplot(3, 3, idx)
        idx += 1
        plt.imshow(outline, cmap='gray')
    plt.show()


get_filtered_color_image('l1-1.jpg')
