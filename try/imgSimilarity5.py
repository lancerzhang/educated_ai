import cv2
import imutils
import numpy as np
from matplotlib import pyplot
from components.filter_colors import FilterColors

"""
1) filter_colors (major colors) 2) (major color shape) canny + drawContours + matchShapes
"""

files = ['head1.jpg', 'head2.jpg', 'head3.jpg', 'head4.jpg', 'head5.jpg', 'head10.jpg', 'head11.jpg', 'gb1.jpg',
         'image1.jpg', 'image2.jpg', 'l1-1.jpg', 'l1-2.jpg', 'manu.jpg', 'rgb1.jpg', 'rgb2.jpg', 's1.jpg', 's2.jpg',
         'square1.jpg', 'square2.jpg', 'square3.jpg', 'triangle1.jpg']

IMG_SIZE = 50
MAJOR_COLORS = 3

imagesFilterColors = {}
for file in files:
    img = cv2.imread(file)
    img = imutils.resize(img, width=IMG_SIZE)
    imagesFilterColors.update({file: FilterColors(img)})


def get_shape(fc, color):
    img = fc.get_filtered_gray_image(color)
    feature = cv2.Canny(img, 30, 200)
    outline = np.zeros(feature.shape, dtype="uint8")
    contours, hierarchy = cv2.findContours(feature,
                                           cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    sorted_cnts = sorted(contours, key=cv2.contourArea, reverse=True)
    if len(sorted_cnts) > 0:
        cnts = sorted_cnts[0]
        cv2.drawContours(outline, [cnts], -1, 255, -1)
    filled_rate = outline.sum() / (outline.shape[0] * outline.shape[1] * 255)
    if filled_rate > 0.05:
        return outline


def compare_contour(ifc1, color1, ranges1, ifc2, color2, ranges2):
    shape1 = get_shape(ifc1, color1)
    if shape1 is not None:
        shape2 = get_shape(ifc2, color2)
        if shape2 is not None:
            distance = cv2.matchShapes(shape1, shape2, cv2.CONTOURS_MATCH_I2, 0)
            if distance < 1:
                # pyplot.subplot(1, 2, 1)
                # pyplot.imshow(shape1, cmap='gray')
                # pyplot.subplot(1, 2, 2)
                # pyplot.imshow(shape2, cmap='gray')
                # pyplot.show()
                return True


def is_in_range(ifc1, color1, ranges1, ifc2, color2, ranges2):
    for rg1 in ranges1:
        for rg2 in ranges2:
            if rg2[0] < rg1[0] < rg2[1]:
                return compare_contour(ifc1, color1, ranges1, ifc2, color2, ranges2)
            elif rg2[0] < rg1[1] < rg2[1]:
                return compare_contour(ifc1, color1, ranges1, ifc2, color2, ranges2)


for file1, ifc1 in imagesFilterColors.items():
    for i in range(MAJOR_COLORS):
        ranges1 = ifc1.rank_ranges[i]
        for file2, ifc2 in imagesFilterColors.items():
            if file1 is file2:
                continue
            for j in range(MAJOR_COLORS):
                ranges2 = ifc2.rank_ranges[j]
                if is_in_range(ifc1, i, ranges1, ifc2, j, ranges2):
                    print(f'{file1} and {file2} are similar color {ranges1} {ranges2}')
