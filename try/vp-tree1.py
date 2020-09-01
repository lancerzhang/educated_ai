# TensorFlow and tf.keras
# Helper libraries

import cv2
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import vptree
from skimage.metrics import structural_similarity as ssim
from tensorflow import keras

print(tf.__version__)

fashion_mnist = keras.datasets.fashion_mnist

(train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()

class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

SMALL = 4
MEDIUM = 3
LARGE = 2

SIZE_UNIT = 7
BASE_SIZE = 14
MIN_FILL_RATE = 0.05
MIN_DISTANCE = 0.1
COMMON_RATE = 0.6
image_group = np.load('image_group.npy', allow_pickle=True)
image_group = image_group[()]

selected_group = 8
selected_image = train_images[image_group[9][0]]
ret, selected_image = cv2.threshold(selected_image, 64, 255, cv2.THRESH_BINARY)
compare_images = 2


def np_2d_array_nonzero_box(arr):
    nz = arr.nonzero()
    if len(nz[0]) > 0 and len(nz[1]) > 0:
        return arr[min(nz[0]):max(nz[0]) + 1, min(nz[1]):max(nz[1]) + 1]
    else:
        return arr


def get_fill_rate(img):
    return img.sum() / (img.shape[0] * img.shape[1] * 255)


points = []
for i in range(len(image_group)):
    for j in range(compare_images):
        img = train_images[image_group[i][j]]
        ret, img = cv2.threshold(img, 64, 255, cv2.THRESH_BINARY)

        points.append(img)


def compare_im(im1, im2):
    d = ssim(im1, im2)
    return 1 - d


tree = vptree.VPTree(points, compare_im)
point1 = points[7]

points2 = tree.get_n_nearest_neighbors(point1, 2)
idx = 1
plt.subplot(2, 2, idx)
plt.imshow(point1, cmap='gray')
for pt in points2:
    idx += 1
    plt.subplot(2, 2, idx)
    plt.imshow(pt[1], cmap='gray')
plt.show()
