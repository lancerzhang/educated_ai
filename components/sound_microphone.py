import logging

import numpy as np
import pyaudio

from . import util
from .sound import Sound

logger = logging.getLogger('MicrophoneSound')
logger.setLevel(logging.INFO)


class MicrophoneSound(Sound):
    running = True
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    MAX_PHASES = 5  # max phases storage

    @util.timeit
    def __init__(self, brain, favor):
        self.CHUNK = 1024
        super(MicrophoneSound, self).__init__(brain, favor)

    @util.timeit
    def receive(self):
        try:
            audio = pyaudio.PyAudio()
            stream = audio.open(format=self.FORMAT,
                                channels=self.CHANNELS,
                                rate=self.SAMPLE_RATE,
                                input=True,
                                frames_per_buffer=self.CHUNK)
            while self.running:
                frame_count = 0
                frame_data = []
                # start to record
                while True:
                    audio_buffer = stream.read(self.CHUNK)
                    if len(audio_buffer) == 0:
                        break  # reached end of the stream
                    np_buffer = np.frombuffer(audio_buffer, dtype=np.int16)
                    normal_buffer = util.normalize_audio_data(np_buffer)
                    frame_data = frame_data + normal_buffer.tolist()
                    frame_count += 1
                    if frame_count >= self.buffer_count_of_phase:
                        break

                # reach buffer threshold, save it as phase
                if len(self.phases) > self.MAX_PHASES:
                    # ignore non-process phase
                    self.phases.popleft()
                self.phases.append(frame_data)
        except IOError:
            raise Exception('Please connect your microphone!')
