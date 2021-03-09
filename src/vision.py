import logging
import threading

import cv2
import numpy as np
import skimage.measure
from pynput.mouse import Controller

from . import constants
from . import util
from .featurepack import FeaturePack

logger = logging.getLogger('Vision')
logger.setLevel(logging.DEBUG)

VISION_USED_KERNEL = 'vuk'
USED_CHANNEL = 'channel'
USED_DEGREES = 'degrees'
USED_SPEED = 'speed'
ACTUAL_SPEED_TIMES = 50
ACTUAL_DEGREES_TIMES = 10

FEATURE_THRESHOLD = 20
FEATURE_SIMILARITY_THRESHOLD = 0.2
POOL_BLOCK_SIZE = 2  # after down-sampling, feature is 3x3
HISTOGRAM_BINS = 27


# match the experience vision sense
# @util.timeit
def filter_feature(fp: FeaturePack):
    kernel_arr = util.string_to_feature_matrix(fp.kernel)
    cov = cv2.filter2D(fp.data.get(fp.channel), -1, kernel_arr)
    # down-sampling once use max pool, size is 50% of origin
    new_feature_pool1 = skimage.measure.block_reduce(cov, (POOL_BLOCK_SIZE, POOL_BLOCK_SIZE), np.max)
    # down-sampling again use max pool, size is 25% of origin
    new_feature_pool2 = skimage.measure.block_reduce(new_feature_pool1,
                                                     (POOL_BLOCK_SIZE, POOL_BLOCK_SIZE), np.max)
    # reduce not obvious feature
    threshold_feature = np.where(new_feature_pool2 < FEATURE_THRESHOLD, 0, new_feature_pool2)
    sum_feature = threshold_feature.sum()
    if sum_feature == 0:
        return fp  # no any feature found
    if util.np_array_all_same(threshold_feature):
        return fp  # useless feature data
    standard_feature = util.standardize_feature(threshold_feature)
    new_feature = standard_feature.flatten().astype(int)
    fp.feature = new_feature
    if fp.contrast is not None:
        difference = util.np_array_diff(new_feature, fp.contrast)
        if difference < FEATURE_SIMILARITY_THRESHOLD:
            fp.similar = True
    return fp


def calculate_histogram(img):
    # TODO, use np.bincount() for faster calculation?
    hist_np, bins = np.histogram(img.ravel(), bins=HISTOGRAM_BINS, range=[0, 256])
    return hist_np


class Block(object):
    def __init__(self, x, y, w=0, h=0, ri=0, v=0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.ri = ri
        self.v = v


class Vision(object):
    running = True
    FRAME_WIDTH = 0
    FRAME_HEIGHT = 0
    ROI_ARR = [28, 56, 112]
    INIT_ROI_INDEX = 2

    FEATURE_INPUT_SIZE = 12
    REGION_VARIANCE_THRESHOLD = 0.05
    MAX_DEGREES = 36  # actual is 10 times
    MAX_SPEED = 40  # actual is 50 times, pixel
    MAX_DURATION = 5  # actual is 0.5s
    PROCESS_STATUS_NORMAL = 0
    PROCESS_STATUS_DIGGING = 1
    PROCESS_STATUS_EXPLORING = 2
    PROCESS_STABLE_DURATION = 0.33
    focus_status = 0
    last_focus_state = ''
    last_focus_state_time = 0

    current_block = None
    STATUS = 'sts'
    IN_PROGRESS = 'pgs'
    COMPLETED = 'cmp'
    MOVE = 'move'
    ZOOM_IN = 'zmi'
    ZOOM_OUT = 'zmo'
    ZOOM_LEFT_TOP = 'zlt'
    ZOOM_RIGHT_TOP = 'zrt'
    ZOOM_LEFT_BOTTOM = 'zlb'
    ZOOM_RIGHT_BOTTOM = 'zrb'
    MOVE_UP = 27
    MOVE_DOWN = 9
    MOVE_LEFT = 18
    MOVE_RIGHT = 0
    LAST_MOVE_TIME = 'lmt'
    previous_energies = []
    previous_full_image = None
    previous_histogram1 = None

    FEATURE_DATA = {constants.KERNEL: [], constants.FEATURE: [], constants.SIMILAR: False}
    current_action = {STATUS: COMPLETED}

    is_show = None

    @util.timeit
    def __init__(self):
        # self.mouse = Controller()
        # self.vision_kernels = np.load(self.VISION_KERNEL_FILE)
        # self.init_current_block()
        # fix error of Mac - Process finished with exit code 132 (interrupted by signal 4: SIGILL)
        if self.is_show != 'n':
            cv2.namedWindow("frame", cv2.WND_PROP_FULLSCREEN)

    def start(self):
        sound_thread = threading.Thread(target=self.receive)
        sound_thread.daemon = True
        sound_thread.start()

    def stop(self):
        self.running = False

    # need to overwrite this
    def receive(self):
        print('receive() not implemented!')
        return

    @util.timeit
    def process(self, status, key):
        return
        # old_focus_x = self.current_block.x + self.current_block.w // 2
        # old_focus_y = self.current_block.y + self.current_block.h // 2
        # if self.current_action[self.STATUS] == self.IN_PROGRESS:
        #     self.calculate_move_action(self.current_action)
        #
        # self.match_features()
        # self.search_feature_memory()
        #
        # # when she's mature, below is the major way of focus move/zoom.
        # # self.reproduce_movements()
        # # self.reproduce_zooms()
        #
        # # when she's not mature, need to guide her.
        # this_full_image = self.grab(0, 0, self.FRAME_WIDTH, self.FRAME_HEIGHT)
        # self.calculate_vision_focus_state()
        # if self.current_action[self.STATUS] is not self.IN_PROGRESS:
        #     if key is constants.KEY_ALT or key is constants.KEY_CTRL:
        #         # the 1st and most efficient way is to set focus directly, and reward it
        #         self.move_focus_to_mouse()
        #     else:
        #         # move out from current reward region.
        #         is_aware = self.aware(this_full_image)
        #         if not is_aware:
        #             if self.focus_status is self.PROCESS_STATUS_DIGGING:
        #                 self.dig()
        #             elif self.focus_status is self.PROCESS_STATUS_EXPLORING:
        #                 # if environment not change, random do some change.
        #                 self.explore()
        #
        # self.previous_full_image = this_full_image
        #
        # new_focus_x = self.current_block.x + self.current_block.w // 2
        # new_focus_y = self.current_block.y + self.current_block.h // 2
        # if new_focus_x == old_focus_x and new_focus_y == old_focus_y:
        #     focus = None
        # else:
        #     focus = {constants.FOCUS_X: new_focus_x, constants.FOCUS_Y: new_focus_y}
        # return focus
