import cv2
import numpy as np

im = cv2.imread(f'square1.jpg', cv2.IMREAD_GRAYSCALE)
im = ~im
ret, thresh = cv2.threshold(im, 127, 255, 0)
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
outline = np.zeros(im.shape, dtype="uint8")
sorted_cnts = sorted(contours, key=cv2.contourArea, reverse=True)
if len(sorted_cnts) > 0:
    cnts = sorted_cnts[0]
    cv2.drawContours(outline, [cnts], -1, 255, -1)
cv2.imshow('h', outline)
cv2.waitKey(0)
cv2.destroyAllWindows()
