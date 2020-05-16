import librosa
import librosa.display as dsp
import matplotlib.pyplot as plt
import numpy as np

y1 = np.load('data1.npy')
y2 = np.load('data2.npy')
y3 = np.load('data3.npy')
y4 = np.load('data4.npy')
y5 = np.load('data5.npy')
y6 = np.load('data6.npy')

y = np.concatenate((y1, y2, y3, y4, y5, y6), axis=0)
mel_data = librosa.feature.melspectrogram(y=y, sr=44100, n_mels=128, fmax=8000)
plt.figure(figsize=(12, 4))
librosa.display.specshow(librosa.power_to_db(mel_data, ref=np.max), y_axis='mel', fmax=8000, x_axis='time')
plt.colorbar(format='%+2.0f dB')
plt.title('Mel spectrogram')
plt.tight_layout()
plt.show()
