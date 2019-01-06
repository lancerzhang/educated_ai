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
    START_X = 'sx'
    START_Y = 'sy'
    WIDTH = 'width'
    HEIGHT = 'height'
    HISTOGRAM_BINS = 27
    FEATURE_INPUT_SIZE = 12
    FEATURE_THRESHOLD = 20
    FEATURE_SIMILARITY_THRESHOLD = 0.2
    POOL_BLOCK_SIZE = 2  # after down-sampling, feature is 3x3
    NUMBER_SUB_REGION = 10
    REGION_VARIANCE_THRESHOLD = 0.05
    MAX_DEGREES = 36  # actuial is 10 times
    MAX_SPEED = 40  # actual is 50 times, pixel
    MAX_DURATION = 5  # actuial is 10%

    STATUS = 'sts'
    IN_PROGRESS = 'pgs'
    COMPLETED = 'cmp'
    MOVE = 'move'
    ZOOM_IN = 'zmi'
    ZOOM_OUT = 'zmo'
    CREATE_TIME = 'crt'
    USED_SPEED_FILE = 'data/vus.npy'
    USED_DEGREES_FILE = 'data/vud.npy'
    USED_KERNEL_FILE = 'data/vuk.npy'
    USED_CHANNEL_FILE = 'data/vuc.npy'
    MEMORY_INDEX_FILE = 'data/vmi.npy'
    VISION_KERNEL_FILE = 'kernels.npy'
    previous_energies = []
    previous_block_histogram = []

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
            self.calculate_action(self.current_action)

        slice_feature_memories = [mem for mem in working_memories if
                                  constants.MEMORY_DURATION in mem and
                                  mem[constants.MEMORY_DURATION] is constants.SLICE_MEMORY and
                                  mem[constants.STATUS] is constants.MATCHING and
                                  mem[constants.PHYSICAL_MEMORY_TYPE] is constants.VISION_FEATURE]

        matched_feature_memories = self.match_features(slice_feature_memories, working_memories,
                                                       sequential_time_memories)

        new_feature_memory = self.search_feature()
        if len(matched_feature_memories) > 0:
            matched_feature_memories_ids = [x[constants.MID] for x in matched_feature_memories]
            if new_feature_memory is not None and new_feature_memory[constants.MID] not in matched_feature_memories_ids:
                matched_feature_memories.append(new_feature_memory)
            new_slice_memory = memory.add_collection_memory(constants.SLICE_MEMORY, matched_feature_memories)
            sequential_time_memories[constants.SLICE_MEMORY].append(new_slice_memory)
            working_memories.append(new_slice_memory)
        elif new_feature_memory is not None:
            new_slice_memories = memory.get_live_sub_memories(new_feature_memory, constants.PARENT_MEM)
            new_matched_feature_memories = self.match_features(new_slice_memories, working_memories,
                                                               sequential_time_memories)
            new_matched_feature_memories_ids = [x[constants.MID] for x in new_matched_feature_memories]
            if new_feature_memory[constants.MID] not in new_matched_feature_memories_ids:
                new_matched_feature_memories.append(new_feature_memory)
            new_slice_memory = memory.add_collection_memory(constants.SLICE_MEMORY, new_matched_feature_memories)
            sequential_time_memories[constants.SLICE_MEMORY].append(new_slice_memory)
            working_memories.append(new_slice_memory)

        # when she's mature, below is the major way of focus move/zoom.
        slice_movement_memories = [mem for mem in working_memories if
                                   constants.MEMORY_DURATION in mem and
                                   mem[constants.MEMORY_DURATION] is constants.SLICE_MEMORY and
                                   mem[constants.STATUS] is constants.MATCHING and
                                   mem[constants.PHYSICAL_MEMORY_TYPE] is constants.VISION_FOCUS_MOVE]

        if self.current_action[self.STATUS] is not self.IN_PROGRESS:
            if len(slice_movement_memories) > 0:
                new_slice_memory = self.match_movement_memories(slice_movement_memories)
                sequential_time_memories[constants.SLICE_MEMORY].append(new_slice_memory)
                working_memories.append(new_slice_memory)

        slice_zoom_memories = [mem for mem in working_memories if
                               constants.MEMORY_DURATION in mem and
                               mem[constants.MEMORY_DURATION] is constants.SLICE_MEMORY and
                               mem[constants.STATUS] is constants.MATCHING and
                               mem[constants.PHYSICAL_MEMORY_TYPE] is constants.VISION_FOCUS_ZOOM]

        if len(slice_zoom_memories) > 0:
            new_slice_memory = self.match_zoom_memories(slice_zoom_memories)
            sequential_time_memories[constants.SLICE_MEMORY].append(new_slice_memory)
            working_memories.append(new_slice_memory)

        # when she's not mature, need to guide her.
        if self.current_action[self.STATUS] is not self.IN_PROGRESS:
            if key is constants.KEY_ALT or key is constants.KEY_CTRL:
                # the 1st and most efficient way is to set focus directly, and reward it
                new_slice_memory = self.move_focus_to_mouse()
                sequential_time_memories[constants.SLICE_MEMORY].append(new_slice_memory)
                working_memories.append(new_slice_memory)
            elif work_status[constants.REWARD]:
                # stay more time on reward region.
                print ''
            elif not work_status[constants.REWARD]:
                # move out from current reward region.
                if not work_status[constants.BUSY][constants.SHORT_DURATION]:
                    # affected by environment vision change.
                    new_slice_memory = self.aware()
                    if new_slice_memory is not None:
                        sequential_time_memories[constants.SLICE_MEMORY].append(new_slice_memory)
                        working_memories.append(new_slice_memory)
                if not work_status[constants.BUSY][constants.MEDIUM_DURATION]:
                    # if environment not change, random do some change.
                    new_slice_memory = self.explore()
                    if new_slice_memory is not None:
                        sequential_time_memories[constants.SLICE_MEMORY].append(new_slice_memory)
                        working_memories.append(new_slice_memory)

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
        img = self.get_region()
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
        start = time.time()
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
        if threshold_feature.sum() == 0:
            return None  # no any feature found
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
        logger.debug('filter_feature used time:{0}'.format(time.time() - start))
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

    # try to find more detail
    def search_feature(self):
        start = time.time()
        channel = self.get_channel()
        img = self.get_region()
        kernel = self.get_kernel()
        channel_img = get_channel_img(img, channel)
        data = self.filter_feature(channel_img, kernel)
        if data is None:
            return None
        mem = self.search_feature_memory(channel, kernel, data[constants.FEATURE])
        if mem is None:
            mem = memory.add_vision_feature_memory(constants.VISION_FEATURE, channel, kernel, data[constants.FEATURE])
            self.update_memory_indexes(channel, kernel, mem[constants.MID])
        self.update_kernel_rank(kernel)
        self.update_channel_rank(channel)
        logger.debug('search_feature used time:{0}'.format(time.time() - start))
        return mem

    # search memory by kernel using index
    def search_feature_memory(self, channel, kernel, feature1):
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

    def aware(self):
        start = time.time()
        duration = self.get_duration()
        pil_image = self.grab(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        full_img = np.array(pil_image)
        block = self.find_most_variable_region(full_img)
        if block is not None and block['v'] > self.REGION_VARIANCE_THRESHOLD:
            # move focus to variable region
            return self.set_movement_absolute(block, duration)
        logger.debug('aware used time:{0}'.format(time.time() - start))

    def find_most_variable_region(self, full_img):
        start = time.time()
        new_block = {}
        channel_img = get_channel_img(full_img, 'y')
        this_block_histogram = self.calculate_block_histogram(channel_img)
        if len(self.previous_block_histogram) == 0:
            self.previous_block_histogram = this_block_histogram
            return None
        else:
            diff_arr = util.np_matrix_diff(this_block_histogram, self.previous_block_histogram)
            self.previous_block_histogram = this_block_histogram
            max_index = np.argmax(diff_arr)
            max_var = diff_arr[max_index]
            if max_var < self.REGION_VARIANCE_THRESHOLD:
                return None
            width = self.SCREEN_WIDTH / self.NUMBER_SUB_REGION
            height = self.SCREEN_HEIGHT / self.NUMBER_SUB_REGION
            new_index_x, new_index_y = util.convert_1d_to_2d_index(max_index, self.NUMBER_SUB_REGION)
            new_start_x = new_index_x * width
            new_start_y = new_index_y * height
            new_block[self.START_X] = self.calculate_start_x(new_start_x)
            new_block[self.START_Y] = self.calculate_start_y(new_start_y)
            new_block.update({'v': max_var})
            self.previous_block_histogram = this_block_histogram
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

    def explore(self):
        ri = random.randint(0, 9)
        if ri == 0:
            return self.random_move()
        elif ri == 1:
            return self.random_zoom()

    def random_move(self):
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

    def random_zoom(self):
        ri = random.randint(0, 1)
        if ri == 0:
            zoom_type = self.zoom_in()
        else:
            zoom_type = self.zoom_out()
        if zoom_type is None:
            return None
        action = {constants.PHYSICAL_MEMORY_TYPE: constants.VISION_FOCUS_ZOOM, constants.ZOOM_TYPE: zoom_type}
        memories = self.data_service.get_vision_zoom_memory(zoom_type)
        if memories is None or len(memories) == 0:
            action_memory = memory.add_physical_memory(action)
        else:
            mem = memories[0]
            memory.recall_memory(mem)
            action_memory = mem
        slice_memory = memory.add_collection_memory(constants.SLICE_MEMORY, [action_memory])
        return slice_memory

    def zoom_in(self):
        temp_index = self.roi_index - 1
        if temp_index < 0:
            return None
        self.roi_index = temp_index
        self.current_block[self.WIDTH] = self.ROI_ARR[self.roi_index]
        self.current_block[self.HEIGHT] = self.ROI_ARR[self.roi_index]
        return self.ZOOM_IN

    def zoom_out(self):
        temp_index = self.roi_index + 1
        if temp_index > (len(self.ROI_ARR) - 1):
            return None
        temp_width = self.ROI_ARR[temp_index]
        if self.current_block[self.START_X] + temp_width > self.SCREEN_WIDTH:
            return None
        if self.current_block[self.START_Y] + temp_width > self.SCREEN_HEIGHT:
            return None
        self.roi_index = temp_index
        self.current_block[self.WIDTH] = self.ROI_ARR[self.roi_index]
        self.current_block[self.HEIGHT] = self.ROI_ARR[self.roi_index]
        return self.ZOOM_OUT

    def get_region(self):
        start = time.time()
        roi_image = self.grab(self.current_block[self.START_Y], self.current_block[self.START_X],
                              self.current_block[self.WIDTH], self.current_block[self.HEIGHT])
        cv_img = cv2.cvtColor(np.array(roi_image), cv2.COLOR_RGB2BGR)
        img = cv2.resize(cv_img, (self.FEATURE_INPUT_SIZE, self.FEATURE_INPUT_SIZE))
        logger.debug('get_region used time:{0}'.format(time.time() - start))
        return img

    def set_movement_absolute(self, new_block, duration):
        degrees = self.calculate_degrees(new_block)
        length = math.hypot(new_block[self.START_Y] - self.current_block[self.START_Y],
                            new_block[self.START_X] - self.current_block[self.START_X])
        speed = length / duration / constants.ACTUAL_SPEED_TIMES
        return self.set_movement_relative(degrees, speed, duration)

    def set_movement_relative(self, degrees, speed, duration):
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
        self.current_action.update({self.CREATE_TIME: time.time(), self.STATUS: self.IN_PROGRESS})
        return slice_memory

    def calculate_start_x(self, new_start_x):
        actual_start_x = new_start_x
        if new_start_x < 0:
            actual_start_x = 0
        if new_start_x + self.current_block[self.WIDTH] > self.SCREEN_WIDTH:
            actual_start_x = self.SCREEN_WIDTH - self.current_block[self.WIDTH]
        return int(round(actual_start_x))

    def calculate_start_y(self, new_start_y):
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

    def calculate_action(self, action):
        elapse = time.time() - action[self.CREATE_TIME]
        if elapse >= action[constants.DURATION]:
            # if process slow, destination will be quite different
            elapse = action[constants.DURATION]
            action.update({self.STATUS: self.COMPLETED})
        # actual degrees is 10 times
        degrees = action[constants.DEGREES] * constants.ACTUAL_DEGREES_TIMES
        # actual speed is 50 times
        speed = action[constants.SPEED] * constants.ACTUAL_SPEED_TIMES
        new_start_y = self.current_block[self.START_Y] + (math.sin(math.radians(degrees)) * elapse * speed)
        new_start_x = self.current_block[self.START_X] + (math.cos(math.radians(degrees)) * elapse * speed)
        self.current_block[self.START_X] = self.calculate_start_x(new_start_x)
        self.current_block[self.START_Y] = self.calculate_start_y(new_start_y)

    def calculate_block_histogram(self, channel_img):
        block_histogram = []
        width = self.SCREEN_WIDTH / self.NUMBER_SUB_REGION
        height = self.SCREEN_HEIGHT / self.NUMBER_SUB_REGION
        for j in range(0, self.NUMBER_SUB_REGION):
            for i in range(0, self.NUMBER_SUB_REGION):
                ret = channel_img[j * height:(j + 1) * height, i * width:(i + 1) * width]
                hist_np, bins = np.histogram(ret.ravel(), bins=self.HISTOGRAM_BINS, range=[0, 256])
                block_histogram.append(hist_np)
        return block_histogram

    def match_movement_memories(self, memories):
        mem = memories[0]
        logger.info('reproduce movement {0}'.format(mem))
        memory.recall_memory(mem)
        self.current_action = {constants.DEGREES: mem[constants.DEGREES], constants.SPEED: mem[constants.SPEED],
                               constants.DURATION: mem[constants.DURATION], self.CREATE_TIME: time.time(),
                               constants.PHYSICAL_MEMORY_TYPE: constants.VISION_FOCUS_MOVE,
                               self.STATUS: self.IN_PROGRESS}
        mem.update({constants.HAPPEN_TIME: time.time()})
        mem[constants.STATUS] = constants.MATCHED
        return mem

    def match_zoom_memories(self, memories):
        mem = memories[0]
        logger.info('reproduce zoom '.format(mem))
        memory.recall_memory(mem)
        zoom_type = mem[constants.ZOOM_TYPE]
        if zoom_type is self.ZOOM_OUT:
            self.zoom_out()
        elif zoom_type is self.ZOOM_IN:
            self.zoom_in()
        mem[constants.STATUS] = constants.MATCHED
        mem.update({constants.HAPPEN_TIME: time.time()})
        return mem

    def grab(self, top, left, width, height):
        return None

    def move_focus_to_mouse(self):
        new_block = {}
        mouse_x = int(self.mouse.position[0])
        mouse_y = int(self.mouse.position[1])
        new_start_x = mouse_x - self.current_block[self.WIDTH] / 2
        new_start_y = mouse_y - self.current_block[self.HEIGHT] / 2
        new_block[self.START_X] = self.calculate_start_x(new_start_x)
        new_block[self.START_Y] = self.calculate_start_y(new_start_y)
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
