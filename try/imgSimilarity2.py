import pickle
import time

import cv2
import tensorflow as tf
from keras.applications.vgg16 import preprocess_input
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import load_img
from matplotlib import pyplot
from numpy import expand_dims

"""
vgg16 filters + threshold + matchShapes
"""

images = ['head1.jpg', 'head2.jpg', 'head3.jpg', 'head4.jpg', 'head5.jpg', 'head10.jpg', 'head11.jpg', 'gb1.jpg',
          'image1.jpg', 'image2.jpg', 'l1-1.jpg', 'l1-2.jpg', 'manu.jpg', 'rgb1.jpg', 'rgb2.jpg', 's1.png', 's2.png',
          'square1.jpg', 'square2.jpg', 'square3.jpg', 'triangle1.jpg']

with open('vgg16.l1.filters', 'rb') as filters:
    vgg16_filters = pickle.load(filters)

IMG_SIZE = 50


def compute_feature_maps():
    image_features = []
    for file1 in images:
        im1 = load_img(file1, target_size=(IMG_SIZE, IMG_SIZE))
        im1 = img_to_array(im1)
        im1 = expand_dims(im1, axis=0)
        im1 = preprocess_input(im1)
        features = []
        for i in range(64):
            kernel = vgg16_filters[:, :, :, i]
            kernel = expand_dims(kernel, axis=-1)
            feature1 = tf.nn.conv2d(im1, kernel, [1, 1, 1, 1], padding="VALID")
            feature1 = tf.nn.relu(feature1)
            feature1 = feature1[0, :, :, 0].numpy()
            ret, feature1 = cv2.threshold(feature1, 127, 255, 0)
            filled_rate = feature1.sum() / (feature1.shape[0] * feature1.shape[1] * 255)
            if filled_rate > 0.05:
                features.append(feature1)
        image_features.append((file1, features))
    return image_features


t1 = time.time()
feature_maps = compute_feature_maps()
t2 = time.time()
print(f'compute_feature_maps used time:{t2 - t1}')


def view_feature_map(j):
    x = 8
    y = 8
    for i in range(len(feature_maps[j][1])):
        pyplot.subplot(x, y, i + 1)
        pyplot.imshow(feature_maps[j][1][i], cmap='gray')
    pyplot.show()


SIZE = 28


def normalize1(img):
    img = cv2.resize(img, (SIZE, SIZE))
    ret, img = cv2.threshold(img, 127, 255, 0)
    return img


def compare_feature_maps():
    for feature1 in feature_maps:
        file1 = feature1[0]
        similarity = []
        for feature2 in feature_maps:
            file2 = feature2[0]
            if file1 == file2:
                continue
            distances = []
            for f1 in feature1[1]:
                for f2 in feature2[1]:
                    distance = cv2.matchShapes(f1, f2, cv2.CONTOURS_MATCH_I2, 0)
                    if distance > 0:
                        distances.append(distance)
            sorted_distances = sorted(distances, reverse=False)
            similarity.append((sorted_distances[0], file2))
        sorted_similarity = sorted(similarity, key=lambda x: x[0], reverse=False)
        most_similar = sorted_similarity[0]
        print(f'{file1} is similar to {most_similar[1]}, distance is {most_similar[0]}')


# view_feature_map(images.index('rgb1.jpg'))
compare_feature_maps()
