import time

import audioread
import numpy as np

from . import util
from .sound import Sound


class VideoFileSound(Sound):
    NFRAMES = 0
    DURATION = 0
    buffer_duration = 0
    play_start_time = 0
    read_time = 0
    audio_buffers = None
    read_buffer_total_count = 0
    read_buffer_phase_count = 0
    frame_data = []

    @util.timeit
    def __init__(self, file_path):
        self.file_path = file_path
        self.open_video()
        # detect chunk size
        self.read_a_buffer()
        self.set_chunk()
        super(VideoFileSound, self).__init__()

    @util.timeit
    def open_video(self):
        audio = audioread.audio_open(self.file_path)
        self.SAMPLE_RATE = audio.samplerate
        self.CHANNELS = audio.channels
        self.NFRAMES = audio.nframes
        self.DURATION = audio.duration
        self.audio_buffers = audio.read_data()
        # numbers of buffers were loaded
        self.read_buffer_total_count = 0
        self.read_buffer_phase_count = 0
        self.read_time = 0
        self.play_start_time = time.time()

    @util.timeit
    def read_a_buffer(self):
        buf = next(self.audio_buffers)
        if self.CHANNELS == 2:
            buf = np.reshape(bytearray(buf), (-1, 2))
            buf = buf[::2].flatten()
        np_buffer = np.frombuffer(buf, dtype=np.int16)
        if self.CHUNK == 0:
            self.CHUNK = len(np_buffer)
            # how long is a buffer
            self.buffer_duration = float(self.CHUNK) / self.SAMPLE_RATE
        self.read_time += self.buffer_duration
        normal_buffer = util.normalize_audio_data(np_buffer)
        self.frame_data = self.frame_data + normal_buffer.tolist()
        self.read_buffer_total_count += 1
        self.read_buffer_phase_count += 1

    @util.timeit
    def process_a_buffer(self):
        self.read_a_buffer()
        if self.read_buffer_phase_count >= self.buffers_per_phase:
            # got enough data, save it to a phase
            self.phases.append(self.frame_data)
            self.frame_data = []
            self.read_buffer_phase_count = 0

    @util.timeit
    def receive(self):
        while self.running:
            # print(f'receive start')
            # print(f' len frame_data {len(self.frame_data)}')
            # print(f' len phases {len(self.phases)}')
            # print(f'read_time {self.read_time}')
            # print(f'DURATION {self.DURATION}')
            # if self.read_time >= self.DURATION:
            #     self.read_time = 0
            #     self.play_start_time = 0
            #     print(f'restart video')
            #     continue
            playing_time = time.time() - self.play_start_time
            while self.read_time < playing_time:
                try:
                    self.process_a_buffer()
                except StopIteration:
                    print(f'replay video')
                    self.open_video()
                    break
            # avoid looping too fast, that eat processing power of main thread
            time.sleep(self.buffer_duration / 2)
