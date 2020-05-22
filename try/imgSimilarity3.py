import cv2
import numpy as np

from components.rgb_histogram import RGBHistogram

images = ['head1.jpg', 'head2.jpg', 'head3.jpg', 'head4.jpg', 'head5.jpg', 'head10.jpg', 'head11.jpg', 'gb1.jpg',
          'image1.jpg', 'image2.jpg', 'l1-1.jpg', 'l1-2.jpg', 'manu.jpg', 'rgb1.jpg', 'rgb2.jpg', 's1.png', 's2.png',
          'square1.jpg', 'square2.jpg', 'square3.jpg', 'triangle1.jpg']


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

for file1 in images:
    im1 = cv2.imread(file1)
    features1 = desc.describe(im1)
    similarity = []
    for file2 in images:
        if file1 == file2:
            continue
        d1 = compare(file2, features1)
        similarity.append((d1, file2))
    sorted_similarity = sorted(similarity, key=lambda x: x[0], reverse=False)
    most_similar = sorted_similarity[0]
    print(f'{file1} is similar to {most_similar[1]}, distance is {most_similar[0]}')
