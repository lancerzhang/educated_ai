import binascii

import cv2
import numpy as np
import scipy.cluster

NUM_CLUSTERS = 10
SIZE = 100
MIN_COUNT_PERCENT = 0.05  # less than this percentage won't be counted


def find_colors(im_cv):
    h, w, c = im_cv.shape
    if h < SIZE or w < SIZE:
        im_cv = cv2.resize(im_cv, (SIZE, SIZE))
        h = SIZE
        w = SIZE
    ar = cv2.cvtColor(im_cv, cv2.COLOR_BGR2RGB)
    shape = ar.shape
    ar = ar.reshape(np.product(shape[:2]), shape[2]).astype(float)
    codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)
    vecs, dist = scipy.cluster.vq.vq(ar, codes)  # assign codes
    counts, bins = np.histogram(vecs, len(codes))  # count occurrences
    hist = []
    total_pixels = h * w
    for i in range(len(counts)):
        if counts[i] > total_pixels * MIN_COUNT_PERCENT:
            hist.append([counts[i] / total_pixels, codes[i],
                         binascii.hexlify(bytearray(int(c) for c in codes[i])).decode('ascii')])
    return sorted(hist, key=lambda x: x[0], reverse=True)
