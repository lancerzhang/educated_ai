# TensorFlow and tf.keras
# Helper libraries
import time
from multiprocessing import Pool

import cv2
import imagehash
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from PIL import Image
from tensorflow import keras

from components import util

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
MIN_DISTANCE = 0.2
COMMON_RATE = 0.6
image_group = np.load('image_group.npy', allow_pickle=True)
image_group = image_group[()]

selected_group = 9
selected_index = 0
CV_THRESHOLD = 64
selected_image = train_images[image_group[9][0]]
ret, selected_image = cv2.threshold(selected_image, CV_THRESHOLD, 255, cv2.THRESH_BINARY)
# compare_images = [0, 2, 3, 6, 8, 9, 10, 11, 12, 15]
compare_images = range(10)
all_matched_seq = []

IMG_SIZE = 14


def np_2d_array_nonzero_box(arr):
    nz = arr.nonzero()
    if len(nz[0]) > 0 and len(nz[1]) > 0:
        return arr[min(nz[0]):max(nz[0]) + 1, min(nz[1]):max(nz[1]) + 1]
    else:
        return arr


def get_fill_rate(img):
    return img.sum() / (img.shape[0] * img.shape[1] * 255)


def resize_img(img):
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    return img


def prepare_img(img):
    ret, img = cv2.threshold(img, CV_THRESHOLD, 255, cv2.THRESH_BINARY)
    if util.img_has_content(img):
        img = util.np_2d_array_nonzero_box(img)
        img = resize_img(img)
        return img


def compare_img(im1, im2):
    im1 = prepare_img(im1)
    im2 = prepare_img(im2)
    if im1 is None or im2 is None:
        return False
    im1 = Image.fromarray(im1)
    h1 = imagehash.phash(im1)
    im2 = Image.fromarray(im2)
    h2 = imagehash.phash(im2)
    d = h1 - h2
    if d < IMG_SIZE * IMG_SIZE * 0.12:
        return True
    else:
        return False


def get_seq_let_right_down(img, size):
    x = size
    y = size
    step = SIZE_UNIT
    width = SIZE_UNIT + (4 - size) * SIZE_UNIT
    blocks_seqs = []
    img_seq = []
    move_seq = []
    direction = 'R'
    for j in range(y):
        for i in range(x):
            if j > 0 and i < x - 1:
                continue
            if j == 0 and i == x - 1:
                direction = 'D'
            p_x = i * step
            p_y = j * step
            block = img[p_y:p_y + width, p_x:p_x + width]
            if get_fill_rate(block) < MIN_FILL_RATE:
                return blocks_seqs
            img_seq.append(block)
            move_seq.append(direction)
            if len(img_seq) > 1:
                blocks_seqs.append([img_seq.copy(), move_seq.copy()])
    return blocks_seqs


def get_seq_let_right_up(img, size):
    x = size
    y = size
    step = SIZE_UNIT
    width = SIZE_UNIT + (4 - size) * SIZE_UNIT
    blocks_seqs = []
    img_seq = []
    move_seq = []
    direction = 'R'
    for j in reversed(range(y)):
        for i in range(x):
            if j < y - 1 and i < x - 1:
                continue
            if j == y - 1 and i == x - 1:
                direction = 'U'
            p_x = i * step
            p_y = j * step
            block = img[p_y:p_y + width, p_x:p_x + width]
            if get_fill_rate(block) < MIN_FILL_RATE:
                return blocks_seqs
            img_seq.append(block)
            move_seq.append(direction)
            if len(img_seq) > 1:
                blocks_seqs.append([img_seq.copy(), move_seq.copy()])
    return blocks_seqs


def get_blocks_seqs(img, size):
    blocks_seq1 = get_seq_let_right_down(img, size)
    blocks_seq2 = get_seq_let_right_up(img, size)
    return blocks_seq1 + blocks_seq2


def get_all_block_seqs(img):
    blocks_seq1 = get_blocks_seqs(img, MEDIUM)
    blocks_seq2 = get_blocks_seqs(img, LARGE)
    return blocks_seq1 + blocks_seq2


def match_block_seq(img_seq, move_seq, img, width, x_start, y_start):
    matched_seq = []
    for i in range(1, len(img_seq)):
        block1 = img_seq[i]
        direction = move_seq[i - 1]
        if direction == 'R':
            x_start += SIZE_UNIT
        elif direction == 'D':
            y_start += SIZE_UNIT
        elif direction == 'U':
            y_start -= SIZE_UNIT
        img_width = img.shape[0]
        img_height = img.shape[1]
        x_end = x_start + width
        y_end = y_start + width
        if x_start < 0 or y_start < 0 or x_end > img_width or y_end > img_height:
            return False
        block2 = img[y_start:y_end, x_start:x_end]
        if not compare_img(block1, block2):
            return False
        else:
            matched_seq.append([block1, block2])
            all_matched_seq.append([block1, block2])
    # np.save(str(time.time()), matched_seq)
    return True


def search_block_seq(img_seq, move_seq, img, size):
    x = size
    y = size
    step = SIZE_UNIT
    width = SIZE_UNIT + (4 - size) * SIZE_UNIT
    for j in range(y):
        for i in range(x):
            p_x = i * step
            p_y = j * step
            block2 = img[p_y:p_y + width, p_x:p_x + width]
            if compare_img(img_seq[0], block2):
                if match_block_seq(img_seq, move_seq, img, width, p_x, p_y):
                    return True
    return False


def has_similar_block_seq(params):
    block1 = params[0]
    compare_img = params[1]
    img_seq = block1[0]
    move_seq = block1[1]
    ret, img = cv2.threshold(compare_img, CV_THRESHOLD, 255, cv2.THRESH_BINARY)
    has_seq = search_block_seq(img_seq, move_seq, img, LARGE)
    if not has_seq:
        has_seq = search_block_seq(img_seq, move_seq, img, MEDIUM)
    return has_seq


def show_blocks_seqs(all_block_seqs):
    size = 6
    idx = 1
    for block_seqs in all_block_seqs:
        block_seq = block_seqs[0]
        for block in block_seq:
            plt.subplot(size, size, idx)
            idx += 1
            plt.imshow(block, cmap='gray')
    plt.show()


def show_blocks(all_blocks_pair, size=6):
    idx = 1
    for blocks_pair in all_blocks_pair:
        plt.subplot(size, size, idx)
        idx += 1
        plt.imshow(blocks_pair[0], cmap='gray')
        plt.subplot(size, size, idx)
        idx += 1
        plt.imshow(blocks_pair[1], cmap='gray')
    plt.show()


if __name__ == '__main__':
    time1 = time.time()
    pool = Pool()
    base_block_seqs = get_all_block_seqs(selected_image)
    print(f'base_block_seqs len {len(base_block_seqs)}')
    # show_blocks_seqs(base_block_seqs)
    all_common_block_seqs = []
    for common_block_seq in base_block_seqs:
        common_n = 0
        pool_params = []
        for i in range(1, len(compare_images)):
            img = train_images[image_group[selected_group][compare_images[i]]]
            pool_params.append([common_block_seq, img])
            if has_similar_block_seq([common_block_seq, img]):
                common_n += 1
        # results = pool.map(has_similar_block_seq, pool_params)
        # for result in results:
        #     if result:
        #         common_n += 1
        print(f'common_n {common_n}')
        if common_n > len(compare_images) * COMMON_RATE:
            all_common_block_seqs.append(common_block_seq)
    print(f'all_common_block_seqs len {len(all_common_block_seqs)}')
    show_blocks_seqs(all_common_block_seqs)
    # print(len(all_matched_seq))
    show_blocks(all_matched_seq, 10)
    time2 = time.time()
    print(f'used time {time2 - time1}')
