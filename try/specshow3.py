import librosa
import matplotlib.pyplot as plt
import librosa.display as dsp
import numpy as np

na = None
for i in range(1, 70):
    print(i)
    fn = '../spec/{0}.npy'.format(i)
    nd = np.load(fn)
    if na is None:
        na = nd
    else:
        na = np.concatenate((na, nd), axis=0)

mel_data = librosa.feature.melspectrogram(y=na, sr=44100, n_mels=20, hop_length=512, fmax=8000)
plt.figure(figsize=(12, 4))
# na=librosa.power_to_db(na)
librosa.display.specshow(librosa.power_to_db(mel_data, ref=np.max), y_axis='mel', x_axis='time')
plt.colorbar(format='%+2.0f dB')
plt.title('Mel spectrogram')
plt.tight_layout()
plt.show()
