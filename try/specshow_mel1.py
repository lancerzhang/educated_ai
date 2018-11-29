import librosa
import matplotlib.pyplot as plt
import librosa.display as dsp
import numpy as np

y = np.load('sound3_1.npy')
# start = 35360
# length = 1024 * 15
# data = y[start:start + length]
# np.save('sound3_1.npy', data)
mmin=np.min(y)
mmax=np.max(y)
print mmax
print mmin
mel_data = librosa.feature.melspectrogram(y=y, sr=44100, n_mels=128, fmax=8000)
plt.figure(figsize=(8, 4))
librosa.display.specshow(librosa.power_to_db(mel_data, ref=np.max), y_axis='mel', fmax=8000, x_axis='time')
plt.colorbar(format='%+2.0f dB')
plt.title('Mel spectrogram')
plt.tight_layout()
plt.show()
