# 1 second = 86.5 mel frames
# find max energy position
# expend the width to 3, add tolerance
# detect if it elapse more than 3 frames, if yes, save to memory
# next time, can detect if has such activation
# if recall many times, can explore more features

import librosa, io, math, audioop, collections, time
import speech_recognition as sr
import matplotlib.pyplot as plt
import librosa.display as dsp
import soundfile as sf
import numpy as np
from speech_recognition import AudioData

r = sr.Recognizer()
m = sr.Microphone()
energy_threshold = 2000  # minimum audio energy to consider for recording
sound_threshold = 1.0

try:
    with m as source:
        r.adjust_for_ambient_noise(source)
    while True:
        print 'start to listen'
        with m as source:
            phrase_count = 0
            frame_data = []

            while True:
                buffer = source.stream.read(source.CHUNK)
                if len(buffer) == 0: break  # reached end of the stream
                # detect whether speaking has started on audio input
                energy = audioop.rms(buffer, source.SAMPLE_WIDTH)  # energy of the audio signal
                if energy > energy_threshold:
                    np_buffer = np.fromstring(buffer, dtype=np.int16)
                    frame_data.append(np_buffer)
                    phrase_count += 1
                    break

            seconds_per_buffer = float(source.CHUNK) / source.SAMPLE_RATE
            buffer_count = int(math.ceil(sound_threshold / seconds_per_buffer))
            while True:
                buffer = source.stream.read(source.CHUNK)
                if len(buffer) == 0: break  # reached end of the stream
                np_buffer = np.fromstring(buffer, dtype=np.int16)
                frame_data.append(np_buffer)
                phrase_count += 1
                if phrase_count >= buffer_count:
                    break

            npArr = np.array(frame_data)
            y = npArr.flatten()
            mel_data = librosa.feature.melspectrogram(y=y, sr=source.SAMPLE_RATE, n_mels=128, fmax=8000)
            plt.figure(figsize=(10, 4))
            librosa.display.specshow(librosa.power_to_db(mel_data, ref=np.max), y_axis='mel', fmax=8000, x_axis='time')
            plt.colorbar(format='%+2.0f dB')
            plt.title('Mel spectrogram')
            plt.tight_layout()
            plt.show()


except KeyboardInterrupt:
    pass
