import pickle

import cv2
import imutils
import numpy as np
import tensorflow as tf
from keras.applications.vgg16 import preprocess_input
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import load_img
from numpy import expand_dims

from components import util
from components.rgb_histogram import RGBHistogram

"""
1) RGBHistogram 2) vgg16 top filters + canny + drawContours + matchShapes
"""

files = ['head1.jpg', 'head2.jpg', 'head3.jpg', 'head4.jpg', 'head5.jpg', 'head10.jpg', 'head11.jpg', 'gb1.jpg',
         'image1.jpg', 'image2.jpg', 'l1-1.jpg', 'l1-2.jpg', 'manu.jpg', 'rgb1.jpg', 'rgb2.jpg', 's1.png', 's2.png',
         'square1.jpg', 'square2.jpg', 'square3.jpg', 'triangle1.jpg']

IMG_SIZE = 50

images = {}
for file in files:
    img = cv2.imread(file)
    img = imutils.resize(img, width=IMG_SIZE)
    images.update({file: img})


def chi2_distance(histA, histB, eps=1e-10):
    # compute the chi-squared distance
    d = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps)
                      for (a, b) in zip(histA, histB)])
    # return the chi-squared distance
    return d


def compare(img, feature):
    features2 = desc.describe(img)
    return chi2_distance(feature, features2)


desc = RGBHistogram([6, 6, 6])

with open('vgg16.l1.top.filters', 'rb') as filters:
    vgg16_filters = pickle.load(filters)


def compute_feature_maps():
    image_features = {}
    for file1, image1 in images.items():
        im1 = load_img(file1, target_size=(IMG_SIZE, IMG_SIZE))
        im1 = img_to_array(im1)
        im1 = expand_dims(im1, axis=0)
        im1 = preprocess_input(im1)
        features = []
        for i in range(len(vgg16_filters)):
            kernel = vgg16_filters[i]
            kernel = expand_dims(kernel, axis=-1)
            feature1 = tf.nn.conv2d(im1, kernel, [1, 1, 1, 1], padding="VALID")
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
                features.append(outline)
        image_features.update({file1: features})
    return image_features


feature_maps = compute_feature_maps()


def compare_feature_maps(file1, files):
    similarity = []
    for file2 in files:
        distances = []
        for f1 in feature_maps[file1]:
            for f2 in feature_maps[file2[1]]:
                distance = cv2.matchShapes(f1, f2, cv2.CONTOURS_MATCH_I2, 0)
                if distance > 0:
                    distances.append(distance)
        if len(distances) == 0:
            continue
        sorted_distances = sorted(distances, reverse=False)
        similarity.append((sorted_distances[0], file2))
    if len(similarity) == 0:
        return
    sorted_similarity = sorted(similarity, key=lambda x: x[0], reverse=False)
    most_similar = sorted_similarity[0]
    return most_similar


for file1, im1 in images.items():
    features1 = desc.describe(im1)
    similarity1pass = []
    for file2, im2 in images.items():
        if file1 is file2:
            continue
        d1 = compare(im2, features1)
        if d1 < 1:
            similarity1pass.append((d1, file2))
    if len(similarity1pass) > 0:
        # print(f'{file1} similarity1pass {similarity1pass}')
        most_similar = compare_feature_maps(file1, similarity1pass)
        if most_similar and most_similar[0] < 0.01:
            print(f'{file1} is similar to {most_similar[1]}')
