# 1 second = 86.5 mel frames
# find max energy position
# expend the width to 3, add tolerance
# detect if it elapse more than 3 frames, if yes, save to memory
# next time, can detect if has such activation
# if recall many times, can explore more features

import math, audioop, pyaudio
from components import util
import numpy as np

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE = 44100
SAMPLE_WIDTH = 2  # 16-bit
energy_threshold = 2000  # minimum audio energy to consider for recording
buffer_threshold = 0.3  # second of buffer

try:
    file_ser = 1
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=SAMPLE_RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
    while True:
        print 'start to listen'
        frame_count = 0
        frame_data = []
        seconds_per_buffer = float(CHUNK) / SAMPLE_RATE
        buffer_count = int(math.ceil(buffer_threshold / seconds_per_buffer))

        # do nothing until frame energy reach threshold
        while True:
            buffer = stream.read(CHUNK)
            if len(buffer) == 0: break  # reached end of the stream
            # detect whether speaking has started on audio input
            energy = audioop.rms(buffer, SAMPLE_WIDTH)  # energy of the audio signal
            if energy > energy_threshold:
                # save the frame
                np_buffer = np.fromstring(buffer, dtype=np.int16)
                normal_buffer = util.normalize_audio_data(np_buffer)
                frame_data.append(normal_buffer)
                frame_count += 1
                break

        # start to record
        while True:
            buffer = stream.read(CHUNK)
            if len(buffer) == 0: break  # reached end of the stream
            np_buffer = np.fromstring(buffer, dtype=np.int16)
            normal_buffer = util.normalize_audio_data(np_buffer)
            frame_data.append(normal_buffer)
            frame_count += 1
            if frame_count >= buffer_count:
                break

        # reach buffer threshold, start to process
        npArr = np.array(frame_data)
        y = npArr.flatten()
        # mel_data = librosa.feature.melspectrogram(y=y, sr=SAMPLE_RATE, n_mels=128, fmax=8000)
        # plt.figure(figsize=(10, 4))
        # librosa.display.specshow(librosa.power_to_db(mel_data, ref=np.max), y_axis='mel', fmax=8000, x_axis='time')
        # plt.colorbar(format='%+2.0f dB')
        # plt.title('Mel spectrogram')
        # plt.tight_layout()
        # plt.savefig('chart' + str(file_ser) + '.png')
        np.save('data' + str(file_ser) + '.npy',y)
        file_ser += 1
        # plt.show()


except KeyboardInterrupt:
    pass
