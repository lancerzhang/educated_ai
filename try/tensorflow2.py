from __future__ import absolute_import, division, print_function, unicode_literals

# TensorFlow and tf.keras
import tensorflow as tf

# Helper libraries

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

img = load_img('triangle1.jpg', target_size=(64, 64))
img = img_to_array(img)
img = expand_dims(img, axis=0)
img = preprocess_input(img)
x = 8
y = 8

# feature = tf.nn.conv2d(img, vgg16_filters, [1, 1, 1, 1], padding="SAME")
# feature = tf.nn.relu(feature)
# for i in range(x * y):
#     pyplot.subplot(x, y, i+1)
#     pyplot.imshow(feature[0, :, :, i], cmap='gray')

t = 0
for i in range(x * y):
    pyplot.subplot(x, y, i + 1)
    t1 = time.time()
    kernel = vgg16_filters[:, :, :, i]
    kernel = expand_dims(kernel, axis=-1)
    feature = tf.nn.conv2d(img, kernel, [1, 1, 1, 1], padding="VALID")
    feature = tf.nn.relu(feature)
    t2 = time.time()
    t = t + (t2 - t1)
    pyplot.imshow(feature[0, :, :, 0], cmap='gray')
print(f'avg {t * 1000 / (x * y)} ms to conv an image')

pyplot.show()
