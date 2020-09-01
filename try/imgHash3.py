# TensorFlow and tf.keras
# Helper libraries

import imagehash
import numpy as np
import tensorflow as tf
from PIL import Image
from tensorflow import keras

print(tf.__version__)

fashion_mnist = keras.datasets.fashion_mnist

(train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()

class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

image_group = np.load('image_group.npy', allow_pickle=True)
image_group = image_group[()]

selected_group = 9
selected_index = 0
selected_image = train_images[image_group[9][0]]
compare_images = range(10)


def im_hash(image, hashSize=8):
    image = Image.fromarray(image)
    imh = imagehash.phash(image)
    # print(imh.hash)
    return imh
    # resized = cv2.resize(image, (hashSize + 1, hashSize))
    # diff = resized[:, 1:] > resized[:, :-1]
    # return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])


def hamming(h1, h2):
    h, d = 0, h1 ^ h2
    while d:
        h += 1
        d &= d - 1
    return h


# im1 = cv2.cvtColor(selected_image, cv2.COLOR_BGR2GRAY)
hash1 = im_hash(selected_image)
print(hash1)
for i in compare_images:
    img = train_images[image_group[selected_group][i]]
    hash2 = im_hash(img)
    # print(hash2)
    # distance = hamming(hash1, hash2)
    distance = hash1 - hash2
    print(distance)
