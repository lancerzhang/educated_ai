from __future__ import absolute_import, division, print_function, unicode_literals

import cv2
# Helper libraries
import numpy as np
# TensorFlow and tf.keras
import tensorflow as tf

print(tf.__version__)

from components import util
import os, ssl
import pickle
import time
from matplotlib import pyplot
from numpy import expand_dims

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
        getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

from keras.applications.vgg16 import preprocess_input
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array

with open('vgg16.l1.top.filters', 'rb') as filters:
    vgg16_filters = pickle.load(filters)

img = load_img('head3.jpg', target_size=(64, 64))
img = img_to_array(img)
img = expand_dims(img, axis=0)
img = preprocess_input(img)
x = 3
y = 3

# feature = tf.nn.conv2d(img, vgg16_filters, [1, 1, 1, 1], padding="SAME")
# feature = tf.nn.relu(feature)
# for i in range(x * y):
#     pyplot.subplot(x, y, i+1)
#     pyplot.imshow(feature[0, :, :, i], cmap='gray')

t = 0
for i in range(len(vgg16_filters)):
    pyplot.subplot(x, y, i + 1)
    t1 = time.time()
    kernel = vgg16_filters[i]
    kernel = expand_dims(kernel, axis=-1)
    feature1 = tf.nn.conv2d(img, kernel, [1, 1, 1, 1], padding="VALID")
    feature1 = tf.nn.relu(feature1)
    feature1 = feature1[0, :, :, 0].numpy()
    outline = np.zeros(feature1.shape, dtype="uint8")
    feature1 = feature1.astype(np.uint8)
    feature1 = cv2.Canny(feature1, 30, 200)
    contours, hierarchy = cv2.findContours(feature1,
                                           cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    sorted_cnts = sorted(contours, key=cv2.contourArea, reverse=True)
    if len(sorted_cnts) > 0:
        cnts = sorted_cnts[0]
        cv2.drawContours(outline, [cnts], -1, 255, -1)
    if util.img_has_content(outline):
        pyplot.imshow(outline, cmap='gray')
    t2 = time.time()
    t = t + (t2 - t1)

print(f'avg {t * 1000 / (x * y)} ms to conv an image')

pyplot.show()
