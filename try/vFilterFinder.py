import time

import cv2
import numpy as np

# read image with color
# img = cv2.imread('image2.jpg')

# read image with grey
img = cv2.imread('image2.jpg', 0)

time1 = time.clock()
count = 0
filters = []
for p1 in range(0, 3):
    for p2 in range(0, 3):
        for p3 in range(0, 3):
            for p4 in range(0, 3):
                for p5 in range(0, 3):
                    for p6 in range(0, 3):
                        for p7 in range(0, 3):
                            for p8 in range(0, 3):
                                for p9 in range(0, 3):
                                    # count = count + 1
                                    # print count
                                    filter = np.array(
                                        [[p1 - 1, p2 - 1, p3 - 1], [p4 - 1, p5 - 1, p6 - 1], [p7 - 1, p8 - 1, p9 - 1]])
                                    # print filter
                                    cov = cv2.filter2D(img, -1, filter)
                                    hist_cv = cv2.calcHist([cov], [0], None, [256], [0, 256])
                                    # if hist less than xx, then it's a useful filter
                                    if (hist_cv[0][0] / np.sum(hist_cv) < 0.9):
                                        # fa = np.array_str(filter.flatten())
                                        filters.append(filter)

print('#useful filters:', len(filters))
time2 = time.clock()
print('use:', (time2 - time1))

idx = 0
nFilters = np.array(filters)
# np.save('vision_kernels90.npy', nFilters)

try:
    while idx < 100:
        filter = nFilters[idx]
        cov = cv2.filter2D(img, -1, filter)
        idx = idx + 1
        cv2.imshow('image', cov)
        cv2.waitKey(500)

except KeyboardInterrupt:
    cv2.destroyAllWindows()

cv2.waitKey(0)
cv2.destroyAllWindows()
