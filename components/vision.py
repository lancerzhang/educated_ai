import copy
import hashlib
import logging
import math
import random
import time
from multiprocessing import Pool

import cv2
import numpy as np
import skimage.measure
from pynput.mouse import Controller

from . import constants
from . import memory
from . import util
from .brain import Brain
from .favor import Favor
from .featurepack import FeaturePack
from .memory import Memory
from .memory import MemoryType
from .memory import RealType

logger = logging.getLogger('Vision')
logger.setLevel(logging.INFO)

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
    VISION_KERNEL_FILE = 'kernels.npy'
    previous_energies = []
    previous_full_image = None
    previous_histogram1 = None

    FEATURE_DATA = {constants.KERNEL: [], constants.FEATURE: [], constants.SIMILAR: False}
    current_action = {STATUS: COMPLETED}

    is_show = None

    @util.timeit
    def __init__(self, brain: Brain, favor: Favor):
        self.brain = brain
        self.favor = favor
        self.mouse = Controller()
        self.vision_kernels = np.load(self.VISION_KERNEL_FILE)
        self.init_current_block()
        # fix error of Mac - Process finished with exit code 132 (interrupted by signal 4: SIGILL)
        if self.is_show is not 'n':
            cv2.namedWindow("frame", cv2.WND_PROP_FULLSCREEN)
        self.pool = Pool()

    @util.timeit
    def init_current_block(self):
        center_x = self.FRAME_WIDTH // 2
        center_y = self.FRAME_HEIGHT // 2
        width = self.ROI_ARR[self.INIT_ROI_INDEX]
        half_width = width // 2
        self.current_block = Block(center_x - half_width, center_y - half_width, width, width, self.INIT_ROI_INDEX)

    @util.timeit
    def process(self, status, key):
        old_focus_x = self.current_block.x + self.current_block.w // 2
        old_focus_y = self.current_block.y + self.current_block.h // 2
        if self.current_action[self.STATUS] == self.IN_PROGRESS:
            self.calculate_move_action(self.current_action)

        self.match_features()
        self.search_feature_memory()

        # when she's mature, below is the major way of focus move/zoom.
        # self.reproduce_movements()
        # self.reproduce_zooms()

        # when she's not mature, need to guide her.
        this_full_image = self.grab(0, 0, self.FRAME_WIDTH, self.FRAME_HEIGHT)
        self.calculate_vision_focus_state()
        if self.current_action[self.STATUS] is not self.IN_PROGRESS:
            if key is constants.KEY_ALT or key is constants.KEY_CTRL:
                # the 1st and most efficient way is to set focus directly, and reward it
                self.move_focus_to_mouse()
            else:
                # move out from current reward region.
                is_aware = self.aware(this_full_image)
                if not is_aware:
                    if self.focus_status is self.PROCESS_STATUS_DIGGING:
                        self.dig()
                    elif self.focus_status is self.PROCESS_STATUS_EXPLORING:
                        # if environment not change, random do some change.
                        self.explore()

        self.previous_full_image = this_full_image

        new_focus_x = self.current_block.x + self.current_block.w // 2
        new_focus_y = self.current_block.y + self.current_block.h // 2
        if new_focus_x == old_focus_x and new_focus_y == old_focus_y:
            focus = None
        else:
            focus = {constants.FOCUS_X: new_focus_x, constants.FOCUS_Y: new_focus_y}
        return focus

    @util.timeit
    def match_features(self):
        feature_memories = self.brain.get_matching_real_memories(RealType.VISION_FEATURE)
        img = self.get_region(self.current_block)
        y, u, v = get_channel_imgs(img)
        data_map = {}
        data_map.update({'y': self.get_data_map(y)})
        data_map.update({'u': self.get_data_map(u)})
        data_map.update({'v': self.get_data_map(v)})
        data_inputs = [FeaturePack(mid=m.mid, kernel=m.kernel, channel=m.channel, contrast=m.feature, data=data_map) for
                       m in feature_memories]
        for fp in self.pool.imap_unordered(filter_feature, data_inputs):
            if fp.similar:
                m = self.brain.memory_indexes.get(fp.mid)
                m.matched()
                cv2.imwrite(f'img/{hashlib.sha1(img).hexdigest()}.jpg', img)
                self.update_used_kernel(fp.kernel)
                self.update_used_channel(fp.channel)

    @util.timeit
    def reproduce(self):
        self.reproduce_movements()
        self.reproduce_zooms()

    @util.timeit
    def reproduce_movements(self):
        feature_memories = self.brain.get_matched_slice_memories(RealType.VISION_FOCUS_MOVE)
        for m in feature_memories:
            for c in m.children:
                self.reproduce_movement(c)
            m.post_matched()

    @util.timeit
    def reproduce_zooms(self):
        feature_memories = self.brain.get_matched_slice_memories(RealType.VISION_FOCUS_ZOOM)
        for m in feature_memories:
            for c in m.children:
                self.reproduce_zoom(c)
            m.post_matched()

    # get a frequent use kernel or a random kernel by certain possibility
    @util.timeit
    def get_kernel(self):
        used_kernel = None
        ri = random.randint(0, 9) - 1
        if ri >= 0:
            used_kernel = self.favor.top(VISION_USED_KERNEL, ri)

        if used_kernel is None:
            shape = self.vision_kernels.shape
            index = random.randint(0, shape[0] - 1)
            kernel = self.vision_kernels[index]
        else:
            kernel = used_kernel.key
        logger.debug(f'get_kernel:{kernel}')
        return kernel

    @util.timeit
    def update_used_kernel(self, kernel):
        self.favor.update(VISION_USED_KERNEL, kernel)

    # try to search more detail
    @util.timeit
    def search_feature_memory(self):
        feature = self.search_feature(self.current_block)
        if feature.feature is None:
            return
        self.brain.put_feature_memory(RealType.VISION_FEATURE, feature.kernel, feature.feature, channel=feature.channel)
        self.update_used_kernel(feature.kernel)
        self.update_used_channel(feature.channel)

    @util.timeit
    def get_data_map(self, channel_img):
        return cv2.resize(channel_img, (self.FEATURE_INPUT_SIZE, self.FEATURE_INPUT_SIZE))

    @util.timeit
    def aware(self, image):
        duration = self.get_duration()
        block = self.find_most_variable_block_division(image, 0, 0, self.FRAME_WIDTH, self.FRAME_HEIGHT,
                                                       self.current_block.w, self.current_block.h)
        if block is None:
            return None
        if block.v < self.REGION_VARIANCE_THRESHOLD:
            return None
        # move focus to variable region
        self.set_movement_absolute(block, duration)
        return True

    # reduce number of histogram call,it's time consuming
    @util.timeit
    def find_most_variable_block_division(self, this_full_image, start_x, start_y, width, height, focus_width,
                                          focus_height):
        if self.previous_full_image is None:
            self.previous_histogram1 = self.calculate_blocks_histogram(this_full_image, 2, 2, width // 2, height // 2)
            return None
        this_valid_region = this_full_image[start_y:start_y + height, start_x:start_x + width]
        previous_valid_region = self.previous_full_image[start_y:start_y + height, start_x:start_x + width]
        blocks_x = 2
        blocks_y = 2
        block_width = width // blocks_x
        block_height = height // blocks_y
        this_block_histogram = self.calculate_blocks_histogram(this_valid_region, blocks_x, blocks_y, block_width,
                                                               block_height)
        if width == self.FRAME_WIDTH:
            # use cache to speed up
            previous_block_histogram = self.previous_histogram1
            self.previous_histogram1 = this_block_histogram
        else:
            previous_block_histogram = self.calculate_blocks_histogram(previous_valid_region, blocks_x, blocks_y,
                                                                       block_width, block_height)
        diff_arr = util.np_matrix_diff(this_block_histogram, previous_block_histogram)
        max_index = np.argmax(diff_arr)
        max_var = diff_arr[max_index]
        if max_var < self.REGION_VARIANCE_THRESHOLD:
            return None
        new_index_x, new_index_y = util.find_2d_index(max_index, blocks_x)
        new_start_x = start_x + new_index_x * block_width
        new_start_y = start_y + new_index_y * block_height
        valid_start_x = self.restrict_edge_start_x(new_start_x)
        valid_start_y = self.restrict_edge_start_y(new_start_y)
        new_block = Block(valid_start_x, valid_start_y, v=max_var)
        # print 'find_most_variable_block_division used time:{0}'.format(time.time() - start)
        if width > focus_width:
            return self.find_most_variable_block_division(this_full_image, valid_start_x, valid_start_y, width // 2,
                                                          height // 2, focus_width, focus_height)
        else:
            return new_block

    @util.timeit
    def update_degrees_rank(self, degrees):
        self.favor.update(USED_DEGREES, degrees)

    @util.timeit
    def get_degrees(self):
        used_degrees = None
        ri = random.randint(0, 9) - 1
        if ri >= 0:
            used_degrees = self.favor.top(USED_DEGREES, ri)

        if used_degrees is None:
            degrees = random.randint(1, self.MAX_DEGREES)
            return degrees
        else:
            return used_degrees.key

    @util.timeit
    def update_speed_rank(self, speed):
        self.favor.update(USED_SPEED, speed)

    @util.timeit
    def get_speed(self):
        used_speed = None
        ri = random.randint(0, 9) - 1
        if ri >= 0:
            used_speed = self.favor.top(USED_SPEED, ri)

        if used_speed is None:
            speed = random.randint(1, self.MAX_SPEED)
            return speed
        else:
            return used_speed.key

    @util.timeit
    def update_used_channel(self, channel):
        self.favor.update(USED_CHANNEL, channel)

    @util.timeit
    def get_channel(self):
        used_channel = None
        ri = random.randint(0, 9) - 1
        if ri >= 0:
            used_channel = self.favor.top(USED_CHANNEL, ri)

        if used_channel is None:
            ri = random.randint(1, 3)
            channel = 'y'
            if ri == 1:
                channel = 'u'
            elif ri == 2:
                channel = 'v'
            return channel
        else:
            return used_channel.key

    @util.timeit
    def get_duration(self):
        return random.randint(1, self.MAX_DURATION) / 10.0

    @util.timeit
    def search_feature(self, block):
        channel = self.get_channel()
        img = self.get_region(block)
        kernel = self.get_kernel()
        channel_img = get_channel_img(img, channel)
        data_map = {channel: self.get_data_map(channel_img)}
        feature = filter_feature(FeaturePack(kernel=kernel, channel=channel, data=data_map))
        feature.kernel = kernel
        feature.channel = channel
        return feature

    @util.timeit
    def dig(self):
        ri = random.randint(0, 2)
        if ri == 0:
            self.random_move_aside()
        elif ri == 1:
            self.random_zoom(self.ZOOM_IN)
        elif ri == 2:
            self.random_zoom(self.ZOOM_OUT)

    @util.timeit
    def try_move_aside(self, move_direction):
        new_block = copy.deepcopy(self.current_block)
        if move_direction is self.MOVE_UP:
            new_block.y = new_block.y - self.current_block.h
        elif move_direction is self.MOVE_DOWN:
            new_block.y = new_block.y + self.current_block.h
        elif move_direction is self.MOVE_LEFT:
            new_block.x = new_block.x - self.current_block.w
        elif move_direction is self.MOVE_RIGHT:
            new_block.x = new_block.x + self.current_block.w
        if not self.verify_block(new_block):
            return None
        return new_block

    @util.timeit
    def random_move_aside(self):
        move_direction = self.random_direction_straight()
        new_block = self.try_move_aside(move_direction)
        if new_block is None:
            return None
        feature_data = self.search_feature(new_block)
        if feature_data is None:
            return None
        self.current_block = new_block
        degrees = move_direction
        speed = -1
        duration = 0
        self.put_vision_move_memory(degrees, speed, duration)

    @util.timeit
    def put_vision_move_memory(self, degrees, speed, duration):
        q = Memory(MemoryType.REAL, real_type=RealType.VISION_FOCUS_MOVE, degrees=degrees, speed=speed,
                   duration=duration)
        m = self.brain.put_memory(q)
        self.brain.compose_memory([m], MemoryType.SLICE, real_type=RealType.VISION_FOCUS_MOVE)

    @util.timeit
    def explore(self):
        # large random number to reduce the possibility
        ri = random.randint(0, 40)
        if ri == 0:
            return self.random_move_away()
        elif ri == 1:
            return self.random_zoom()

    @util.timeit
    def random_move_away(self):
        # random move, explore the world
        degrees = self.get_degrees()
        self.update_degrees_rank(degrees)
        # most frequent speed
        speed = self.get_speed()
        self.update_speed_rank(speed)
        # 0.1-0.5s
        duration = self.get_duration()
        self.set_movement_relative(degrees, speed, duration)

    @util.timeit
    def random_direction_straight(self):
        ri = random.randint(0, 3)
        if ri == 0:
            return self.MOVE_UP
        elif ri == 1:
            return self.MOVE_DOWN
        elif ri == 2:
            return self.MOVE_LEFT
        else:
            return self.MOVE_RIGHT

    @util.timeit
    def random_direction_angle(self):
        ri = random.randint(0, 3)
        if ri == 0:
            return self.ZOOM_LEFT_TOP
        elif ri == 1:
            return self.ZOOM_RIGHT_TOP
        elif ri == 2:
            return self.ZOOM_LEFT_BOTTOM
        else:
            return self.ZOOM_RIGHT_BOTTOM

    @util.timeit
    def random_zoom(self, zoom_type=None):
        if zoom_type is None:
            ri = random.randint(0, 1)
            if ri == 0:
                zoom_type = self.ZOOM_IN
            else:
                zoom_type = self.ZOOM_OUT
        zoom_direction = self.random_direction_angle()
        if zoom_type is self.ZOOM_IN:
            new_block = self.try_zoom_in(zoom_direction)
        else:
            new_block = self.try_zoom_out(zoom_direction)
        if new_block is None:
            return None
        feature_data = self.search_feature(new_block)
        if feature_data is None:
            return None
        self.current_block = new_block
        self.put_vision_zoom_memory(zoom_type, zoom_direction)

    @util.timeit
    def put_vision_zoom_memory(self, zoom_type, zoom_direction):
        q = Memory(MemoryType.REAL, real_type=memory.RealType.VISION_FOCUS_ZOOM, zoom_direction=zoom_direction,
                   zoom_type=zoom_type)
        m = self.brain.put_memory(q)
        self.brain.compose_memory([m], MemoryType.SLICE, real_type=RealType.VISION_FOCUS_ZOOM)

    @util.timeit
    def try_zoom_in(self, zoom_direction):
        temp_index = self.current_block.ri - 1
        if temp_index < 0:
            return None
        new_block = copy.deepcopy(self.current_block)
        new_block.ri = temp_index
        new_block.w = self.ROI_ARR[temp_index]
        new_block.h = self.ROI_ARR[temp_index]
        if zoom_direction is self.ZOOM_RIGHT_TOP:
            new_block.x = new_block.x + new_block.w
        elif zoom_direction is self.ZOOM_LEFT_BOTTOM:
            new_block.y = new_block.y + new_block.h
        elif zoom_direction is self.ZOOM_RIGHT_BOTTOM:
            new_block.x = new_block.x + new_block.w
            new_block.y = new_block.y + new_block.h
        return new_block

    @util.timeit
    def try_zoom_out(self, zoom_direction):
        temp_index = self.current_block.ri + 1
        if temp_index > (len(self.ROI_ARR) - 1):
            return None
        new_block = copy.deepcopy(self.current_block)
        new_block.ri = temp_index
        new_block.w = self.ROI_ARR[temp_index]
        new_block.h = self.ROI_ARR[temp_index]
        if zoom_direction is self.ZOOM_LEFT_TOP:
            new_block.x = new_block.x - self.current_block.w
            new_block.y = new_block.y - self.current_block.h
        elif zoom_direction is self.ZOOM_RIGHT_TOP:
            new_block.y = new_block.y - self.current_block.h
        elif zoom_direction is self.ZOOM_LEFT_BOTTOM:
            new_block.x = new_block.x - self.current_block.w
        if not self.verify_block(new_block):
            return None
        return new_block

    @util.timeit
    def verify_block(self, block):
        if block.x < 0:
            return False
        if block.y < 0:
            return False
        if block.x + block.w > self.FRAME_WIDTH:
            return False
        if block.y + block.h > self.FRAME_HEIGHT:
            return False
        return True

    @util.timeit
    def get_region(self, block):
        roi_image = self.grab(block.y, block.x,
                              block.w, block.h)
        cv_img = cv2.cvtColor(np.array(roi_image), cv2.COLOR_RGB2BGR)
        img = cv2.resize(cv_img, (self.FEATURE_INPUT_SIZE, self.FEATURE_INPUT_SIZE))
        return img

    @util.timeit
    def set_movement_absolute(self, new_block, duration):
        degrees = self.calculate_degrees(new_block)
        length = math.hypot(new_block.y - self.current_block.y,
                            new_block.x - self.current_block.x)
        speed = length / duration / ACTUAL_SPEED_TIMES
        self.set_movement_relative(degrees, speed, duration)

    @util.timeit
    def set_movement_relative(self, degrees, speed, duration):
        self.current_action = {constants.DEGREES: degrees, constants.SPEED: speed, constants.MOVE_DURATION: duration,
                               self.LAST_MOVE_TIME: time.time(), self.STATUS: self.IN_PROGRESS}
        self.put_vision_move_memory(degrees, int(speed), duration)

    @util.timeit
    def restrict_edge_start_x(self, new_start_x):
        actual_start_x = new_start_x
        if new_start_x < 0:
            actual_start_x = 0
        if new_start_x + self.current_block.w > self.FRAME_WIDTH:
            actual_start_x = self.FRAME_WIDTH - self.current_block.w
        return int(round(actual_start_x))

    @util.timeit
    def restrict_edge_start_y(self, new_start_y):
        actual_start_y = new_start_y
        if new_start_y < 0:
            actual_start_y = 0
        if new_start_y + self.current_block.h > self.FRAME_HEIGHT:
            actual_start_y = self.FRAME_HEIGHT - self.current_block.h
        return int(round(actual_start_y))

    @util.timeit
    def calculate_degrees(self, new_block):
        radians = math.atan2(new_block.y - self.current_block.y,
                             new_block.x - self.current_block.x)
        degrees = math.degrees(radians)
        return int(round(degrees / float(ACTUAL_DEGREES_TIMES)))

    @util.timeit
    def try_move_away(self, elapse, degrees, speed):
        # actual degrees is 10 times
        actual_degrees = degrees * ACTUAL_DEGREES_TIMES
        # actual speed is 50 times
        actual_speed = speed * ACTUAL_SPEED_TIMES
        new_start_y = self.current_block.y + math.sin(math.radians(actual_degrees)) * elapse * actual_speed
        new_start_x = self.current_block.x + math.cos(math.radians(actual_degrees)) * elapse * actual_speed
        new_block = copy.deepcopy(self.current_block)
        new_block.x = int(round(new_start_x))
        new_block.y = int(round(new_start_y))
        if not self.verify_block(new_block):
            return None
        return new_block

    @util.timeit
    def calculate_move_action(self, action):
        elapse = time.time() - action[self.LAST_MOVE_TIME]
        duration = action[constants.MOVE_DURATION]
        degrees = action[constants.DEGREES]
        speed = action[constants.SPEED]
        if elapse >= duration:
            # if process slow, destination will be quite different
            elapse = duration
            action.update({self.STATUS: self.COMPLETED})
        new_block = self.try_move_away(elapse, degrees, speed)
        if new_block:
            self.current_block = new_block
            action[self.LAST_MOVE_TIME] = time.time()
            action[constants.MOVE_DURATION] = duration - elapse
        else:
            action.update({self.STATUS: self.COMPLETED})

    # deprecated, low performance
    @util.timeit
    def sum_blocks_histogram(self, cells_histogram):
        blocks_histogram = []
        times = self.current_block.w // self.ROI_ARR[0]
        blocks_x = self.FRAME_WIDTH // self.current_block.w
        blocks_y = self.FRAME_HEIGHT // self.current_block.h
        for j in range(0, blocks_y):
            for i in range(0, blocks_x):
                hist = None
                for h in range(0, times):
                    for w in range(0, times):
                        index = (j * times + h) * times * blocks_x + i * times + w
                        temp = cells_histogram[index]
                        if hist is None:
                            hist = temp
                        else:
                            hist = hist + temp
                blocks_histogram.append(hist)
        return blocks_histogram

    @util.timeit
    def calculate_blocks_histogram(self, full_image, blocks_x: int, blocks_y: int, block_width: int, block_height: int):
        data_inputs = []
        gray_image = cv2.cvtColor(full_image, cv2.COLOR_BGR2GRAY)  # use gray to save process time
        for j in range(0, blocks_y):
            for i in range(0, blocks_x):
                ret = gray_image[j * block_height:(j + 1) * block_height, i * block_width:(i + 1) * block_width]
                data_inputs.append(ret)
        run_results = self.pool.imap(calculate_histogram, data_inputs)
        blocks_histogram = list(run_results)
        return blocks_histogram

    @util.timeit
    def reproduce_movement(self, m: Memory):
        # print(f'reproduce_movement {m}')
        degrees = m.degrees
        speed = m.speed
        duration = m.duration
        if duration == 0:
            new_block = self.try_move_aside(degrees)
            if not new_block:
                return None
            self.current_block = new_block
        else:
            new_block = self.try_move_away(duration, degrees, speed)
            if not new_block:
                return None
            self.current_action = {constants.DEGREES: degrees, constants.SPEED: speed,
                                   constants.MOVE_DURATION: duration,
                                   self.LAST_MOVE_TIME: time.time(), self.STATUS: self.IN_PROGRESS}
        m.matched()
        m.post_matched()

    @util.timeit
    def reproduce_zoom(self, m: Memory):
        zoom_type = m.zoom_type
        zoom_direction = m.zoom_direction
        if zoom_type is self.ZOOM_OUT:
            new_block = self.try_zoom_out(zoom_direction)
        else:
            new_block = self.try_zoom_in(zoom_direction)
        if new_block is None:
            return None
        self.current_block = new_block
        m.matched()
        m.post_matched()

    @util.timeit
    def grab(self, top, left, width, height):
        raise NotImplementedError("error message")

    @util.timeit
    def move_focus_to_mouse(self):
        mouse_x = int(self.mouse.position[0])
        mouse_y = int(self.mouse.position[1])
        new_start_x = mouse_x - self.current_block.w // 2
        new_start_y = mouse_y - self.current_block.h // 2
        new_block_x = self.restrict_edge_start_x(new_start_x)
        new_block_y = self.restrict_edge_start_y(new_start_y)
        new_block = Block(new_block_x, new_block_y)
        self.set_movement_absolute(new_block, 0.5)

    @util.timeit
    def calculate_vision_focus_state(self):
        this_focus_state = self.get_focus_state(self.current_block)
        if self.last_focus_state != this_focus_state:
            self.last_focus_state_time = time.time()
        self.last_focus_state = this_focus_state
        elapse = time.time() - self.last_focus_state_time
        if elapse <= self.PROCESS_STABLE_DURATION:
            self.focus_status = self.PROCESS_STATUS_NORMAL
        elif elapse > self.PROCESS_STABLE_DURATION and \
                self.focus_status is self.PROCESS_STATUS_NORMAL:
            self.focus_status = self.PROCESS_STATUS_DIGGING
        elif elapse > self.PROCESS_STABLE_DURATION * 2 and \
                self.focus_status is self.PROCESS_STATUS_DIGGING:
            self.focus_status = self.PROCESS_STATUS_EXPLORING

    @util.timeit
    def get_focus_state(self, block):
        list1 = [block.x, block.y, block.w, block.h]
        return util.list_to_str(list1)


@util.timeit
def get_channel_imgs(bgr):
    yuv = cv2.cvtColor(bgr, cv2.COLOR_BGR2YUV)
    return cv2.split(yuv)


@util.timeit
def get_channel_img(bgr, channel):
    y, u, v = get_channel_imgs(bgr)
    if channel == 'y':
        return y
    elif channel == 'u':
        return u
    elif channel == 'v':
        return v


@util.timeit
def get_feature_result(channel, kernel, feature_data):
    feature_data_str = util.list_to_str(feature_data)
    return channel + kernel + feature_data_str
