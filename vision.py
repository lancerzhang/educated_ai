from pynput.mouse import Controller
import constants
import copy
import cv2
import logging
import math
import memory
import numpy as np
import random
import skimage.measure
import time
import util

logger = logging.getLogger('Vision')
logger.setLevel(logging.INFO)


class Vision(object):
    SCREEN_WIDTH = 0
    SCREEN_HEIGHT = 0
    ROI_ARR = [12, 36, 72, 144, 288]
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
    MAX_DURATION = 5  # actual is 10%

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
    USED_SPEED_FILE = 'data/vus.npy'
    USED_DEGREES_FILE = 'data/vud.npy'
    USED_KERNEL_FILE = 'data/vuk.npy'
    USED_CHANNEL_FILE = 'data/vuc.npy'
    MEMORY_INDEX_FILE = 'data/vmi.npy'
    VISION_KERNEL_FILE = 'kernels.npy'
    previous_energies = []
    previous_full_image = None

    FEATURE_DATA = {constants.KERNEL: [], constants.FEATURE: [], constants.SIMILAR: False}
    current_action = {STATUS: COMPLETED}

    def __init__(self, ds):
        self.mouse = Controller()
        self.data_service = ds
        center_x = self.SCREEN_WIDTH / 2
        center_y = self.SCREEN_HEIGHT / 2
        width = self.ROI_ARR[self.roi_index]
        half_width = width / 2
        self.current_block = {self.START_X: center_x - half_width, self.START_Y: center_y - half_width,
                              self.WIDTH: width, self.HEIGHT: width}

        try:
            self.memory_indexes = np.load(self.MEMORY_INDEX_FILE)
        except IOError:
            self.memory_indexes = np.array([])

        try:
            self.used_kernel_rank = np.load(self.USED_KERNEL_FILE)
        except IOError:
            self.used_kernel_rank = np.array([])

        self.vision_kernels = np.load(self.VISION_KERNEL_FILE)

        try:
            self.used_speed_rank = np.load(self.USED_SPEED_FILE)
        except IOError:
            self.used_speed_rank = np.array([])

        try:
            self.used_degrees_rank = np.load(self.USED_DEGREES_FILE)
        except IOError:
            self.used_degrees_rank = np.array([])

        try:
            self.used_channel_rank = np.load(self.USED_CHANNEL_FILE)
        except IOError:
            self.used_channel_rank = np.array([])

    def save_files(self):
        np.save(self.MEMORY_INDEX_FILE, self.memory_indexes)
        np.save(self.USED_KERNEL_FILE, self.used_kernel_rank[0:100])
        np.save(self.USED_SPEED_FILE, self.used_speed_rank)
        np.save(self.USED_DEGREES_FILE, self.used_degrees_rank)
        np.save(self.USED_CHANNEL_FILE, self.used_channel_rank)

    def process(self, working_memories, sequential_time_memories, work_status, key):
        start = time.time()
        if self.current_action[self.STATUS] is self.IN_PROGRESS:
            self.calculate_move_action(self.current_action)

        slice_feature_memories = [mem for mem in working_memories if
                                  constants.MEMORY_DURATION in mem and
                                  mem[constants.MEMORY_DURATION] is constants.SLICE_MEMORY and
                                  mem[constants.STATUS] is constants.MATCHING and
                                  mem[constants.PHYSICAL_MEMORY_TYPE] is constants.VISION_FEATURE]

        matched_feature_memories = self.match_features(slice_feature_memories, working_memories,
                                                       sequential_time_memories)

        new_slice_memory = None
        new_feature_memory = self.search_feature_memory(self.current_block)
        if len(matched_feature_memories) > 0:
            matched_feature_memories_ids = [x[constants.MID] for x in matched_feature_memories]
            if new_feature_memory is not None and new_feature_memory[constants.MID] not in matched_feature_memories_ids:
                matched_feature_memories.append(new_feature_memory)
            new_slice_memory = memory.add_collection_memory(constants.SLICE_MEMORY, matched_feature_memories)
        elif new_feature_memory is not None:
            new_slice_memories = memory.get_live_sub_memories(new_feature_memory, constants.PARENT_MEM)
            new_matched_feature_memories = self.match_features(new_slice_memories, working_memories,
                                                               sequential_time_memories)
            new_matched_feature_memories_ids = [x[constants.MID] for x in new_matched_feature_memories]
            if new_feature_memory[constants.MID] not in new_matched_feature_memories_ids:
                new_matched_feature_memories.append(new_feature_memory)
            new_slice_memory = memory.add_collection_memory(constants.SLICE_MEMORY, new_matched_feature_memories)
        add_new_slice_memory(new_slice_memory, sequential_time_memories, working_memories)

        # when she's mature, below is the major way of focus move/zoom.
        slice_movement_memories = [mem for mem in working_memories if
                                   constants.MEMORY_DURATION in mem and
                                   mem[constants.MEMORY_DURATION] is constants.SLICE_MEMORY and
                                   mem[constants.STATUS] is constants.MATCHING and
                                   mem[constants.PHYSICAL_MEMORY_TYPE] is constants.VISION_FOCUS_MOVE]

        if self.current_action[self.STATUS] is not self.IN_PROGRESS:
            if len(slice_movement_memories) > 0:
                new_slice_memory = self.match_movement_memories(slice_movement_memories)
                add_new_slice_memory(new_slice_memory, sequential_time_memories, working_memories)

        slice_zoom_memories = [mem for mem in working_memories if
                               constants.MEMORY_DURATION in mem and
                               mem[constants.MEMORY_DURATION] is constants.SLICE_MEMORY and
                               mem[constants.STATUS] is constants.MATCHING and
                               mem[constants.PHYSICAL_MEMORY_TYPE] is constants.VISION_FOCUS_ZOOM]

        if len(slice_zoom_memories) > 0:
            new_slice_memory = self.match_zoom_memories(slice_zoom_memories)
            add_new_slice_memory(new_slice_memory, sequential_time_memories, working_memories)

        # when she's not mature, need to guide her.
        this_full_image = self.grab(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        if self.current_action[self.STATUS] is not self.IN_PROGRESS:
            logger.debug('reward is {0}'.format(work_status[constants.REWARD]))
            if key is constants.KEY_ALT or key is constants.KEY_CTRL:
                # the 1st and most efficient way is to set focus directly, and reward it
                new_slice_memory = self.move_focus_to_mouse()
            elif work_status[constants.REWARD]:
                # stay more time on reward region.
                new_slice_memory = self.dig()
            elif not work_status[constants.REWARD]:
                # move out from current reward region.
                new_slice_memory_aware = self.aware(this_full_image)
                if new_slice_memory_aware:
                    # affected by environment vision change.
                    new_slice_memory = new_slice_memory_aware
                else:
                    if not work_status[constants.BUSY][constants.MEDIUM_DURATION]:
                        # if environment not change, random do some change.
                        new_slice_memory = self.explore()
        add_new_slice_memory(new_slice_memory, sequential_time_memories, working_memories)
        self.previous_full_image = this_full_image

        if not work_status[constants.BUSY][constants.LONG_DURATION]:
            self.save_files()
        logger.debug('process used time:{0}'.format(time.time() - start))

    def match_features(self, slice_memories, working_memories, sequential_time_memories):
        distinct_feature_memories = []
        slice_memory_children = {}
        memory.search_sub_memories(slice_memories, distinct_feature_memories, slice_memory_children)
        for fmm in distinct_feature_memories:
            self.match_feature(fmm)
        matched_feature_memories = memory.verify_slice_memory_match_result(slice_memories, slice_memory_children,
                                                                           working_memories, sequential_time_memories)
        return matched_feature_memories

    def match_feature(self, fmm):
        channel = fmm[constants.CHANNEL]
        kernel = fmm[constants.KERNEL]
        feature = fmm[constants.FEATURE]
        img = self.get_region(self.current_block)
        channel_img = get_channel_img(img, channel)
        fmm.update({constants.STATUS: constants.MATCHING})
        data = self.filter_feature(channel_img, kernel, np.array(feature))
        if data is None:
            return False  # not similar
        if data[constants.SIMILAR]:
            # recall memory and update feature to average
            memory.recall_feature_memory(fmm, data[constants.FEATURE])
            fmm[constants.STATUS] = constants.MATCHED
            self.update_channel_rank(channel)
            self.update_kernel_rank(kernel)
        return data[constants.SIMILAR]

    # match the experience vision sense
    def filter_feature(self, data, kernel, feature=None):
        feature_data = copy.deepcopy(self.FEATURE_DATA)
        feature_data[constants.KERNEL] = kernel
        data_map = cv2.resize(data, (self.FEATURE_INPUT_SIZE, self.FEATURE_INPUT_SIZE))
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
            return None  # no any feature found
        if util.np_array_all_same(threshold_feature):
            return None  # useless feature data
        standard_feature = util.standardize_feature(threshold_feature)
        new_feature = standard_feature.flatten().astype(int)
        if feature is None:
            feature_data[constants.FEATURE] = new_feature
        else:
            difference = util.np_array_diff(new_feature, feature)
            if difference < self.FEATURE_SIMILARITY_THRESHOLD:
                feature_data[constants.SIMILAR] = True
                avg_feature = (feature + new_feature) / 2
                feature_data[constants.FEATURE] = avg_feature
            else:
                feature_data[constants.FEATURE] = new_feature
        return feature_data

    # get a frequent use kernel or a random kernel by certain possibility
    def get_kernel(self):
        used_kernel = util.get_high_rank(self.used_kernel_rank)
        if used_kernel is None:
            shape = self.vision_kernels.shape
            index = random.randint(0, shape[0] - 1)
            kernel = self.vision_kernels[index]
            return kernel
        else:
            return used_kernel[constants.KERNEL]

    def update_kernel_rank(self, kernel):
        self.used_kernel_rank = util.update_rank_list(constants.KERNEL, kernel, self.used_kernel_rank)

    # try to search more detail
    def search_feature_memory(self, block):
        feature_data = self.search_feature(block)
        if feature_data is None:
            return None
        channel = feature_data[constants.CHANNEL]
        kernel = feature_data[constants.KERNEL]
        feature = feature_data[constants.FEATURE]
        mem = self.find_feature_memory(channel, kernel, feature)
        if mem is None:
            mem = memory.add_vision_feature_memory(constants.VISION_FEATURE, channel, kernel, feature)
            self.update_memory_indexes(channel, kernel, mem[constants.MID])
        self.update_kernel_rank(kernel)
        self.update_channel_rank(channel)
        return mem

    # find memory by kernel using index
    def find_feature_memory(self, channel, kernel, feature1):
        element = next(
            (x for x in self.memory_indexes if x[constants.KERNEL] == kernel and x[constants.CHANNEL] == channel),
            None)
        if element is not None:
            memory_ids = element[constants.MEMORIES]
            live_memories = memory.get_live_memories(memory_ids)
            if live_memories is not None:
                for mem in live_memories:
                    feature2 = mem[constants.FEATURE]
                    difference = util.np_array_diff(feature1, np.array(feature2))
                    if difference < self.FEATURE_SIMILARITY_THRESHOLD:
                        return mem
        return None

    def update_memory_indexes(self, channel, kernel, mid):
        element = next(
            (x for x in self.memory_indexes if x[constants.KERNEL] == kernel and x[constants.CHANNEL] == channel),
            None)
        if element is None:
            new_kernel = {constants.CHANNEL: channel, constants.KERNEL: kernel, constants.MEMORIES: [mid]}
            self.memory_indexes = np.append(self.memory_indexes, new_kernel)
        else:
            memory_ids = element[constants.MEMORIES]
            if mid not in memory_ids:
                memory_ids.append(mid)

    def aware(self, image):
        logger.info('aware')
        start = time.time()
        duration = self.get_duration()
        block = self.find_most_variable_block(image)
        logger.debug('variable block is {0}'.format(block))
        logger.debug('current block is {0}'.format(self.current_block))
        if block is None:
            return None
        if block['v'] < self.REGION_VARIANCE_THRESHOLD:
            return None
        logger.debug('aware used time:{0}'.format(time.time() - start))
        # move focus to variable region
        return self.set_movement_absolute(block, duration)

    def find_most_variable_block(self, this_full_image):
        start = time.time()
        new_block = {}
        if self.previous_full_image is None:
            return None
        else:
            # logger.debug('compare channel img {0}'.format((self.previous_full_image == this_full_image).all()))
            blocks_x = self.SCREEN_WIDTH / self.current_block[self.WIDTH]
            blocks_y = self.SCREEN_HEIGHT / self.current_block[self.HEIGHT]
            previous_block_histogram = self.calculate_blocks_histogram(self.previous_full_image, blocks_x, blocks_y)
            this_block_histogram = self.calculate_blocks_histogram(this_full_image, blocks_x, blocks_y)
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
        logger.debug('find_most_variable_region used time:{0}'.format(time.time() - start))
        return new_block

    def update_degrees_rank(self, degrees):
        self.used_degrees_rank = util.update_rank_list(constants.DEGREES, degrees, self.used_degrees_rank)

    def get_degrees(self):
        used_degrees = util.get_high_rank(self.used_degrees_rank)
        if used_degrees is None:
            degrees = random.randint(1, self.MAX_DEGREES)
            return degrees
        else:
            return used_degrees[constants.DEGREES]

    def update_speed_rank(self, speed):
        self.used_speed_rank = util.update_rank_list(constants.SPEED, speed, self.used_speed_rank)

    def get_speed(self):
        used_speed = util.get_high_rank(self.used_speed_rank)
        if used_speed is None:
            speed = random.randint(1, self.MAX_SPEED)
            return speed
        else:
            return used_speed[constants.SPEED]

    def update_channel_rank(self, channel):
        self.used_channel_rank = util.update_rank_list(constants.CHANNEL, channel, self.used_channel_rank)

    def get_channel(self):
        used_channel = util.get_high_rank(self.used_channel_rank)
        if used_channel is None:
            ri = random.randint(1, 3)
            channel = 'y'
            if ri == 1:
                channel = 'u'
            elif ri == 2:
                channel = 'v'
            return channel
        else:
            return used_channel[constants.CHANNEL]

    def get_duration(self):
        return random.randint(1, self.MAX_DURATION) / 10.0

    def search_feature(self, block):
        channel = self.get_channel()
        img = self.get_region(block)
        kernel = self.get_kernel()
        channel_img = get_channel_img(img, channel)
        feature_data = self.filter_feature(channel_img, kernel)
        if feature_data:
            feature_data[constants.CHANNEL] = channel
        return feature_data

    def dig(self):
        logger.debug('dig')
        ri = random.randint(0, 2)
        if ri == 0:
            return self.random_move_aside()
        elif ri == 1:
            return self.random_zoom(self.ZOOM_IN)
        elif ri == 2:
            return self.random_zoom(self.ZOOM_OUT)

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

    def random_move_aside(self):
        logger.debug('random_move_aside')
        move_direction = self.random_direction_straight()
        new_block = self.try_move_aside(move_direction)
        if new_block is None:
            return None
        logger.debug('new_block is {0}'.format(new_block))
        feature_data = self.search_feature(new_block)
        logger.debug('feature_data is {0}'.format(feature_data))
        if feature_data is None:
            return None
        self.current_block = new_block
        degrees = move_direction
        speed = -1
        duration = 0
        action = {constants.DEGREES: degrees, constants.SPEED: speed, constants.DURATION: duration,
                  constants.PHYSICAL_MEMORY_TYPE: constants.VISION_FOCUS_MOVE}
        memories = self.data_service.get_vision_move_memory(degrees, speed, duration)
        if memories is None or len(memories) == 0:
            action_memory = memory.add_physical_memory(action)
        else:
            mem = memories[0]
            memory.recall_memory(mem)
            action_memory = mem
        slice_memory = memory.add_collection_memory(constants.SLICE_MEMORY, [action_memory])
        return slice_memory

    def explore(self):
        logger.debug('explore')
        # large random number to reduce the possibility
        ri = random.randint(0, 40)
        if ri == 0:
            return self.random_move_away()
        elif ri == 1:
            return self.random_zoom()

    def random_move_away(self):
        logger.debug('random_move_away')
        # random move, explore the world
        degrees = self.get_degrees()
        self.update_degrees_rank(degrees)
        # most frequent speed
        speed = self.get_speed()
        self.update_speed_rank(speed)
        # 0.1-0.5s
        duration = self.get_duration()
        slice_memory = self.set_movement_relative(degrees, speed, duration)
        return slice_memory

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

    def random_zoom(self, zoom_type=None):
        logger.debug('random_zoom')
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
        logger.debug('new_block is {0}'.format(new_block))
        feature_data = self.search_feature(new_block)
        logger.debug('feature_data is {0}'.format(feature_data))
        if feature_data is None:
            return None
        self.current_block = new_block
        action = {constants.PHYSICAL_MEMORY_TYPE: constants.VISION_FOCUS_ZOOM, constants.ZOOM_TYPE: zoom_type,
                  constants.ZOOM_DIRECTION: zoom_direction}
        memories = self.data_service.get_vision_zoom_memory(zoom_type, zoom_direction)
        if memories is None or len(memories) == 0:
            action_memory = memory.add_physical_memory(action)
        else:
            mem = memories[0]
            memory.recall_memory(mem)
            action_memory = mem
        slice_memory = memory.add_collection_memory(constants.SLICE_MEMORY, [action_memory])
        return slice_memory

    def try_zoom_in(self, zoom_direction):
        temp_index = self.roi_index - 1
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

    def try_zoom_out(self, zoom_direction):
        temp_index = self.roi_index + 1
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

    def verify_block(self, block):
        if block[self.START_X] < 0:
            return False
        if block[self.START_Y] < 0:
            return False
        if block[self.START_X] + block[self.WIDTH] > self.SCREEN_WIDTH:
            return False
        if block[self.START_Y] + block[self.HEIGHT] > self.SCREEN_HEIGHT:
            return False
        return True

    def get_region(self, block):
        roi_image = self.grab(block[self.START_Y], block[self.START_X],
                              block[self.WIDTH], block[self.HEIGHT])
        cv_img = cv2.cvtColor(np.array(roi_image), cv2.COLOR_RGB2BGR)
        img = cv2.resize(cv_img, (self.FEATURE_INPUT_SIZE, self.FEATURE_INPUT_SIZE))
        return img

    def set_movement_absolute(self, new_block, duration):
        logger.debug('set_movement_absolute')
        degrees = self.calculate_degrees(new_block)
        length = math.hypot(new_block[self.START_Y] - self.current_block[self.START_Y],
                            new_block[self.START_X] - self.current_block[self.START_X])
        speed = length / duration / constants.ACTUAL_SPEED_TIMES
        logger.debug('absolute params is {0} {1} {2}'.format(degrees, speed, duration))
        return self.set_movement_relative(degrees, speed, duration)

    def set_movement_relative(self, degrees, speed, duration):
        logger.debug('set_movement_relative')
        action = {constants.DEGREES: degrees, constants.SPEED: speed, constants.DURATION: duration,
                  constants.PHYSICAL_MEMORY_TYPE: constants.VISION_FOCUS_MOVE}
        memories = self.data_service.get_vision_move_memory(degrees, speed, duration)
        if memories is None or len(memories) == 0:
            action_memory = memory.add_physical_memory(action)
        else:
            mem = memories[0]
            memory.recall_memory(mem)
            action_memory = mem
        slice_memory = memory.add_collection_memory(constants.SLICE_MEMORY, [action_memory])
        self.current_action = copy.deepcopy(action)
        self.current_action.update({self.LAST_MOVE_TIME: time.time(), self.STATUS: self.IN_PROGRESS})
        return slice_memory

    def restrict_edge_start_x(self, new_start_x):
        actual_start_x = new_start_x
        if new_start_x < 0:
            actual_start_x = 0
        if new_start_x + self.current_block[self.WIDTH] > self.SCREEN_WIDTH:
            actual_start_x = self.SCREEN_WIDTH - self.current_block[self.WIDTH]
        return int(round(actual_start_x))

    def restrict_edge_start_y(self, new_start_y):
        actual_start_y = new_start_y
        if new_start_y < 0:
            actual_start_y = 0
        if new_start_y + self.current_block[self.HEIGHT] > self.SCREEN_HEIGHT:
            actual_start_y = self.SCREEN_HEIGHT - self.current_block[self.HEIGHT]
        return int(round(actual_start_y))

    def calculate_degrees(self, new_block):
        radians = math.atan2(new_block[self.START_Y] - self.current_block[self.START_Y],
                             new_block[self.START_X] - self.current_block[self.START_X])
        degrees = math.degrees(radians)
        return int(round(degrees / float(constants.ACTUAL_DEGREES_TIMES)))

    def try_move_away(self, elapse, degrees, speed):
        # actual degrees is 10 times
        actual_degrees = degrees * constants.ACTUAL_DEGREES_TIMES
        # actual speed is 50 times
        actual_speed = speed * constants.ACTUAL_SPEED_TIMES
        new_start_y = self.current_block[self.START_Y] + math.sin(math.radians(actual_degrees)) * elapse * actual_speed
        new_start_x = self.current_block[self.START_X] + math.cos(math.radians(actual_degrees)) * elapse * actual_speed
        new_block = copy.deepcopy(self.current_block)
        new_block[self.START_X] = int(new_start_x)
        new_block[self.START_Y] = int(new_start_y)
        if not self.verify_block(new_block):
            return None
        return new_block

    def calculate_move_action(self, action):
        logger.debug('calculate_move_action')
        elapse = time.time() - action[self.LAST_MOVE_TIME]
        duration = action[constants.DURATION]
        degrees = action[constants.DEGREES]
        speed = action[constants.SPEED]
        if elapse >= duration:
            # if process slow, destination will be quite different
            elapse = duration
            action.update({self.STATUS: self.COMPLETED})
        logger.debug('elapse is {0}, degrees is {1}, speed is {2}'.format(elapse, degrees, speed))
        new_block = self.try_move_away(elapse, degrees, speed)
        logger.debug('new block is {0}'.format(new_block))
        if new_block:
            self.current_block = new_block
            action[self.LAST_MOVE_TIME] = time.time()
            action[constants.DURATION] = duration - elapse
        else:
            action.update({self.STATUS: self.COMPLETED})

    def calculate_blocks_histogram(self, full_image, blocks_x, blocks_y):
        blocks_histogram = []
        width = self.current_block[self.WIDTH]
        height = self.current_block[self.HEIGHT]
        b, g, r = cv2.split(full_image)
        for j in range(0, blocks_y):
            for i in range(0, blocks_x):
                ret_b = b[j * height:(j + 1) * height, i * width:(i + 1) * width]
                ret_g = g[j * height:(j + 1) * height, i * width:(i + 1) * width]
                ret_r = r[j * height:(j + 1) * height, i * width:(i + 1) * width]
                ret = np.concatenate([ret_b, ret_g, ret_r])
                hist_np, bins = np.histogram(ret.ravel(), bins=self.HISTOGRAM_BINS, range=[0, 256])
                blocks_histogram.append(hist_np)
        return blocks_histogram

    def match_movement_memories(self, memories):
        mem = memories[0]
        logger.info('reproduce movement {0}'.format(mem))
        degrees = mem[constants.DEGREES]
        speed = mem[constants.SPEED]
        duration = mem[constants.DURATION]
        if duration == 0:
            new_block = self.try_move_aside(degrees)
            if not new_block:
                return None
            self.current_block = new_block
        else:
            new_block = self.try_move_away(duration, degrees, speed)
            if not new_block:
                return None
            self.current_action = {constants.DEGREES: degrees, constants.SPEED: speed, constants.DURATION: duration,
                                   self.LAST_MOVE_TIME: time.time(), self.STATUS: self.IN_PROGRESS}
        memory.recall_memory(mem)
        mem[constants.STATUS] = constants.MATCHED
        mem.update({constants.HAPPEN_TIME: time.time()})
        return mem

    def match_zoom_memories(self, memories):
        mem = memories[0]
        logger.info('reproduce zoom '.format(mem))
        zoom_type = mem[constants.ZOOM_TYPE]
        zoom_direction = mem[constants.ZOOM_DIRECTION]
        if zoom_type is self.ZOOM_OUT:
            new_block = self.try_zoom_out(zoom_direction)
        else:
            new_block = self.try_zoom_in(zoom_direction)
        if new_block is None:
            return None
        self.roi_index = new_block[self.ROI_INDEX_NAME]
        self.current_block = new_block
        memory.recall_memory(mem)
        mem[constants.STATUS] = constants.MATCHED
        mem.update({constants.HAPPEN_TIME: time.time()})
        return mem

    def grab(self, top, left, width, height):
        return None

    def move_focus_to_mouse(self):
        logger.debug('move_focus_to_mouse')
        new_block = {}
        mouse_x = int(self.mouse.position[0])
        mouse_y = int(self.mouse.position[1])
        new_start_x = mouse_x - self.current_block[self.WIDTH] / 2
        new_start_y = mouse_y - self.current_block[self.HEIGHT] / 2
        new_block[self.START_X] = self.restrict_edge_start_x(new_start_x)
        new_block[self.START_Y] = self.restrict_edge_start_y(new_start_y)
        logger.debug('current block is {0}'.format(self.current_block))
        logger.debug('new block is {0}'.format(new_block))
        return self.set_movement_absolute(new_block, 0.5)


def get_channel_img(bgr, channel):
    # start = time.time()
    yuv = cv2.cvtColor(bgr, cv2.COLOR_BGR2YUV)
    y, u, v = cv2.split(yuv)
    if channel == 'y':
        return y
    elif channel == 'u':
        return u
    elif channel == 'v':
        return v


def add_new_slice_memory(new_slice_memory, sequential_time_memories, working_memories):
    if new_slice_memory is not None:
        sequential_time_memories[constants.SLICE_MEMORY].append(new_slice_memory)
        working_memories.append(new_slice_memory)
