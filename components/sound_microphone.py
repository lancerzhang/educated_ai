from sound import Sound
import logging
import math
import numpy as np
import pyaudio
import util


class MicrophoneSound(Sound):
    start_thread = True
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    MAX_PHASES = 5  # max phases storage
    DEFAULT_PHASE_DURATION = 0.2  # second of buffer

    def __init__(self, bm):
        super(MicrophoneSound, self).__init__(bm)

    def receive(self, phase_duration=DEFAULT_PHASE_DURATION):
        logging.info('start to receive sound data.')
        try:
            audio = pyaudio.PyAudio()
            stream = audio.open(format=self.FORMAT,
                                channels=self.CHANNELS,
                                rate=self.SAMPLE_RATE,
                                input=True,
                                frames_per_buffer=self.CHUNK)
            while self.start_thread:
                frame_count = 0
                frame_data = []
                buffer_duration = float(self.CHUNK) / self.SAMPLE_RATE
                buffer_count_of_phase = int(math.ceil(phase_duration / buffer_duration))

                # start to record
                while True:
                    audio_buffer = stream.read(self.CHUNK)
                    if len(audio_buffer) == 0:
                        break  # reached end of the stream
                    np_buffer = np.fromstring(audio_buffer, dtype=np.int16)
                    normal_buffer = util.normalize_audio_data(np_buffer)
                    frame_data = frame_data + normal_buffer.tolist()
                    frame_count += 1
                    if frame_count >= buffer_count_of_phase:
                        break

                # reach buffer threshold, save it as phase
                if len(self.phases) > self.MAX_PHASES:
                    # ignore non-process phase
                    self.phases.popleft()
                self.phases.append(frame_data)
        except IOError:
            raise Exception('Please connect your microphone!')
