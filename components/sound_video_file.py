from sound import Sound
import audioread
import constants
import logging
import numpy as np
import util


class VideoFileSound(Sound):
    audio_buffers = None
    buf_seq = 0
    CHUNK = 2048

    def __init__(self, bm, video_file, video_file_info):
        self.file_path = video_file
        self.video_info = video_file_info
        super(VideoFileSound, self).__init__(bm)

    def open_video(self):
        audio = audioread.audio_open(self.file_path)
        self.audio_buffers = audio.read_data()
        self.buf_seq = 0

    def get_frequency_map(self):
        logging.info('get_frequency_map')
        frame_data = []
        frame = self.video_info[constants.current_frame]
        fps = self.video_info[constants.fps]
        if frame == 1:
            self.open_video()
        video_duration = frame / fps
        buffer_duration = float(self.CHUNK) / self.SAMPLE_RATE
        max_buf = int(video_duration / buffer_duration)
        while self.buf_seq <= max_buf:
            try:
                np_buffer = np.fromstring(self.audio_buffers.next(), dtype=np.int16)
                normal_buffer = util.normalize_audio_data(np_buffer)
                frame_data = frame_data + normal_buffer.tolist()
                self.buf_seq = self.buf_seq + 1
            except StopIteration:
                break
        self.phases.append(frame_data)
        return super(VideoFileSound, self).get_frequency_map()
