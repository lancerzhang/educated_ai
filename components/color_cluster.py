import binascii

import numpy as np
import scipy.cluster
from PIL import Image

NUM_CLUSTERS = 10
SIZE = 100


def cluster(file):
    im = Image.open(file)
    im = im.resize((SIZE, SIZE))  # optional, to reduce time
    ar = np.asarray(im)
    shape = ar.shape
    ar = ar.reshape(np.product(shape[:2]), shape[2]).astype(float)
    codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)
    vecs, dist = scipy.cluster.vq.vq(ar, codes)  # assign codes
    counts, bins = np.histogram(vecs, len(codes))  # count occurrences
    hist = []
    for i in range(len(counts)):
        if counts[i] > SIZE * SIZE * 0.05:
            hist.append([counts[i], codes[i], binascii.hexlify(bytearray(int(c) for c in codes[i])).decode('ascii')])
    return sorted(hist, key=lambda x: x[0], reverse=True)
