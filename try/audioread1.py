import audioread, librosa
import numpy as np
from components import util
import matplotlib.pyplot as plt
import librosa.display as dsp

RATE = 44100
i = 0
frame_data = []
duration = 17
buf_size = 2048
buf_time = float(buf_size) / RATE
buf_no = int(duration / buf_time)
print(buf_no)
f = audioread.audio_open('../train/1440.mp4')
print((f.channels, f.samplerate, f.duration))

# for buf in f:
bufs = f.read_data()
while i < buf_no + 100:
    try:
        print(i)
        np_buffer = np.frombuffer(next(bufs), dtype=np.int16)
        normal_buffer = util.normalize_audio_data(np_buffer)
        frame_data = frame_data + normal_buffer.tolist()
        i = i + 1
    except StopIteration:
        break

# for buf in f:
#     if i < buf_no:
#         np_buffer = np.fromstring(buf, dtype=np.int16)
#         normal_buffer = util.normalize_audio_data(np_buffer)
#         frame_data = frame_data + normal_buffer.tolist()
#         i = i + 1

mel_data = librosa.feature.melspectrogram(y=np.array(frame_data), sr=RATE, n_mels=128, fmax=8000)
plt.figure(figsize=(10, 4))
librosa.display.specshow(librosa.power_to_db(mel_data, ref=np.max), y_axis='mel', fmax=8000, x_axis='time')
plt.colorbar(format='%+2.0f dB')
plt.title('Mel spectrogram')
plt.tight_layout()
plt.show()
