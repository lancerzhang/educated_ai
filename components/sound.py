import collections
import constants
import copy
import cv2
import librosa
import logging
import numpy as np
import random
import skimage.measure
import time
import util

logger = logging.getLogger('Sound')
logger.setLevel(logging.INFO)


class Sound(object):
    SAMPLE_RATE = 44100
    MAX_FREQUENCY = 8000
    phases = collections.deque()  # phases queue
    ENERGY_THRESHOLD = 250  # minimum audio energy to consider for processing

    FREQUENCY_MAP_HEIGHT = 20
    HOP_LENGTH = 512
    FEATURE_INPUT_SIZE = 12
    FEATURE_THRESHOLD = 10
    FEATURE_SIMILARITY_THRESHOLD = 0.2
    POOL_BLOCK_SIZE = 2  # after down-sampling, feature is 3x3
    USED_KERNEL_FILE = 'data/suk.npy'
    MEMORY_INDEX_FILE = 'data/smi.npy'
    SOUND_KERNEL_FILE = 'kernels.npy'
    previous_energies = []

    ROI_ARR = [3, 5, 9, 13]
    ROI_LEVEL = 1
    current_range = {}
    RANGE_ARR = [5, 10, 15]
    RANGE = 'rng'
    REGION_VARIANCE_THRESHOLD = 0.05

    FEATURE_DATA = {constants.KERNEL: [], constants.FEATURE: [], constants.SIMILAR: False}

    def __init__(self, bm):
        self.bio_memory = bm
        self.frequency_map = None
        try:
            self.memory_indexes = np.load(self.MEMORY_INDEX_FILE)
        except IOError:
            self.memory_indexes = np.array([])

        try:
            self.used_kernel_rank = np.load(self.USED_KERNEL_FILE)
        except IOError:
            self.used_kernel_rank = np.array([])

        self.sound_kernels = np.load(self.SOUND_KERNEL_FILE)
        self.previous_phase = None

    def save_files(self):
        np.save(self.MEMORY_INDEX_FILE, self.memory_indexes)
        np.save(self.USED_KERNEL_FILE, self.used_kernel_rank)

    def process(self, work_status):
        logger.info('process')
        start = time.time()
        self.frequency_map = self.get_frequency_map()
        if self.frequency_map is None:
            logger.error('no frequency data!')
            return

        self.match_features()
        new_feature_memory = self.search_feature_memory()
        self.bio_memory.enrich_feature_memories(constants.SOUND_FEATURE, new_feature_memory)

        if not work_status[constants.BUSY][constants.LONG_DURATION]:
            self.save_files()
        logger.info('process used time:{0}'.format(time.time() - start))

    def match_features(self):
        physical_memories = self.bio_memory.prepare_matching_physical_memories(constants.SOUND_FEATURE)
        for bm in physical_memories:
            self.match_feature(bm)
        self.bio_memory.verify_matching_physical_memories()

    def match_feature(self, fmm):
        kernel = fmm[constants.KERNEL]
        feature = fmm[constants.FEATURE]
        # data_range = fmm[RANGE]
        # frequency_map = full_frequency_map[data_range[0]:data_range[1], :]
        # data = filter_feature(frequency_map, kernel, feature)
        fmm.update({constants.STATUS: constants.MATCHING})
        feature_data = self.filter_feature(self.frequency_map, kernel, np.array(feature))
        if feature_data is None:
            return False  # not similar
        if feature_data[constants.SIMILAR]:
            # recall memory and update feature to average
            self.bio_memory.recall_feature_memory(fmm, feature_data[constants.FEATURE])
            self.update_kernel_rank(kernel)
        return feature_data[constants.SIMILAR]

    # match the experience sound sense
    def filter_feature(self, raw, kernel, feature=None):
        logger.debug('filter_feature')
        # map to image color range
        color_data = raw / (self.MAX_FREQUENCY / 256)
        data = color_data.astype(np.uint8)
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
        logger.debug('data map is {0}'.format(np.around(data_map, decimals=2)))
        logger.debug('new_feature_pool1 is {0}'.format(new_feature_pool1))
        logger.debug('new_feature_pool2 is {0}'.format(new_feature_pool2))
        logger.debug('threshold_feature is {0}'.format(threshold_feature))
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
            shape = self.sound_kernels.shape
            index = random.randint(0, shape[0] - 1)
            kernel = self.sound_kernels[index]
            return kernel
        else:
            return used_kernel[constants.KERNEL]

    def update_kernel_rank(self, kernel):
        self.used_kernel_rank = util.update_rank_list(constants.KERNEL, kernel, self.used_kernel_rank)

    # try to search more detail
    def search_feature_memory(self):
        logger.debug('search_feature_memory')
        kernel = self.get_kernel()
        # range_width = get_range()
        # energies = get_energy(full_frequency_map)
        # range_energies = get_range_energy(energies, range_width)
        # max_index = np.argmax(range_energies)
        # new_range = expend_max(range_energies, [max_index, max_index], range_width)
        # frequency_map = full_frequency_map[new_range[0]:new_range[1], :]
        # data = filter_feature(frequency_map, kernel)
        data = self.filter_feature(self.frequency_map, kernel)
        if data is None:
            return None
        logger.debug('feature data is {0}'.format(data))
        bm = self.find_feature_memory(kernel, data[constants.FEATURE])
        if bm is None:
            bm = self.bio_memory.add_feature_memory(constants.SOUND_FEATURE, kernel, data[constants.FEATURE])
            self.update_memory_indexes(kernel, bm[constants.MID])
        else:
            self.bio_memory.recall_physical_memory(bm)
        self.update_kernel_rank(kernel)
        return bm

    # search memory by kernel using index
    def find_feature_memory(self, kernel, feature1):
        element = next((x for x in self.memory_indexes if x[constants.KERNEL] == kernel), None)
        if element is not None:
            memory_ids = element[constants.MEMORIES]
            live_memories = self.bio_memory.search_live_memories(memory_ids)
            if live_memories is not None:
                for mem in live_memories:
                    feature2 = mem[constants.FEATURE]
                    difference = util.np_array_diff(feature1, np.array(feature2))
                    if difference < self.FEATURE_SIMILARITY_THRESHOLD:
                        return mem
        return None

    def update_memory_indexes(self, kernel, mid):
        element = next((x for x in self.memory_indexes if x[constants.KERNEL] == kernel), None)
        if element is None:
            new_kernel = {constants.KERNEL: kernel, constants.MEMORIES: [mid]}
            self.memory_indexes = np.append(self.memory_indexes, new_kernel)
        else:
            memory_ids = element[constants.MEMORIES]
            if mid not in memory_ids:
                memory_ids.append(mid)

    def aware(self, full_frequency_map):
        range_data = self.find_most_variable_region(full_frequency_map)
        frequency_map = full_frequency_map[range_data[0]:range_data[1], :]
        kernel = self.get_kernel()
        data = self.filter_feature(frequency_map, kernel)
        if range_data['v'] > self.REGION_VARIANCE_THRESHOLD:
            fmm = self.bio_memory.add_feature_memory(constants.SOUND_FEATURE, kernel, data[constants.FEATURE])
            smm = self.bio_memory.add_virtual_memory(constants.SLICE_MEMORY, [fmm], constants.SOUND_FEATURE)
            return smm
        else:
            return None

    def find_most_variable_region(self, frequency_map):
        range_width = self.get_range()
        new_range = {}
        this_energies = get_energy(frequency_map)
        if len(self.previous_energies) == 0:
            self.previous_energies = this_energies
        else:
            previous_range_energies = get_range_energy(self.previous_energies, range_width)
            this_range_energy = get_range_energy(this_energies, range_width)
            diff_arr = abs(previous_range_energies - this_range_energy) / this_range_energy
            max_index = np.argmax(diff_arr)
            max_var = diff_arr(max_index)
            new_range.update({self.RANGE: [max_index, max_index + range_width]})
            new_range.update({'v': max_var})
            self.previous_energies = this_energies
        return new_range

    def get_frequency_map(self):
        logger.debug('get_frequency_map')
        if len(self.phases) == 0:
            return None
        phase = self.phases.popleft()
        if self.previous_phase is None:
            self.previous_phase = phase
            return
        data = np.append(self.previous_phase, phase)
        map_width = (len(data) / self.HOP_LENGTH) + 1
        if map_width >= self.FEATURE_INPUT_SIZE:
            map_height = map_width
        else:
            map_height = self.FREQUENCY_MAP_HEIGHT
        # frequency_map = librosa.feature.mfcc(frame, sr=SAMPLE_RATE, n_mfcc=FREQUENCY_MAP_HEIGHT)
        frequency_map = librosa.feature.melspectrogram(y=data, sr=self.SAMPLE_RATE, n_mels=map_height,
                                                       hop_length=self.HOP_LENGTH,
                                                       fmax=self.MAX_FREQUENCY)
        # logger.debug('frequency_map is {0}'.format(frequency_map))
        self.previous_phase = phase
        return frequency_map

    def get_range(self):
        index = random.randint(0, len(self.RANGE_ARR) - 1)
        return self.RANGE_ARR[index]

    def expend_max(self, range_energies, temp_range, range_width):
        new_range = []
        if temp_range[0] > 0:
            if temp_range[1] < len(range_energies):
                left_energy = range_energies[temp_range[0] - 1]
                right_energy = range_energies[temp_range[1] + 1]
                if left_energy >= right_energy:
                    new_range.append(temp_range[0] - 1)
                    new_range.append(temp_range[1])
                else:
                    new_range.append(temp_range[0])
                    new_range.append(temp_range[1] + 1)
            else:
                new_range.append(temp_range[0] - 1)
                new_range.append(temp_range[1])
        else:
            new_range.append(temp_range[0])
            new_range.append(temp_range[1] + 1)
        if len(new_range) < range_width:
            self.expend_max(range_energies, temp_range, range_width)
        else:
            return new_range


def get_energy(frequency_map):
    this_energy = []
    for i in range(0, len(frequency_map)):
        line = frequency_map[i]
        energy = np.average(line)
        this_energy.append(energy)
    return this_energy


def get_range_energy(energy, range_width):
    range_energies = []
    for i in range(0, len(energy) - range_width):
        range_energies.append(np.average(energy[i:i + range_width]))
    return np.array(range_energies)
