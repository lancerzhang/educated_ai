# TensorFlow and tf.keras
# Helper libraries
import time
from multiprocessing import Pool

import cv2
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow import keras

print(tf.__version__)

fashion_mnist = keras.datasets.fashion_mnist

(train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()

class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

SMALL = 4
MEDIUM = 3
LARGE = 2

SIZE_UNIT = 7
BASE_SIZE = 14
MIN_FILL_RATE = 0.05
MIN_DISTANCE = 0.05
image_group = np.load('image_group.npy', allow_pickle=True)
image_group = image_group[()]

selected_group = 9
selected_index = 0
selected_image = train_images[image_group[9][0]]
ret, selected_image = cv2.threshold(selected_image, 127, 255, cv2.THRESH_BINARY)
# compare_images = [0, 2, 3, 6, 8, 9, 10, 11, 12, 15]
compare_images = range(500)


# selected_image = cv2.Canny(selected_image, 30, 200)


def get_blocks(img, size):
    blocks = []
    x = size
    y = size
    step = SIZE_UNIT
    width = SIZE_UNIT + (4 - size) * SIZE_UNIT
    for i in range(x):
        for j in range(y):
            p_x = i * step
            p_y = j * step
            blocks.append(img[p_x:p_x + width, p_y:p_y + width])
    return blocks


def get_all_blocks(img):
    blocks = get_blocks(img, MEDIUM)
    blocks2 = get_blocks(img, LARGE)
    for b in blocks2:
        b = cv2.resize(b, (BASE_SIZE, BASE_SIZE))
        blocks.append(b)
    return blocks


def show_block(size):
    blocks = get_blocks(selected_image, size)
    for i in range(len(blocks)):
        plt.subplot(size, size, i + 1)
        plt.imshow(blocks[i], cmap='gray')
    plt.show()


def has_similar_block(params):
    block1 = params[0]
    common_blocks = params[1]
    filled_rate1 = block1.sum() / (block1.shape[0] * block1.shape[1] * 255)
    if filled_rate1 < MIN_FILL_RATE:
        return False
    for block2 in common_blocks:
        filled_rate2 = block2.sum() / (block2.shape[0] * block2.shape[1] * 255)
        if filled_rate2 < MIN_FILL_RATE:
            continue
        distance = cv2.matchShapes(block1, block2, cv2.CONTOURS_MATCH_I2, 0)
        if distance < MIN_DISTANCE:
            return True
    return False


def has_similar_block2(params):
    block1 = params[0]
    img = params[1]
    ret, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    blocks = get_all_blocks(img)
    return has_similar_block([block1, blocks])


def find_similar_blocks(blocks):
    similar_blocks = []
    for block in blocks:
        if not has_similar_block([block, similar_blocks]):
            similar_blocks.append(block)
    return similar_blocks


def show_blocks(blocks):
    size = 4
    for i in range(len(blocks)):
        plt.subplot(size, size, i + 1)
        plt.imshow(blocks[i], cmap='gray')
    plt.show()


if __name__ == '__main__':
    time1 = time.time()
    pool = Pool()
    base_blocks = get_all_blocks(selected_image)
    all_common_blocks = []
    for common_block in base_blocks:
        common_n = 0
        pool_params = []
        for i in range(1, len(compare_images)):
            img = train_images[image_group[selected_group][compare_images[i]]]
            pool_params.append([common_block, img])
        results = pool.map(has_similar_block2, pool_params)
        for result in results:
            if result:
                common_n += 1
        print(f'common_n {common_n}')
        if common_n > len(compare_images) * 0.5:
            all_common_blocks.append(common_block)
    print(len(all_common_blocks))
    show_blocks(all_common_blocks)
    time2 = time.time()
    print(f'used time {time2 - time1}')
