import collections
import logging
import math
import threading

import numpy as np

from components.recognizers import MfccRecognizer
from . import util

logger = logging.getLogger('Sound')
logger.setLevel(logging.DEBUG)

DEFAULT_PHASE_DURATION = 0.2  # second of buffer


class Sound(object):
    running = True
    CHUNK = 0  # need to be overwrote
    SAMPLE_RATE = 0  # need to be overwrote
    CHANNELS = 0
    buffers_per_phase = 0
    phases = collections.deque()  # phases queue

    @util.timeit
    def __init__(self):
        self.frequency_map = None
        self.data_map = None

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

    # @util.timeit
    def process(self):
        return self.get_features()

    def set_chunk(self):
        buffer_duration = float(self.CHUNK) / self.SAMPLE_RATE
        self.buffers_per_phase = int(math.ceil(DEFAULT_PHASE_DURATION / buffer_duration))

    # @util.timeit
    def get_features(self):
        if len(self.phases) == 0:
            return []
        audio_data = np.array(list(self.phases)).flatten()
        # remove silence
        # print(f'len audio_data {len(audio_data)}')
        audio_data[abs(audio_data) < 0.05] = 0
        self.phases.clear()
        mf = MfccRecognizer(y=audio_data, sr=self.SAMPLE_RATE)
        features = mf.features
        return features
