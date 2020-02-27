import collections
import cv2
import librosa
import logging
import math
import numpy as np
import random
import skimage.measure
import time
from . import constants
from . import util
from .brain import Brain
from .favor import Favor
from .featurepack import FeaturePack
from .memory import Memory
from .memory import RealType
from multiprocessing import Pool

logger = logging.getLogger('Sound')
logger.setLevel(logging.INFO)

MAX_FREQUENCY = 8000
ENERGY_THRESHOLD = 250  # minimum audio energy to consider for processing
DEFAULT_PHASE_DURATION = 0.2  # second of buffer

FREQUENCY_MAP_HEIGHT = 20
HOP_LENGTH = 512
FEATURE_INPUT_SIZE = 12
FEATURE_THRESHOLD = 10
FEATURE_SIMILARITY_THRESHOLD = 0.2
POOL_BLOCK_SIZE = 2  # after down-sampling, feature is 3x3
SOUND_KERNEL_FILE = 'kernels.npy'
MAX_DB = 80.0
SOUND_USED_KERNEL = 'suk'


# match the experience sound sense
def filter_feature(fp: FeaturePack):
    kernel_arr = util.string_to_feature_matrix(fp.kernel)
    cov = cv2.filter2D(fp.data, -1, kernel_arr)
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
    # logger.debug('data map is {0}'.format(np.around(data_map, decimals=2)))
    # logger.debug('new_feature_pool1 is {0}'.format(new_feature_pool1))
    # logger.debug('new_feature_pool2 is {0}'.format(new_feature_pool2))
    # logger.debug('threshold_feature is {0}'.format(threshold_feature))
    standard_feature = util.standardize_feature(threshold_feature)
    new_feature = standard_feature.flatten().astype(int)
    fp.feature = new_feature
    if fp.contrast is not None:
        difference = util.np_array_diff(new_feature, fp.contrast)
        if difference < FEATURE_SIMILARITY_THRESHOLD:
            fp.similar = True
    return fp


class Sound(object):
    CHUNK = 64  # for UT only
    SAMPLE_RATE = 44100
    phases = collections.deque()  # phases queue

    @util.timeit
    def __init__(self, brain: Brain, favor: Favor):
        self.brain = brain
        self.favor = favor
        self.frequency_map = None
        buffer_duration = float(self.CHUNK) / self.SAMPLE_RATE
        self.buffer_count_of_phase = int(math.ceil(DEFAULT_PHASE_DURATION / buffer_duration))
        self.sound_kernels = np.load(SOUND_KERNEL_FILE)
        self.previous_phase = None
        self.config = None
        self.data_map = None
        self.pool = Pool()

    @util.timeit
    def process(self, status_controller):
        self.config = status_controller
        if not self.init_data_map():
            return
        self.match_features()
        self.search_feature_memory()

    @util.timeit
    def match_features(self):
        feature_memories = self.brain.get_matching_real_memories(RealType.SOUND_FEATURE)
        data_inputs = [FeaturePack(mid=m.mid, kernel=m.kernel, contrast=m.feature, data=self.data_map) for m in
                       feature_memories]
        for fp in self.pool.imap_unordered(filter_feature, data_inputs):
            if fp.similar:
                m = self.brain.memory_indexes.get(fp.mid)
                m.matched()
                self.update_used_kernel(fp.kernel)
        # for m in feature_memories:
        #     fp = self.filter_feature(FeaturePack(mid=m.mid, kernel=m.kernel, feature=m.feature))
        #     if fp.similar:
        #         m.matched()
        #         self.update_used_kernel(m.kernel)

    # get a frequent use kernel or a random kernel by certain possibility

    # for UT
    def filter_feature(self, fp):
        self.init_data_map()
        fp.data = self.data_map
        return filter_feature(fp)

    @util.timeit
    def get_kernel(self):
        used_kernel = None
        ri = random.randint(0, 9) - 1
        # Give a chane to choose kernel for library
        if ri >= 0:
            used_kernel = self.favor.top(SOUND_USED_KERNEL, ri)

        if used_kernel is None:
            shape = self.sound_kernels.shape
            index = random.randint(0, shape[0] - 1)
            kernel = self.sound_kernels[index]
            return kernel
        else:
            return used_kernel.key

    @util.timeit
    def update_used_kernel(self, kernel):
        self.favor.update(SOUND_USED_KERNEL, kernel)

    @util.timeit
    def search_feature_memory(self):
        kernel = self.get_kernel()
        feature = filter_feature(FeaturePack(kernel=kernel, data=self.data_map))
        if feature.feature is None:
            return
        self.brain.put_feature_memory(RealType.SOUND_FEATURE, kernel, feature.feature)
        self.update_used_kernel(kernel)

    @util.timeit
    def get_frequency_map(self, config):
        if len(self.phases) == 0:
            return None
        phase = self.phases.popleft()
        if self.previous_phase is None:
            self.previous_phase = phase
            return
        data = np.append(self.previous_phase, phase)
        map_width = (len(data) // HOP_LENGTH) + 1
        if map_width >= FEATURE_INPUT_SIZE:
            map_height = map_width
        else:
            map_height = FREQUENCY_MAP_HEIGHT
        # frequency_map = librosa.feature.mfcc(frame, sr=SAMPLE_RATE, n_mfcc=FREQUENCY_MAP_HEIGHT)
        mel_data = librosa.feature.melspectrogram(y=data, sr=self.SAMPLE_RATE, n_mels=map_height,
                                                  hop_length=HOP_LENGTH,
                                                  fmax=MAX_FREQUENCY)
        # logger.debug('frequency_map is {0}'.format(frequency_map))
        self.previous_phase = phase
        # after this method, data will be -80 to 0 db (max)
        frequency_map = librosa.power_to_db(mel_data, ref=MAX_FREQUENCY)
        frequency_map = frequency_map + MAX_DB
        frequency_map[frequency_map < 0] = 0
        return frequency_map

    @util.timeit
    def init_data_map(self):
        frequency_map = self.get_frequency_map(self.config)
        if frequency_map is None:
            logger.info('no frequency data!')
            return False
        # map to image color range
        color_data = frequency_map / (MAX_DB / 256)
        data = color_data.astype(np.uint8)
        self.data_map = cv2.resize(data, (FEATURE_INPUT_SIZE, FEATURE_INPUT_SIZE))
        return True
