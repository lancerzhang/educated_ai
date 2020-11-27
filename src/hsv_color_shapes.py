import colorsys

import cv2
import numpy as np

import src.rgb_top_colors as mc

RGB_MAX = 255
HUE_MAX = 179
SV_MAX = 255
SV_EDGE = 0.03  # max is 1
H_VARIANCE = 5  # max is 180
SV_VARIANCE = 50  # max is 255


def get_ranges(pos):
    idx_list = []
    low_idx = pos - H_VARIANCE
    high_idx = pos + H_VARIANCE
    if low_idx < 0:
        idx_list.append((0, high_idx))
        idx_list.append((HUE_MAX + low_idx, HUE_MAX))
    elif high_idx > HUE_MAX:
        idx_list.append((low_idx, HUE_MAX))
        idx_list.append((0, high_idx - HUE_MAX))
    else:
        idx_list.append((low_idx, high_idx))
    return idx_list


def has_hue(hue, top_colors_hsv):
    v_range = get_ranges(hue)
    for item in v_range:
        for i in range(item[0], item[1]):
            if i in top_colors_hsv:
                return True
    return False


def get_mask(color, im_hsv):
    masks = []
    h, s, v = color
    if h == 'Black':
        full_mask = cv2.inRange(im_hsv, (0, 0, 0), (179, 255, int(255 * SV_EDGE)))
    elif h == 'White':
        full_mask = cv2.inRange(im_hsv, (0, 0, int(255 * (1 - SV_EDGE))), (179, int(255 * SV_EDGE), 255))
    elif h == 'Grey':
        full_mask = cv2.inRange(im_hsv, (0, 0, 0), (179, int(255 * SV_EDGE), 255))
    else:
        for idx_pair in get_ranges(h):
            low_s = s - SV_VARIANCE
            high_s = s + SV_VARIANCE
            low_v = v - SV_VARIANCE
            high_v = v + SV_VARIANCE
            mask = cv2.inRange(im_hsv, (idx_pair[0], low_s, low_v), (idx_pair[1], high_s, high_v))
            mask = mask.astype('bool')
            masks.append(mask)
        if len(masks) == 2:
            full_mask = masks[0] + masks[1]
        else:
            full_mask = masks[0]
    return full_mask


class ColorShape:

    def __init__(self, im_cv):
        rgb_colors = mc.find_colors(im_cv)
        self.im_hsv = cv2.cvtColor(im_cv, cv2.COLOR_BGR2HSV)
        top_colors_hsv = {}
        for rbg_color in rgb_colors:
            r, g, b = rbg_color[1].astype(int)
            color_hsv = colorsys.rgb_to_hsv(r / RGB_MAX, g / RGB_MAX, b / RGB_MAX)
            h, s, v = color_hsv
            if v <= SV_EDGE:
                cv_h = 'Black'
            elif v >= 1 - SV_EDGE and s <= SV_EDGE:
                cv_h = 'White'
            elif s <= SV_EDGE:
                cv_h = 'Grey'
            else:
                cv_h = int(h * 180)
            cv_s = int(s * 255)
            cv_v = int(v * 255)
            if isinstance(cv_h, int):
                if not has_hue(cv_h, top_colors_hsv):
                    top_colors_hsv[cv_h] = (cv_h, cv_s, cv_v)
            else:
                if cv_h not in top_colors_hsv:
                    top_colors_hsv[cv_h] = (cv_h, cv_s, cv_v)
        self.top_colors_hsv = top_colors_hsv

    def get_color_shape(self, rank):
        mask = get_mask(self.top_colors_hsv[rank], self.im_hsv)
        return self.im_hsv * np.dstack((mask, mask, mask))

    def get_grey_shape(self, rank):
        mask = get_mask(self.top_colors_hsv[rank], self.im_hsv)
        h, s, v = cv2.split(self.im_hsv)
        return v * mask
