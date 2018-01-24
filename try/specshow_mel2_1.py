import librosa
import matplotlib.pyplot as plt
import librosa.display as dsp
import numpy as np

energy_threshold = 50
energy_similar_time = 0.7


def rms(x):
    return np.sqrt(x.dot(x) / x.size)


y = np.load('hi2.npy')
mel_data = librosa.feature.melspectrogram(y=y, sr=44100, n_mels=128, fmax=8000)
idata = mel_data.transpose()

i = 0
for row in idata:
    rmse = rms(row)
    if rmse < energy_threshold:
        row.fill(0)
        # print i
    else:
        max_energy = row.max()
        similar_energy = max_energy * energy_similar_time
        feature_array = row >= similar_energy
        energy_feature_array = row * feature_array
        idata[i] = energy_feature_array
        # print i, ' ', energy_feature_array
        print i
    i = i + 1

data = idata.transpose()

plt.figure(figsize=(10, 4))
librosa.display.specshow(librosa.power_to_db(mel_data, ref=np.max), y_axis='mel', fmax=8000, x_axis='time')
plt.colorbar(format='%+2.0f dB')
plt.title('Mel spectrogram')
plt.tight_layout()
plt.show()
