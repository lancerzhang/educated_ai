import cv2
import librosa
import librosa.display as dsp
import matplotlib.pyplot as plt
import numpy as np

# edge detection
filter1 = np.array([[1, 0, -1],
                    [0, 0, 0],
                    [-1, 0, 1]])

filter2 = np.array([[-1, 0, 1],
                    [0, 0, 0],
                    [1, 0, -1]])

# black
filter3 = np.array([[-1, -1, 0],
                    [0, -1, -1],
                    [1, 0, 0]])
# blur
filter4 = np.array([[0.11, 0.11, 0.11],
                    [0.11, 0.11, 0.11],
                    [0.11, 0.11, 0.11]])

filter5 = np.array([[0.5, 0.5, 0.5],
                    [0.5, 0.5, 0.5],
                    [0.5, 0.5, 0.5]])

filter6 = np.array([[0.11, 0.11, 0.11, 0.11, 0.11],
                    [0.11, 0.11, 0.11, 0.11, 0.11],
                    [0.11, 0.11, 0.11, 0.11, 0.11],
                    [0.11, 0.11, 0.11, 0.11, 0.11],
                    [0.11, 0.11, 0.11, 0.11, 0.11]])

y = np.load('hi1.npy')
mel_data = librosa.feature.melspectrogram(y=y, sr=44100, n_mels=128, fmax=8000)
cov = cv2.filter2D(mel_data, -1, filter4)
plt.figure(figsize=(8, 4))
librosa.display.specshow(librosa.power_to_db(cov, ref=np.max), y_axis='mel', fmax=8000, x_axis='time')
plt.colorbar(format='%+2.0f dB')
plt.title('Mel spectrogram')
plt.tight_layout()
plt.show()
