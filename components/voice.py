import collections
import logging
import math
import threading

import numpy as np

from components.recognizers import VoiceRecognizer
from . import util

logger = logging.getLogger('Sound')
logger.setLevel(logging.DEBUG)


class Voice(object):
    MAX_PHASE_DURATION = 0.2  # second of phase
    chunk = 0  # need to be overwrote
    sample_rate = 0  # need to be overwrote
    channels = 0  # need to be overwrote

    @util.timeit
    def __init__(self):
        self.running = True
        self.buffers_per_phase = 0
        self.phases = collections.deque()  # phases queue

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
        buffer_duration = float(self.chunk) / self.sample_rate
        self.buffers_per_phase = int(math.ceil(self.MAX_PHASE_DURATION / buffer_duration))

    @util.timeit
    def get_features(self):
        if len(self.phases) == 0:
            return []
        phase = self.phases.popleft()
        # print(f'len phase:{len(phase)}')
        phase = np.array(phase)
        mf = VoiceRecognizer(y=phase, sr=self.sample_rate)
        features = mf.features
        print(f'len features: {len(features)}')
        return features
