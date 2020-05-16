import librosa
import librosa.display as dsp
import matplotlib.pyplot as plt
import numpy as np

y = np.load('hi1.npy')
mfccs = librosa.feature.mfcc(y, sr=44100)
plt.figure(figsize=(10, 4))
dsp.specshow(mfccs, x_axis='time')
plt.colorbar()
plt.title('MFCC')
plt.tight_layout()
plt.show()
