from __future__ import absolute_import, division, print_function, unicode_literals

import cv2
# TensorFlow and tf.keras
import tensorflow as tf

# Helper libraries

print(tf.__version__)

import os, ssl
import pickle
import numpy as np
from matplotlib import pyplot
from numpy import expand_dims

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
        getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

from keras.applications.vgg16 import preprocess_input
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array

with open('vgg16.l1.filters', 'rb') as filters:
    vgg16_filters = pickle.load(filters)

img = load_img('head3.jpg', target_size=(100, 100))
img = img_to_array(img)
img = expand_dims(img, axis=0)
img = preprocess_input(img)
x = 8
y = 8

for i in range(x * y):
    pyplot.subplot(x, y, i + 1)
    # kernel = vgg16_filters[:, :, 0, i]
    # feature = cv2.filter2D(image, -1, kernel)
    kernel = vgg16_filters[:, :, :, i]
    kernel = expand_dims(kernel, axis=-1)
    feature = tf.nn.conv2d(img, kernel, [1, 1, 1, 1], padding="VALID")
    feature = tf.nn.relu(feature)
    feature = feature[0, :, :, 0]
    outline = np.zeros(feature.shape, dtype="uint8")
    feature = feature.numpy()
    feature = feature.astype(np.uint8)
    feature = cv2.Canny(feature, 30, 200)
    contours, hierarchy = cv2.findContours(feature,
                                           cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # cv2.drawContours(outline, contours, -1, 255, 3)
    # cnts = imutils.grab_contours(contours)
    sorted_cnts = sorted(contours, key=cv2.contourArea, reverse=True)
    if len(sorted_cnts) > 0:
        cnts = sorted_cnts[0]
        cv2.drawContours(outline, [cnts], -1, 255, -1)
    pyplot.imshow(outline, cmap='gray')

pyplot.show()
# image = cv2.bilateralFilter(image, 11, 17, 17)
# image = cv2.Canny(image, 30, 200)
# # thresh = cv2.bitwise_not(image)
# # thresh[thresh > 127] = 255
# outline = np.zeros(image.shape, dtype="uint8")
# cnts = cv2.findContours(image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# cnts = imutils.grab_contours(cnts)
# cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[0]
# cv2.drawContours(outline, [cnts], -1, 255, -1)
# cv2.imshow('h', image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
