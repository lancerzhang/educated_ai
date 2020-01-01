import collections
from . import constants
import copy
import cv2
import librosa
import logging
import math
import numpy as np
import random
import skimage.measure
import time
from . import util

logger = logging.getLogger('Sound')
logger.setLevel(logging.ERROR)


class Sound(object):
    SAMPLE_RATE = 44100
    MAX_FREQUENCY = 8000
    phases = collections.deque()  # phases queue
    ENERGY_THRESHOLD = 250  # minimum audio energy to consider for processing
    DEFAULT_PHASE_DURATION = 0.2  # second of buffer

    FREQUENCY_MAP_HEIGHT = 20
    HOP_LENGTH = 512
    FEATURE_INPUT_SIZE = 12
    FEATURE_THRESHOLD = 10
    FEATURE_SIMILARITY_THRESHOLD = 0.2
    POOL_BLOCK_SIZE = 2  # after down-sampling, feature is 3x3
    SOUND_KERNEL_FILE = 'kernels.npy'
    previous_energies = []
    MAX_DB = 80.0

    ROI_ARR = [3, 5, 9, 13]
    ROI_LEVEL = 1
    current_range = {}
    RANGE_ARR = [5, 10, 15]
    RANGE = 'rng'
    REGION_VARIANCE_THRESHOLD = 0.05

    FEATURE_DATA = {constants.KERNEL: [], constants.FEATURE: [], constants.SIMILAR: False}

    @util.timeit
    def __init__(self, bm):
        self.bio_memory = bm
        self.frequency_map = None
        buffer_duration = float(self.CHUNK) / self.SAMPLE_RATE
        self.buffer_count_of_phase = int(math.ceil(self.DEFAULT_PHASE_DURATION / buffer_duration))
        self.sound_kernels = np.load(self.SOUND_KERNEL_FILE)
        self.previous_phase = None

    @util.timeit
    def process(self, status_controller):
        start = time.time()
        self.frequency_map = self.get_frequency_map(status_controller)
        if self.frequency_map is None:
            logger.info('no frequency data!')
            return

        self.match_features()
        new_feature_memory = self.search_feature_memory()
        self.bio_memory.enrich_feature_memories(constants.SOUND_FEATURE, new_feature_memory)
        logger.info('sound process used time:{0}'.format(time.time() - start))

    @util.timeit
    def match_features(self):
        physical_memories = self.bio_memory.prepare_matching_physical_memories(constants.SOUND_FEATURE)
        data_map = self.get_data_map()
        for bm in physical_memories:
            self.match_feature(data_map, bm)
        self.bio_memory.verify_matching_physical_memories()

    @util.timeit
    def match_feature(self, data_map, fmm):
        kernel = fmm[constants.KERNEL]
        feature = fmm[constants.FEATURE]
        # data_range = fmm[RANGE]
        # frequency_map = full_frequency_map[data_range[0]:data_range[1], :]
        # data = filter_feature(frequency_map, kernel, feature)
        fmm.update({constants.STATUS: constants.MATCHING})
        feature_data = self.filter_feature(data_map, kernel, np.array(feature))
        if feature_data is None:
            return False  # not similar
        if feature_data[constants.SIMILAR]:
            # recall memory and update feature to average
            self.bio_memory.recall_feature_memory(fmm, feature_data[constants.FEATURE])
            self.update_kernel_rank(kernel)
        return feature_data[constants.SIMILAR]

    # match the experience sound sense
    @util.timeit
    def filter_feature(self, data_map, kernel, feature=None):
        feature_data = copy.deepcopy(self.FEATURE_DATA)
        feature_data[constants.KERNEL] = kernel
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
        # logger.debug('data map is {0}'.format(np.around(data_map, decimals=2)))
        # logger.debug('new_feature_pool1 is {0}'.format(new_feature_pool1))
        # logger.debug('new_feature_pool2 is {0}'.format(new_feature_pool2))
        # logger.debug('threshold_feature is {0}'.format(threshold_feature))
        standard_feature = util.standardize_feature(threshold_feature)
        new_feature = standard_feature.flatten().astype(int)
        if feature is None:
            feature_data[constants.FEATURE] = new_feature
        else:
            difference = util.np_array_diff(new_feature, feature)
            if difference < self.FEATURE_SIMILARITY_THRESHOLD:
                feature_data[constants.SIMILAR] = True
                avg_feature = (feature + new_feature) // 2
                feature_data[constants.FEATURE] = avg_feature
            else:
                feature_data[constants.FEATURE] = new_feature
        return feature_data

    # get a frequent use kernel or a random kernel by certain possibility
    @util.timeit
    def get_kernel(self):
        used_kernel = None
        ri = random.randint(0, 9) - 1
        # Give a chane to choose kernel for library
        if ri >= 0:
            used_kernel = self.bio_memory.data_adaptor.get_top_sound_used_kernel(ri)

        if used_kernel is None:
            shape = self.sound_kernels.shape
            index = random.randint(0, shape[0] - 1)
            kernel = self.sound_kernels[index]
            return kernel
        else:
            return used_kernel[constants.KERNEL]

    @util.timeit
    def update_kernel_rank(self, kernel):
        self.bio_memory.data_adaptor.put_sound_used_kernel(kernel)

    # try to search more detail
    @util.timeit
    def search_feature_memory(self):
        kernel = self.get_kernel()
        data = self.filter_feature(self.get_data_map(), kernel)
        if data is None:
            return None
        bm = self.find_feature_memory(kernel, data[constants.FEATURE])
        if bm is None:
            bm = self.bio_memory.add_feature_memory(constants.SOUND_FEATURE, kernel, data[constants.FEATURE])
        else:
            self.bio_memory.recall_physical_memory(bm)
        self.update_kernel_rank(kernel)
        return bm

    # search memory by kernel using index
    @util.timeit
    def find_feature_memory(self, kernel, feature1):
        feature_memories = self.bio_memory.get_sound_feature_memories(kernel)
        for mem in feature_memories:
            feature2 = mem[constants.FEATURE]
            difference = util.np_array_diff(feature1, np.array(feature2))
            if difference < self.FEATURE_SIMILARITY_THRESHOLD:
                return mem
        return None

    @util.timeit
    def get_frequency_map(self, status_controller):
        if len(self.phases) == 0:
            return None
        phase = self.phases.popleft()
        if self.previous_phase is None:
            self.previous_phase = phase
            return
        data = np.append(self.previous_phase, phase)
        map_width = (len(data) // self.HOP_LENGTH) + 1
        if map_width >= self.FEATURE_INPUT_SIZE:
            map_height = map_width
        else:
            map_height = self.FREQUENCY_MAP_HEIGHT
        # frequency_map = librosa.feature.mfcc(frame, sr=SAMPLE_RATE, n_mfcc=FREQUENCY_MAP_HEIGHT)
        mel_data = librosa.feature.melspectrogram(y=data, sr=self.SAMPLE_RATE, n_mels=map_height,
                                                  hop_length=self.HOP_LENGTH,
                                                  fmax=self.MAX_FREQUENCY)
        # logger.debug('frequency_map is {0}'.format(frequency_map))
        self.previous_phase = phase
        # after this method, data will be -80 to 0 db (max)
        frequency_map = librosa.power_to_db(mel_data, ref=self.MAX_FREQUENCY)
        frequency_map = frequency_map + self.MAX_DB
        frequency_map[frequency_map < 0] = 0
        return frequency_map

    @util.timeit
    def get_data_map(self):
        # map to image color range
        color_data = self.frequency_map / (self.MAX_DB / 256)
        data = color_data.astype(np.uint8)
        return cv2.resize(data, (self.FEATURE_INPUT_SIZE, self.FEATURE_INPUT_SIZE))
