import collections
import logging
import math
import threading

import numpy as np

from src.recognizers import VoiceRecognizer
from . import util

logger = logging.getLogger('Voice')
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
        logger.error('receive() not implemented!')
        return

    # @util.timeit
    def process(self):
        return self.get_features_serial()

    def set_chunk(self):
        buffer_duration = float(self.chunk) / self.sample_rate
        self.buffers_per_phase = int(math.ceil(self.MAX_PHASE_DURATION / buffer_duration))

    @util.timeit
    def get_features_serial(self):
        if len(self.phases) == 0:
            return []
        # get voice data of a phase, which max duration is Voice.MAX_PHASE_DURATION
        phase = self.phases.popleft()
        # print(f'len phase:{len(phase)}')
        phase = np.array(phase)
        mf = VoiceRecognizer(y=phase, sr=self.sample_rate)
        features = mf.features
        logger.debug(f'len features: {len(features)}')
        # for feature in features:
        #     print(f'len feature: {len(feature)}')
        return features
