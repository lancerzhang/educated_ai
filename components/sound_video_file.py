from .sound import Sound
import audioread
import numpy as np
from . import util


class VideoFileSound(Sound):
    audio_buffers = None
    buf_seq = 0

    @util.timeit
    def __init__(self, brain, favor, video_file):
        self.CHUNK = 2048
        self.file_path = video_file
        self.frame_data = []
        self.frame_count = 0
        super(VideoFileSound, self).__init__(brain, favor)

    @util.timeit
    def open_video(self):
        audio = audioread.audio_open(self.file_path)
        self.audio_buffers = audio.read_data()
        # numbers of buffers were loaded
        self.buf_seq = 0

    @util.timeit
    def get_frequency_map(self, config):
        fps = config.video_fps
        # which frame is in current video
        frame = config.video_frame
        if frame == 1:
            self.open_video()
        # how long did video play
        video_duration = frame / fps
        # how long is a buffer
        buffer_duration = float(self.CHUNK) / self.SAMPLE_RATE
        # how much frames it should have loaded
        max_buf = int(video_duration / buffer_duration)
        while self.buf_seq <= max_buf:
            try:
                np_buffer = np.frombuffer(next(self.audio_buffers), dtype=np.int16)
                normal_buffer = util.normalize_audio_data(np_buffer)
                self.frame_data = self.frame_data + normal_buffer.tolist()
                self.buf_seq += 1
                self.frame_count += 1
                if self.frame_count >= self.buffer_count_of_phase:
                    # got enough data, save it to a phase
                    self.phases.append(self.frame_data)
                    self.frame_data = []
                    self.frame_count = 0
            except StopIteration:
                break
        return super(VideoFileSound, self).get_frequency_map(config)
