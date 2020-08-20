import colorsys
import functools

import cv2
import numpy as np

import components.color_cluster as cc

MAX = 179
WIDTH = 5


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


def has_hue(hue, palettes_hsv):
    v_range = get_ranges(hue)
    for item in v_range:
        for i in range(item[0], item[1]):
            if i in palettes_hsv:
                return True
    return False


class ImgPalette:
    sv_variance = 0.03
    h_variance = 5

    def __init__(self, file):
        palettes = cc.cluster(file)
        print(palettes)
        self.grey = cv2.imread(file, 0)
        self.im_hsv = cv2.cvtColor(cv2.imread(file, 1), cv2.COLOR_BGR2HSV)
        palettes_hsv = {}
        for item in palettes:
            palette = item[1].astype(int)
            print(palette)
            r, g, b = palette
            palette_hsv = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            # print(palette_hsv)
            h, s, v = palette_hsv
            if v <= self.sv_variance:
                cv_h = 'Black'
            elif v >= 1 - self.sv_variance and s <= self.sv_variance:
                cv_h = 'White'
            elif s <= self.sv_variance:
                cv_h = 'Grey'
            else:
                cv_h = int(h * 180)
            cv_s = int(s * 255)
            cv_v = int(v * 255)
            if isinstance(cv_h, int):
                print(h * 360, s * 100, v * 100)
                if not has_hue(cv_h, palettes_hsv):
                    palettes_hsv[cv_h] = (cv_h, cv_s, cv_v)
                    print(f'has hue {h * 360, s * 100, v * 100}')
            else:
                if cv_h not in palettes_hsv:
                    palettes_hsv[cv_h] = (cv_h, cv_s, cv_v)
        self.palettes_hsv = palettes_hsv

    def get_filtered_color_image(self, rank):
        masks = []
        palette = self.palettes_hsv[rank]
        hue = palette[0]
        if hue == 'Black':
            full_mask = cv2.inRange(self.im_hsv, (0, 0, 0), (179, 255, int(255 * self.sv_variance)))
        elif hue == 'White':
            full_mask = cv2.inRange(self.im_hsv, (0, 0, int(255 * (1 - self.sv_variance))),
                                    (179, int(255 * self.sv_variance), 255))
        elif hue == 'Grey':
            full_mask = cv2.inRange(self.im_hsv, (0, 0, 0),
                                    (179, int(255 * self.sv_variance), 255))
        else:
            for idx_pair in get_ranges(hue):
                mask = cv2.inRange(self.im_hsv, (idx_pair[0], 50, 50), (idx_pair[1], 255, 255))
                mask = mask.astype('bool')
                masks.append(mask)
            full_mask = functools.reduce(lambda a, b: a + b, masks)
        return self.im_hsv * np.dstack((full_mask, full_mask, full_mask))

    def get_filtered_gray_image(self, rank):
        masks = []
        palette = self.palettes_hsv[rank]
        hue = palette[0]
        if hue == 'Black':
            full_mask = cv2.inRange(self.im_hsv, (0, 0, 0), (179, 255, int(255 * self.sv_variance)))
        elif hue == 'White':
            full_mask = cv2.inRange(self.im_hsv, (0, 0, int(255 * (1 - self.sv_variance))),
                                    (179, int(255 * self.sv_variance), 255))
        elif hue == 'Grey':
            full_mask = cv2.inRange(self.im_hsv, (0, 0, 0),
                                    (179, int(255 * self.sv_variance), 255))
        else:
            for idx_pair in get_ranges(hue):
                mask = cv2.inRange(self.im_hsv, (idx_pair[0], 50, 50), (idx_pair[1], 255, 255))
                mask = mask.astype('bool')
                masks.append(mask)
            full_mask = functools.reduce(lambda a, b: a + b, masks)
        h, s, v1 = cv2.split(self.im_hsv)
        return v1 * full_mask
