import librosa
import matplotlib.pyplot as plt
import librosa.display as dsp
import numpy as np
from scipy import signal

y = np.load('hi2.npy')
mel_data = librosa.feature.melspectrogram(y=y, sr=44100, n_mels=128, fmax=8000)
v=np.array([
    [1,1,1],
    [1,1,1],
    [1,1,1]
])
grad = signal.convolve2d(mel_data, v, boundary='symm', mode='same')
plt.figure(figsize=(10, 4))
librosa.display.specshow(librosa.power_to_db(grad, ref=np.max), y_axis='mel', fmax=8000, x_axis='time')
plt.colorbar(format='%+2.0f dB')
plt.title('Mel spectrogram')
plt.tight_layout()
plt.show()
