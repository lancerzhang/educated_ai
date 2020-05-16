import cv2
import numpy as np


# This module can classify the image by histogram.
# This method is easy for someone who is a beginner in Image classification.
#
# author MashiMaroLjc
# version 2016-2-16

def classfiy_histogram(image1, image2, size=(64, 64)):
    ''' 'image1' and 'image2' is a Image Object.
    You can build it by 'Image.open(path)'.
    'Size' is parameter what the image will resize to it.It's 256 * 256 when it default.
    This function return the similarity rate betweene 'image1' and 'image2'
    '''
    image1 = cv2.resize(image1, size)
    data1 = np.histogram(image1.ravel(), 16, [0, 256])
    ls1 = data1[0]
    g = ls1.flatten().tolist()

    image2 = cv2.resize(image2, size)
    data2 = np.histogram(image2.ravel(), 16, [0, 256])
    ls2 = data2[0]
    s = ls2.flatten().tolist()

    assert len(g) == len(s), "error"

    data = []

    for index in range(0, len(g)):
        if g[index] != s[index]:
            data.append(1 - abs(g[index] - s[index]) / max(g[index], s[index]))
        else:
            data.append(1)

    return float(sum(data)) / len(g)
