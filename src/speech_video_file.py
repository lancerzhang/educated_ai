import logging
import time

import audioread
import numpy as np

from . import util
from .speech import Speech

logger = logging.getLogger('VideoFileSpeech')
logger.setLevel(logging.DEBUG)


class VideoFileSpeech(Speech):

    @util.timeit
    def __init__(self, file_path):
        self.file_path = file_path
        self.duration = 0
        self.buffer_duration = 0
        self.play_start_time = 0
        self.read_time = 0
        self.audio_buffers = None
        self.phase_is_start = False
        self.phase_start_time = 0
        self.phase_data = []
        self.open_video()
        # detect chunk size
        self.read_a_buffer()
        self.set_chunk()
        super(VideoFileSpeech, self).__init__()

    @util.timeit
    def open_video(self):
        audio = audioread.audio_open(self.file_path)
        self.sample_rate = audio.samplerate
        self.channels = audio.channels
        self.duration = audio.duration
        self.audio_buffers = audio.read_data()
        self.read_time = 0
        self.play_start_time = time.time()

    @util.timeit
    def read_a_buffer(self):
        buf = next(self.audio_buffers)
        if self.channels == 2:
            buf = np.reshape(bytearray(buf), (-1, 2))
            buf = buf[::2].flatten()
        np_buffer = np.frombuffer(buf, dtype=np.int16)
        if self.chunk == 0:
            self.chunk = len(np_buffer)
            # how long is a buffer
            self.buffer_duration = float(self.chunk) / self.sample_rate
        self.read_time += self.buffer_duration
        normal_buffer = util.normalize_audio_data(np_buffer)
        return normal_buffer

    @util.timeit
    def process_a_buffer(self):
        np_buffer = self.read_a_buffer()
        np_buffer = np_buffer.copy()
        np_buffer[abs(np_buffer) < 0.05] = 0
        abs_sum_abs_buffer = np.abs(np.sum(np_buffer))
        if self.phase_is_start:
            if abs_sum_abs_buffer > 0:
                self.phase_data = self.phase_data + np_buffer.tolist()
                if (time.time() - self.phase_start_time) > self.MAX_PHASE_DURATION:
                    # force to stop a phase when gather enough data
                    self.stop_phase()
            else:
                # phase stop, save it to a phase
                self.stop_phase()
        else:
            if abs_sum_abs_buffer > 0:
                # start a new phase
                self.phase_data = self.phase_data + np_buffer.tolist()
                self.phase_is_start = True
                self.phase_start_time = time.time()

    def stop_phase(self):
        self.phase_is_start = False
        self.phases.append(self.phase_data)
        self.phase_data = []

    @util.timeit
    def receive(self):
        while self.running:
            playing_time = time.time() - self.play_start_time
            while self.read_time < playing_time:
                try:
                    self.process_a_buffer()
                except StopIteration:
                    logger.debug(f'replay video')
                    self.open_video()
                    break
            # avoid looping too fast, that eat processing power of main thread
            time.sleep(self.buffer_duration / 2)
