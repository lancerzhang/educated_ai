from pynput.mouse import Controller
import copy
import cv2
import logging
import math
import numpy as np
import random
import skimage.measure
import time
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


class Vision(object):
    FRAME_WIDTH = 0
    FRAME_HEIGHT = 0
    ROI_ARR = [32, 64, 128, 256]
    roi_index = 2
    ROI_INDEX_NAME = 'ROI_INDEX'
    START_X = 'sx'
    START_Y = 'sy'
    WIDTH = 'width'
    HEIGHT = 'height'
    HISTOGRAM_BINS = 27
    FEATURE_INPUT_SIZE = 12
    FEATURE_THRESHOLD = 20
    FEATURE_SIMILARITY_THRESHOLD = 0.2
    POOL_BLOCK_SIZE = 2  # after down-sampling, feature is 3x3
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
        center_x = self.FRAME_WIDTH // 2
        center_y = self.FRAME_HEIGHT // 2
        width = self.ROI_ARR[self.roi_index]
        half_width = width // 2
        self.current_block = {self.START_X: center_x - half_width, self.START_Y: center_y - half_width,
                              self.WIDTH: width, self.HEIGHT: width, self.ROI_INDEX_NAME: self.roi_index}
        self.vision_kernels = np.load(self.VISION_KERNEL_FILE)
        # fix error of Mac - Process finished with exit code 132 (interrupted by signal 4: SIGILL)
        if self.is_show is not 'n':
            cv2.namedWindow("frame", cv2.WND_PROP_FULLSCREEN)

    @util.timeit
    def process(self, status, key):
        old_focus_x = self.current_block[self.START_X] + self.current_block[self.WIDTH] // 2
        old_focus_y = self.current_block[self.START_Y] + self.current_block[self.HEIGHT] // 2
        if self.current_action[self.STATUS] == self.IN_PROGRESS:
            self.calculate_move_action(self.current_action)

        self.match_features()
        self.search_feature_memory()

        # when she's mature, below is the major way of focus move/zoom.
        self.reproduce_movements()
        self.reproduce_zooms()

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

        new_focus_x = self.current_block[self.START_X] + self.current_block[self.WIDTH] // 2
        new_focus_y = self.current_block[self.START_Y] + self.current_block[self.HEIGHT] // 2
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
        data_map = None
        data_map_y = None
        data_map_u = None
        data_map_v = None
        for m in feature_memories:
            channel = m.channel
            if channel == 'y':
                if data_map_y is None:
                    data_map_y = self.get_data_map(y)
                data_map = data_map_y
            elif channel == 'u':
                if data_map_u is None:
                    data_map_u = self.get_data_map(u)
                data_map = data_map_u
            elif channel == 'v':
                if data_map_v is None:
                    data_map_v = self.get_data_map(v)
                data_map = data_map_v
            self.match_feature(data_map, m)

    @util.timeit
    def reproduce_movements(self):
        feature_memories = self.brain.get_matching_real_memories(RealType.VISION_FOCUS_MOVE)
        for m in feature_memories:
            self.reproduce_movement(m)

    @util.timeit
    def reproduce_zooms(self):
        feature_memories = self.brain.get_matching_real_memories(RealType.VISION_FOCUS_ZOOM)
        for m in feature_memories:
            self.reproduce_zoom(m)

    @util.timeit
    def match_feature(self, data_map, m: Memory):
        feature = self.filter_feature(data_map, m.kernel, m.feature)
        if feature.similar:
            m.feature = feature.feature
            logger.debug(f'matched_feature {m.mid}')
            m.matched()
            self.update_used_channel(m.channel)
            self.update_used_kernel(m.kernel)

    # match the experience vision sense
    @util.timeit
    def filter_feature(self, data_map, kernel, data=None):
        feature = FeaturePack()
        kernel_arr = util.string_to_feature_matrix(kernel)
        cov = cv2.filter2D(data_map, -1, kernel_arr)
        # down-sampling once use max pool, size is 50% of origin
        new_feature_pool1 = skimage.measure.block_reduce(cov, (self.POOL_BLOCK_SIZE, self.POOL_BLOCK_SIZE), np.max)
        # down-sampling again use max pool, size is 25% of origin
        new_feature_pool2 = skimage.measure.block_reduce(new_feature_pool1,
                                                         (self.POOL_BLOCK_SIZE, self.POOL_BLOCK_SIZE), np.max)
        # reduce not obvious feature
        threshold_feature = np.where(new_feature_pool2 < self.FEATURE_THRESHOLD, 0, new_feature_pool2)
        sum_feature = threshold_feature.sum()
        if sum_feature == 0:
            return feature  # no any feature found
        if util.np_array_all_same(threshold_feature):
            return feature  # useless feature data
        standard_feature = util.standardize_feature(threshold_feature)
        new_feature = standard_feature.flatten().astype(int)
        if data is None:
            feature.feature = new_feature
        else:
            difference = util.np_array_diff(new_feature, data)
            if difference < self.FEATURE_SIMILARITY_THRESHOLD:
                feature.similar = True
                avg_feature = (data + new_feature) // 2
                feature.feature = avg_feature
            else:
                feature.feature = new_feature
        return feature

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
                                                       self.current_block[self.WIDTH], self.current_block[self.HEIGHT])
        if block is None:
            return None
        if block['v'] < self.REGION_VARIANCE_THRESHOLD:
            return None
        # move focus to variable region
        self.set_movement_absolute(block, duration)
        return True

    @util.timeit
    def find_most_variable_block(self, this_full_image):
        new_block = {}
        if self.previous_full_image is None:
            return None
        else:
            # logger.debug('compare channel img {0}'.format((self.previous_full_image == this_full_image).all()))
            blocks_x = self.FRAME_WIDTH // self.current_block[self.WIDTH]
            blocks_y = self.FRAME_HEIGHT // self.current_block[self.HEIGHT]
            block_width = self.current_block[self.WIDTH]
            block_height = self.current_block[self.HEIGHT]
            # this_cells_histogram = self.calculate_cells_histogram(this_full_image)
            # self.this_cells_histogram = this_cells_histogram  # save a copy
            # previous_block_histogram = self.sum_blocks_histogram(self.previous_cells_histogram)
            # this_block_histogram = self.sum_blocks_histogram(this_cells_histogram)
            previous_block_histogram = self.calculate_blocks_histogram(self.previous_full_image, blocks_x, blocks_y,
                                                                       block_width, block_height)
            this_block_histogram = self.calculate_blocks_histogram(this_full_image, blocks_x, blocks_y, block_width,
                                                                   block_height)

            # logger.debug('previous histogram array is {0}'.format(previous_block_histogram))
            # logger.debug('this histogram array is {0}'.format(this_block_histogram))
            diff_arr = util.np_matrix_diff(this_block_histogram, previous_block_histogram)
            max_index = np.argmax(diff_arr)
            max_var = diff_arr[max_index]
            if max_var < self.REGION_VARIANCE_THRESHOLD:
                return None
            # logger.debug('diff histogram array is {0}'.format(diff_arr))
            # logger.debug('max_var is {0}'.format(max_var))
            # np.save('pimg.npy', self.previous_full_image)
            # np.save('timg.npy', this_full_image)
            new_index_x, new_index_y = util.find_2d_index(max_index, blocks_x)
            new_start_x = new_index_x * self.current_block[self.WIDTH]
            new_start_y = new_index_y * self.current_block[self.HEIGHT]
            new_block[self.START_X] = self.restrict_edge_start_x(new_start_x)
            new_block[self.START_Y] = self.restrict_edge_start_y(new_start_y)
            new_block.update({'v': max_var})
        return new_block

    # reduce number of histogram call,it's time consuming
    @util.timeit
    def find_most_variable_block_division(self, this_full_image, start_x, start_y, width, height, focus_width,
                                          focus_height):
        # start = time.time()
        new_block = {}
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
        new_block[self.START_X] = valid_start_x
        new_block[self.START_Y] = valid_start_y
        new_block.update({'v': max_var})
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
        data_map = self.get_data_map(channel_img)
        feature = self.filter_feature(data_map, kernel)
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
            new_block[self.START_Y] = new_block[self.START_Y] - self.current_block[self.HEIGHT]
        elif move_direction is self.MOVE_DOWN:
            new_block[self.START_Y] = new_block[self.START_Y] + self.current_block[self.HEIGHT]
        elif move_direction is self.MOVE_LEFT:
            new_block[self.START_X] = new_block[self.START_X] - self.current_block[self.WIDTH]
        elif move_direction is self.MOVE_RIGHT:
            new_block[self.START_X] = new_block[self.START_X] + self.current_block[self.WIDTH]
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
        temp_index = self.current_block[self.ROI_INDEX_NAME] - 1
        if temp_index < 0:
            return None
        new_block = copy.deepcopy(self.current_block)
        new_block[self.ROI_INDEX_NAME] = temp_index
        new_block[self.WIDTH] = self.ROI_ARR[temp_index]
        new_block[self.HEIGHT] = self.ROI_ARR[temp_index]
        if zoom_direction is self.ZOOM_RIGHT_TOP:
            new_block[self.START_X] = new_block[self.START_X] + new_block[self.WIDTH]
        elif zoom_direction is self.ZOOM_LEFT_BOTTOM:
            new_block[self.START_Y] = new_block[self.START_Y] + new_block[self.HEIGHT]
        elif zoom_direction is self.ZOOM_RIGHT_BOTTOM:
            new_block[self.START_X] = new_block[self.START_X] + new_block[self.WIDTH]
            new_block[self.START_Y] = new_block[self.START_Y] + new_block[self.HEIGHT]
        return new_block

    @util.timeit
    def try_zoom_out(self, zoom_direction):
        temp_index = self.current_block[self.ROI_INDEX_NAME] + 1
        if temp_index > (len(self.ROI_ARR) - 1):
            return None
        new_block = copy.deepcopy(self.current_block)
        new_block[self.ROI_INDEX_NAME] = temp_index
        new_block[self.WIDTH] = self.ROI_ARR[temp_index]
        new_block[self.HEIGHT] = self.ROI_ARR[temp_index]
        if zoom_direction is self.ZOOM_LEFT_TOP:
            new_block[self.START_X] = new_block[self.START_X] - self.current_block[self.WIDTH]
            new_block[self.START_Y] = new_block[self.START_Y] - self.current_block[self.HEIGHT]
        elif zoom_direction is self.ZOOM_RIGHT_TOP:
            new_block[self.START_Y] = new_block[self.START_Y] - self.current_block[self.HEIGHT]
        elif zoom_direction is self.ZOOM_LEFT_BOTTOM:
            new_block[self.START_X] = new_block[self.START_X] - self.current_block[self.WIDTH]
        if not self.verify_block(new_block):
            return None
        return new_block

    @util.timeit
    def verify_block(self, block):
        if block[self.START_X] < 0:
            return False
        if block[self.START_Y] < 0:
            return False
        if block[self.START_X] + block[self.WIDTH] > self.FRAME_WIDTH:
            return False
        if block[self.START_Y] + block[self.HEIGHT] > self.FRAME_HEIGHT:
            return False
        return True

    @util.timeit
    def get_region(self, block):
        roi_image = self.grab(block[self.START_Y], block[self.START_X],
                              block[self.WIDTH], block[self.HEIGHT])
        cv_img = cv2.cvtColor(np.array(roi_image), cv2.COLOR_RGB2BGR)
        img = cv2.resize(cv_img, (self.FEATURE_INPUT_SIZE, self.FEATURE_INPUT_SIZE))
        return img

    @util.timeit
    def set_movement_absolute(self, new_block, duration):
        degrees = self.calculate_degrees(new_block)
        length = math.hypot(new_block[self.START_Y] - self.current_block[self.START_Y],
                            new_block[self.START_X] - self.current_block[self.START_X])
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
        if new_start_x + self.current_block[self.WIDTH] > self.FRAME_WIDTH:
            actual_start_x = self.FRAME_WIDTH - self.current_block[self.WIDTH]
        return int(round(actual_start_x))

    @util.timeit
    def restrict_edge_start_y(self, new_start_y):
        actual_start_y = new_start_y
        if new_start_y < 0:
            actual_start_y = 0
        if new_start_y + self.current_block[self.HEIGHT] > self.FRAME_HEIGHT:
            actual_start_y = self.FRAME_HEIGHT - self.current_block[self.HEIGHT]
        return int(round(actual_start_y))

    @util.timeit
    def calculate_degrees(self, new_block):
        radians = math.atan2(new_block[self.START_Y] - self.current_block[self.START_Y],
                             new_block[self.START_X] - self.current_block[self.START_X])
        degrees = math.degrees(radians)
        return int(round(degrees / float(ACTUAL_DEGREES_TIMES)))

    @util.timeit
    def try_move_away(self, elapse, degrees, speed):
        # actual degrees is 10 times
        actual_degrees = degrees * ACTUAL_DEGREES_TIMES
        # actual speed is 50 times
        actual_speed = speed * ACTUAL_SPEED_TIMES
        new_start_y = self.current_block[self.START_Y] + math.sin(math.radians(actual_degrees)) * elapse * actual_speed
        new_start_x = self.current_block[self.START_X] + math.cos(math.radians(actual_degrees)) * elapse * actual_speed
        new_block = copy.deepcopy(self.current_block)
        new_block[self.START_X] = int(round(new_start_x))
        new_block[self.START_Y] = int(round(new_start_y))
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
    def calculate_cells_histogram(self, full_image):
        cells_histogram = []
        width = self.ROI_ARR[0]
        height = self.ROI_ARR[0]
        # b, g, r = cv2.split(full_image)
        gray_image = cv2.cvtColor(full_image, cv2.COLOR_BGR2GRAY)  # use gray to save process time
        cells_x = self.FRAME_WIDTH // width
        cells_y = self.FRAME_HEIGHT // height
        for j in range(0, cells_y):
            for i in range(0, cells_x):
                # ret_b = b[j * height:(j + 1) * height, i * width:(i + 1) * width]
                # ret_g = g[j * height:(j + 1) * height, i * width:(i + 1) * width]
                # ret_r = r[j * height:(j + 1) * height, i * width:(i + 1) * width]
                # ret = np.concatenate([ret_b, ret_g, ret_r])
                ret = gray_image[j * height:(j + 1) * height, i * width:(i + 1) * width]
                hist_np, bins = np.histogram(ret.ravel(), bins=self.HISTOGRAM_BINS, range=[0, 256])
                cells_histogram.append(hist_np)
        return cells_histogram

    # deprecated, low performance
    @util.timeit
    def sum_blocks_histogram(self, cells_histogram):
        blocks_histogram = []
        times = self.current_block[self.WIDTH] // self.ROI_ARR[0]
        blocks_x = self.FRAME_WIDTH // self.current_block[self.WIDTH]
        blocks_y = self.FRAME_HEIGHT // self.current_block[self.HEIGHT]
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
    def calculate_blocks_histogram(self, full_image, blocks_x, blocks_y, block_width, block_height):
        blocks_histogram = []
        # b, g, r = cv2.split(full_image)
        gray_image = cv2.cvtColor(full_image, cv2.COLOR_BGR2GRAY)  # use gray to save process time
        for j in range(0, blocks_y):
            for i in range(0, blocks_x):
                # ret_b = b[j * block_height:(j + 1) * block_height, i * block_width:(i + 1) * block_width]
                # ret_g = g[j * block_height:(j + 1) * block_height, i * block_width:(i + 1) * block_width]
                # ret_r = r[j * block_height:(j + 1) * block_height, i * block_width:(i + 1) * block_width]
                # ret = np.concatenate([ret_b, ret_g, ret_r])
                ret = gray_image[j * block_height:(j + 1) * block_height, i * block_width:(i + 1) * block_width]
                hist_np, bins = np.histogram(ret.ravel(), bins=self.HISTOGRAM_BINS, range=[0, 256])
                blocks_histogram.append(hist_np)
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

    @util.timeit
    def grab(self, top, left, width, height):
        raise NotImplementedError("error message")

    @util.timeit
    def move_focus_to_mouse(self):
        new_block = {}
        mouse_x = int(self.mouse.position[0])
        mouse_y = int(self.mouse.position[1])
        new_start_x = mouse_x - self.current_block[self.WIDTH] // 2
        new_start_y = mouse_y - self.current_block[self.HEIGHT] // 2
        new_block[self.START_X] = self.restrict_edge_start_x(new_start_x)
        new_block[self.START_Y] = self.restrict_edge_start_y(new_start_y)
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
        list1 = [block[self.START_X], block[self.START_Y], block[self.WIDTH], block[self.HEIGHT]]
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
