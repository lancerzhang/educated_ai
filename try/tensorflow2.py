from __future__ import absolute_import, division, print_function, unicode_literals

# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow import keras
import time
# Helper libraries
import numpy as np
import matplotlib.pyplot as plt

print(tf.__version__)

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

with open('vgg16.l1.filters', 'rb') as filters:
    vgg16_filters = pickle.load(filters)

img = load_img('triangle1.jpg', target_size=(224, 224))
x = 8
y = 8
# pyplot.subplot(x, y, ix)
# pyplot.imshow(img, cmap='gray')
# convert the image to an array
img = img_to_array(img)
# expand dimensions so that it represents a single 'sample'
img = expand_dims(img, axis=0)
# prepare the image (e.g. scale pixel values for the vgg)
img = preprocess_input(img)
# ix += 1


# feature = tf.nn.conv2d(img, vgg16_filters, [1, 1, 1, 1], padding="SAME")
# feature = tf.nn.relu(feature)
# for i in range(x * y):
#     pyplot.subplot(x, y, i+1)
#     pyplot.imshow(feature[0, :, :, i], cmap='gray')

t = 0
for i in range(x * y):
    pyplot.subplot(x, y, i + 1)
    t1 = time.time()
    filter = vgg16_filters[:, :, :, i]
    filter = expand_dims(filter, axis=-1)
    feature = tf.nn.conv2d(img, filter, [1, 1, 1, 1], padding="VALID")
    feature = tf.nn.relu(feature)
    t2 = time.time()
    t = t + (t2 - t1)
    pyplot.imshow(feature[0, :, :, 0], cmap='gray')
print(f'avg {t * 1000 / (x * y)} ms to con an image once')

pyplot.show()
