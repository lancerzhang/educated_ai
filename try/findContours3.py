import cv2
import imutils
import numpy as np

im = cv2.imread(f'pokemon1.jpg', cv2.IMREAD_GRAYSCALE)
ret, thresh = cv2.threshold(im, 127, 255, 0)
thresh = ~thresh
outline = np.zeros(thresh.shape, dtype="uint8")
cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[0]
cv2.drawContours(outline, [cnts], -1, 255, -1)
cv2.imshow('h', outline)
cv2.waitKey(0)
cv2.destroyAllWindows()
