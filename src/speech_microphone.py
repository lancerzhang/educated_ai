import logging
import time

import numpy as np
import pyaudio

from . import util
from .speech import Speech

logger = logging.getLogger('MicrophoneSpeech')
logger.setLevel(logging.INFO)


class MicrophoneSpeech(Speech):
    FORMAT = pyaudio.paInt16

    @util.timeit
    def __init__(self, brain, favor):
        self.chunk = 1024
        self.channels = 1
        self.max_phases = 5  # max phases storage
        super(MicrophoneSpeech, self).__init__(brain, favor)

    @util.timeit
    def receive(self):
        try:
            audio = pyaudio.PyAudio()
            stream = audio.open(format=self.FORMAT,
                                channels=self.channels,
                                rate=self.sample_rate,
                                input=True,
                                frames_per_buffer=self.chunk)
            while self.running:
                frame_count = 0
                frame_data = []
                # start to record
                while True:
                    audio_buffer = stream.read(self.chunk)
                    if len(audio_buffer) == 0:
                        break  # reached end of the stream
                    np_buffer = np.frombuffer(audio_buffer, dtype=np.int16)
                    normal_buffer = util.normalize_audio_data(np_buffer)
                    frame_data = frame_data + normal_buffer.tolist()
                    frame_count += 1
                    if frame_count >= self.buffers_per_phase:
                        break

                # reach buffer threshold, save it as phase
                if len(self.phases) > self.max_phases:
                    # ignore non-process phase
                    self.phases.popleft()
                self.phases.append(frame_data)
                # avoid looping too fast, that eat processing power of main thread
                time.sleep(0.01)
        except IOError:
            raise Exception('Please connect your microphone!')
