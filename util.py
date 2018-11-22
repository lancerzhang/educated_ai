import time, numpy, cv2, random, math
import numpy as np

USED_COUNT = 'uct'


def time_diff(start):
    return time.time() - start


def between(val, m, n):
    return m <= val <= n


# TODO, need to consider other audio format
# normalize audio data
def normalize_audio_data(raw):
    return raw / 32768.0  # assume 16 bit


# calculate energy
def rms(x):
    return numpy.sqrt(x.dot(x) / x.size)


# return common elements in 2 lists
def list_common(list1, list2):
    return list(set(list1).intersection(list2))


# count each element in a list, return a dict, key is the element in list, value is count
def list_element_count(list1):
    return dict((a, list1.count(a)) for a in list1)


# list a - b, return new list
def list_comprehension_new(list1, list2):
    return [x for x in list1 if x not in list2]


def list_comprehension_existing(list1, list2):
    tobe_remove = list_common(list1, list2)
    for el1 in tobe_remove:
        list1.remove(el1)


def list_concat(list1, list2):
    return np.concatenate([list1, list2])


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


def sort_color(rgb):
    return str(rgb[0] / 86) + str(rgb[1] / 86) + str(rgb[2] / 86)


def point_color_category(img):
    reg_point = cv2.resize(img, (1, 1))
    return sort_color(reg_point[0, 0])


def color_hist(rgb, bins):
    num = 256 / bins + 1
    r = rgb[:, :, 0].flatten()
    g = rgb[:, :, 1].flatten()
    b = rgb[:, :, 2].flatten()
    bc1 = np.bincount(r / num, minlength=3)
    bc2 = np.bincount(g / num, minlength=3)
    bc3 = np.bincount(b / num, minlength=3)
    return np.concatenate((bc1, bc2, bc3))


def color_hist_similarity(img1, img2, resize=32, bins=3):
    img1 = cv2.resize(img1, (resize, resize))
    img2 = cv2.resize(img2, (resize, resize))
    g = color_hist(img1, bins).astype(float)
    s = color_hist(img2, bins).astype(float)
    data = []
    for index in range(0, len(g)):
        if g[index] != s[index]:
            data.append(1 - abs(g[index] - s[index]) / max(g[index], s[index]))
        else:
            data.append(1)
    return sum(data) / len(g)


def hamming(h1, h2):
    h, d = 0, h1 ^ h2
    while d:
        h += 1
        d &= d - 1
    return h


def image_hash(im, size):
    resized_image = cv2.resize(im, (size, size))
    gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
    data = gray.flatten().tolist()
    avg_value = reduce(lambda x, y: x + y, data) / (size * size)
    return reduce(lambda x, (y, z): x | (z << y), enumerate(map(lambda i: 0 if i < avg_value else 1, data)), 0)


def avg(arr):
    return sum(arr) / len(arr)


def standardize_feature(matrix):
    while sum(matrix[0]) == 0:
        matrix = np.roll(matrix, -1, axis=0)
    while sum(matrix[:, 0]) == 0:
        matrix = np.roll(matrix, -1, axis=1)
    return matrix


def compare_feature(feature1, feature2):
    matrix = [feature1, feature2]
    max_list = np.max(matrix, axis=0)
    # avoid 0 division
    standard_max_list = np.where(max_list == 0, 9999999, max_list)
    diff = abs(feature1.astype(int) - feature2.astype(int))
    differences = diff / standard_max_list.astype(float)
    difference = avg(differences)
    return difference


def histogram_array_diff(his_arr1, his_arr2):
    return


def get_top_rank(rank_list):
    ri = random.randint(0, 9)
    if len(rank_list) == 0 or ri == 0:
        return None
    else:
        return rank_list[0]


def update_rank_list(key_key, key_value, rank_list):
    element = next((x for x in rank_list if x[key_key] is key_value), None)
    if element is None:
        element = {key_key: key_value, USED_COUNT: 1}
        rank_list = np.append(rank_list, element)
    else:
        element[USED_COUNT] = element[USED_COUNT] + 1
    return sorted(rank_list, key=lambda x: (x[key_key]), reverse=True)


def matrix_to_string(matrix):
    arr = matrix.flatten()
    matrix_str = ','.join(str(e) for e in arr)
    return matrix_str


def string_to_feature_matrix(string):
    arr = np.fromstring(string, dtype=int, sep=',')
    matrix = np.reshape(arr, (3, 3))
    return matrix
