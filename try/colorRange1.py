import cv2
import matplotlib.pyplot as plt

from src.filter_colors import FilterColors

img = cv2.imread('square1.jpg', 1)
fc = FilterColors(img)
idx = 1
for k in range(len(fc.rank_ranges)):
    img = fc.get_filtered_gray_image(k)
    plt.subplot(4, 4, idx)
    idx += 1
    plt.imshow(img, cmap='gray')
plt.show()
