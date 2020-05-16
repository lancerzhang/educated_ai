import cv2
import numpy as np

from components.rgb_histogram import RGBHistogram


def chi2_distance(histA, histB, eps=1e-10):
    # compute the chi-squared distance
    d = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps)
                      for (a, b) in zip(histA, histB)])
    # return the chi-squared distance
    return d


def compare(img, feature):
    image2 = cv2.imread(img)
    features2 = desc.describe(image2)
    return chi2_distance(feature, features2)


desc = RGBHistogram([8, 8, 8])
image = cv2.imread('head1.jpg')
# t1 = time.time()
features1 = desc.describe(image)
# t2 = time.time()
# print(features1)
# print((t2 - t1) * 1000)

images = ['head2.jpg', 'head3.jpg', 'head4.jpg', 'head5.jpg']
for img in images:
    print(compare(img, features1))
