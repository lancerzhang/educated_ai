import numpy as np
import cv2, time

# read image with color
# img = cv2.imread('image2.jpg')

# read image with grey
img = cv2.imread('image2.jpg',0)

times = 100

try:
    while times > 0:
        times = times - 1
        print times
        filter = np.random.choice([-1, 0, 1], (3, 3))
        print filter
        cov = cv2.filter2D(img, -1, filter)
        cv2.imshow('image', cov)
        cv2.waitKey(1000)

except KeyboardInterrupt:
    cv2.destroyAllWindows()

cv2.waitKey(0)
cv2.destroyAllWindows()
