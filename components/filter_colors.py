import functools

import cv2
import numpy as np

MAX = 179
WIDTH = 10


def get_ranges(pos):
    idx_list = []
    low_idx = pos - WIDTH
    high_idx = pos + WIDTH
    if low_idx < 0:
        idx_list.append((0, high_idx))
        idx_list.append((MAX + low_idx, MAX))
    elif high_idx > MAX:
        idx_list.append((low_idx, MAX))
        idx_list.append((0, high_idx - MAX))
    else:
        idx_list.append((low_idx, high_idx))
    return idx_list


def fill_mask(mask, ranges):
    for r in ranges:
        mask[r[0]:(r[1] + 1)] = -1


def append_ranges(ranges, next_rank, mask):
    next_ranges = get_ranges(next_rank)
    ranges.append(next_ranges)
    fill_mask(mask, next_ranges)


def get_rank_ranges(arr, num=1):
    rank_ranges = []
    mask = np.arange(0, 180)
    top_rank = arr[0][0]
    append_ranges(rank_ranges, top_rank, mask)
    # print(f'top_rank:{top_rank}')
    for i in range(1, num):
        next_rank = get_next_rank(arr, mask)
        if next_rank > -1:
            # print(f'next_rank:{next_rank}')
            append_ranges(rank_ranges, next_rank, mask)
    return rank_ranges


def get_next_rank(arr, mask):
    for i in range(0, len(arr)):
        idx = arr[i][0]
        if idx in mask:
            return idx
    return -1


"""
Can't detect light color!!
"""


class FilterColors:
    def __init__(self, img):
        self.img = img
        im_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        self.img_hsv = im_hsv
        hist = cv2.calcHist([im_hsv], [0], None, [180], [0, 256])
        seq_hist = [(idx, int(val[0])) for idx, val in enumerate(hist)]
        rank_hist = sorted(seq_hist, key=lambda x: x[1], reverse=True)
        self.rank_ranges = get_rank_ranges(rank_hist, 9)

    def get_filtered_color_image(self, rank):
        masks = []
        for idx_pair in self.rank_ranges[rank]:
            mask = cv2.inRange(self.img_hsv, (idx_pair[0], 50, 50), (idx_pair[1], 245, 245))
            mask = mask.astype('bool')
            masks.append(mask)
        full_mask = functools.reduce(lambda a, b: a + b, masks)
        return self.img * np.dstack((full_mask, full_mask, full_mask))

    def get_filtered_gray_image(self, rank):
        masks = []
        for idx_pair in self.rank_ranges[rank]:
            mask = cv2.inRange(self.img_hsv, (idx_pair[0], 50, 50), (idx_pair[1], 245, 245))
            mask = mask.astype('bool')
            masks.append(mask)
        full_mask = functools.reduce(lambda a, b: a + b, masks)
        h, s, v1 = cv2.split(self.img_hsv)
        return v1 * full_mask
