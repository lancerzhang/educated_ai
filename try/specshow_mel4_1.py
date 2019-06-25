import librosa
import matplotlib.pyplot as plt
import librosa.display as dsp
import numpy as np

energy_threshold = 50
energy_width = 3


def rms(x):
    return np.sqrt(x.dot(x) / x.size)


y = np.load('hi1.npy')
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
        max_index = row.argmax(axis=0)
        feature_array = row >= max_energy
        feature_array[max_index - 1] = True
        feature_array[max_index - 2] = True
        feature_array[max_index + 1] = True
        feature_array[max_index + 2] = True
        energy_feature_array = row * feature_array
        idata[i] = energy_feature_array
        # print i, ' ', energy_feature_array
        print(i)
    i = i + 1

data = idata.transpose()

plt.figure(figsize=(10, 4))
librosa.display.specshow(librosa.power_to_db(mel_data, ref=np.max), y_axis='mel', fmax=8000, x_axis='time')
plt.colorbar(format='%+2.0f dB')
plt.title('Mel spectrogram')
plt.tight_layout()
plt.show()
