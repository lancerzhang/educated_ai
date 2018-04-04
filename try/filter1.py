import numpy as np
import cv2, time

img = cv2.imread('image2.jpg', 0)

times = 100
try:
    while times > 0:
        times = times - 1
        filter = np.random.choice([-1, 0, 1], (3, 3))
        print filter
        fimg = np.array(filter, dtype='float32')
        cov = cv2.filter2D(img, -1, fimg)
        cv2.imshow('image', cov)
        time.sleep(5)

except KeyboardInterrupt:
    cv2.destroyAllWindows()

cv2.waitKey(0)
cv2.destroyAllWindows()
