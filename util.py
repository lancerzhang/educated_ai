import time, numpy, cv2
import numpy as np


def time_diff(start):
    return time.time() - start


def between(val, m, n):
    return m <= val <= n


# TODO, need to consider other audio format
# normalize audio data
def normalizeAudioData(raw):
    return raw / 32768.0  # assume 16 bit


# calculate energy
def rms(x):
    return numpy.sqrt(x.dot(x) / x.size)


# return common elements in 2 lists
def common_elements(list1, list2):
    return list(set(list1).intersection(list2))


# count each element in a list, return a dict, key is the element in list, value is count
def list_element_count(list1):
    return dict((a, list1.count(a)) for a in list1)


# list a - b, return new list
def comprehension_new(list1, list2):
    return [x for x in list1 if x not in list2]


def comprehension(list1, list2):
    tobe_remove = common_elements(list1, list2)
    for el1 in tobe_remove:
        list1.remove(el1)


def calculate_similarity(value, similarity):
    min, max = 0, 0
    if value > 0:
        min = value * (1 - similarity)
        max = value * (1 + similarity)
    else:
        min = value * (1 + similarity)
        max = value * (1 - similarity)
    return [min, max]


def delete_empty_surround(arr):
    shape = arr.shape
    for col_num in range(shape[1] - 1, 0, -1):
        if arr[:, col_num].sum() == 0:
            arr = np.delete(arr, col_num, 1)
        else:
            break

    for row_num in range(shape[0] - 1, 0, -1):
        if arr[row_num].sum() == 0:
            arr = np.delete(arr, row_num, 0)
        else:
            break

    shape = arr.shape
    col_to_delete = []
    for col_num in range(0, shape[1] - 1):
        if arr[:, col_num].sum() == 0:
            col_to_delete.append(col_num)
        else:
            break
    arr = np.delete(arr, col_to_delete, 1)

    row_to_delete = []
    for row_num in range(0, shape[0] - 1):
        if arr[row_num].sum() == 0:
            row_to_delete.append(row_num)
        else:
            break
    arr = np.delete(arr, row_to_delete, 0)

    return arr


def colorSorter(rgb):
    return str(rgb[0] / 86) + str(rgb[1] / 86) + str(rgb[2] / 86)


def hamming(h1, h2):
    h, d = 0, h1 ^ h2
    while d:
        h += 1
        d &= d - 1
    return h


def imgHash(im, size):
    resized_image = cv2.resize(im, (size, size))
    gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
    data = gray.flatten().tolist()
    avg = reduce(lambda x, y: x + y, data) / (size * size)
    return reduce(lambda x, (y, z): x | (z << y), enumerate(map(lambda i: 0 if i < avg else 1, data)), 0)
