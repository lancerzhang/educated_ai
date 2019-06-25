import numpy as np
import cv2, time

# read image with color
img = cv2.imread('image2.jpg')

# read image with grey
# img = cv2.imread('image2.jpg', 0)


# edge detection
filter1 = np.array([[1, 0, -1],
                    [0, 0, 0],
                    [-1, 0, 1]])

filter2 = np.array([[-1, 0, 1],
                    [0, 0, 0],
                    [1, 0, -1]])

# black
filter3 = np.array([[-1, -1, 0],
                    [0, -1, -1],
                    [1, 0, 0]])
# blur
filter4 = np.array([[0.11, 0.11, 0.11],
                    [0.11, 0.11, 0.11],
                    [0.11, 0.11, 0.11]])

filter5 = np.array([[0.5, 0.5, 0.5],
                    [0.5, 0.5, 0.5],
                    [0.5, 0.5, 0.5]])

new_img = cv2.resize(img, (3, 3))
cov = cv2.filter2D(new_img, -1, filter5)
cv2.imshow('image', cov)
print(cov)
cv2.waitKey(0)
cv2.destroyAllWindows()
