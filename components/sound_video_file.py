import audioread
import numpy as np

from . import util
from .sound import Sound


class VideoFileSound(Sound):
    audio_buffers = None
    read_buffer_total_count = 0
    read_buffer_phase_count = 0
    frame_data = []

    @util.timeit
    def __init__(self, brain, config, file_path):
        self.config = config
        self.CHUNK = 1024
        self.file_path = file_path
        super(VideoFileSound, self).__init__(brain)

    @util.timeit
    def open_video(self):
        audio = audioread.audio_open(self.file_path)
        self.SAMPLE_RATE = audio.samplerate
        self.CHANNELS = audio.channels
        self.audio_buffers = audio.read_data()
        # numbers of buffers were loaded
        self.read_buffer_total_count = 0
        self.read_buffer_phase_count = 0

    def read_data(self):
        buf = next(self.audio_buffers)
        if self.CHANNELS == 2:
            buf = np.reshape(bytearray(buf), (-1, 2))
            buf = buf[::2].flatten()
        np_buffer = np.frombuffer(buf, dtype=np.int16)
        self.CHUNK = len(np_buffer)
        normal_buffer = util.normalize_audio_data(np_buffer)
        self.frame_data = self.frame_data + normal_buffer.tolist()
        self.read_buffer_total_count += 1
        self.read_buffer_phase_count += 1
        if self.read_buffer_phase_count >= self.buffers_per_phase:
            # got enough data, save it to a phase
            self.phases.append(self.frame_data)
            self.frame_data = []
            self.read_buffer_phase_count = 0

    @util.timeit
    def receive_data(self):
        fps = self.config["video"]["fps"]
        frame_count = self.config["video"]["frame_count"]
        # which frame is in current video
        play_frame = self.config["video"]["play_frame"]
        if play_frame == 1:
            self.open_video()
        # how long did video play
        video_duration = play_frame / fps
        # how long is a buffer
        buffer_duration = float(self.CHUNK) / self.SAMPLE_RATE
        # how much frames it should have loaded
        total_buffer_count = int(video_duration / buffer_duration)
        while self.read_buffer_total_count < total_buffer_count:
            try:
                self.read_data()
            except StopIteration:
                break
        return True
