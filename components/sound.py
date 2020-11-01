import collections
import logging
import math

import numpy as np

from components.recognizer import MfccRecognizer
from . import util
from .brain import Brain

logger = logging.getLogger('Sound')
logger.setLevel(logging.INFO)

MAX_FREQUENCY = 8000
ENERGY_THRESHOLD = 250  # minimum audio energy to consider for processing
DEFAULT_PHASE_DURATION = 0.2  # second of buffer

FREQUENCY_MAP_HEIGHT = 13
HOP_LENGTH = 512
FEATURE_INPUT_SIZE = 12
FEATURE_THRESHOLD = 10
FEATURE_SIMILARITY_THRESHOLD = 0.2
POOL_BLOCK_SIZE = 2  # after down-sampling, feature is 3x3
SOUND_KERNEL_FILE = 'kernels.npy'
MAX_DB = 80.0


class Sound(object):
    CHUNK = 64  # for UT only
    SAMPLE_RATE = 44100
    CHANNELS = 1
    phases = collections.deque()  # phases queue

    @util.timeit
    def __init__(self, brain: Brain):
        self.brain = brain
        self.frequency_map = None
        buffer_duration = float(self.CHUNK) / self.SAMPLE_RATE
        self.buffers_per_phase = int(math.ceil(DEFAULT_PHASE_DURATION / buffer_duration))
        self.data_map = None
        # self.pool = Pool()

    @util.timeit
    def process(self):
        self.receive_data()
        self.get_features()

    @util.timeit
    def get_features(self):
        while len(self.phases) > 0:
            print(f'len(self.phases):{len(self.phases)}')
            audio_data = np.array(list(self.phases)).flatten()
            # remove silence
            audio_data[abs(audio_data) < 0.05] = 0
            self.phases.clear()
            # self.data_map = librosa.feature.mfcc(y=audio_data, sr=self.SAMPLE_RATE, n_mfcc=FREQUENCY_MAP_HEIGHT).T
            mf = MfccRecognizer(y=audio_data, sr=self.SAMPLE_RATE)
            data_map = mf.features
            print(f'found features:{len(data_map)}')
            # for feature in data_map:
            #     print(feature)
