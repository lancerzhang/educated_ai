import cv2

im = cv2.imread(f'data.png', cv2.IMREAD_GRAYSCALE)
im = ~im
ret, thresh = cv2.threshold(im, 127, 255, 0)
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
img = cv2.drawContours(im, contours, -1, (0, 255, 0), 3)
cv2.imshow('h', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
