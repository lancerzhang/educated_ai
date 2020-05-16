import pickle
from os import listdir

import cv2
import numpy as np
import skimage.measure
import tensorflow as tf
from keras.applications.vgg16 import preprocess_input
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import load_img
from numpy import expand_dims

SIZE = 14
PATH = '../debug/img/'

with open('vgg16.l1.filters', 'rb') as filters:
    vgg16_filters = pickle.load(filters)


def normalize1(img):
    img = cv2.resize(img, (SIZE, SIZE))
    ret, img = cv2.threshold(img, 127, 255, 0)
    return img


def normalize2(img):
    img = skimage.measure.block_reduce(img, (2, 2), np.max)
    img = cv2.resize(img, (SIZE, SIZE))
    ret, img = cv2.threshold(img, 127, 255, 0)
    return img


def normalize(img):
    return normalize2(img)


def filter_image(name):
    img = load_img(f'../debug/img/{name}', target_size=(64, 64))
    img = img_to_array(img)
    img = expand_dims(img, axis=0)
    img = preprocess_input(img)
    filter = vgg16_filters[:, :, :, 7]
    filter = expand_dims(filter, axis=-1)
    img = tf.nn.conv2d(img, filter, [1, 1, 1, 1], padding="VALID")
    img = tf.nn.relu(img)
    img = img[0, :, :, 0].numpy()
    # im1 = util.np_2d_array_nonzero_box(im1)
    # im1 = normalize(im1)
    return img


file1 = 'f363ec8da8a04f31d29b28de668587098764b9d9.jpg'
im1 = filter_image(file1)

# cv2.imshow('h', im1)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

for file in listdir(PATH):
    if file == '.DS_Store':
        continue
    im2 = filter_image(file)
    d1 = cv2.matchShapes(im1, im2, cv2.CONTOURS_MATCH_I2, 0)
    if d1 < 0.01:
        print(f'{file1} compared with {file}')
        print(f'd1 {d1}')
