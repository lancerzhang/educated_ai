import librosa,time
import matplotlib.pyplot as plt
import librosa.display as dsp
import numpy as np
import cv2


y = np.load('hi1.npy')
mel_data = librosa.feature.melspectrogram(y=y, sr=44100, n_mels=128, fmax=8000)

times = 100

plt.figure(figsize=(8, 4))

try:
    while times > 0:
        times = times - 1
        print(times)
        filter = np.random.choice([-1, 0, 1], (3, 3))
        print(filter)
        cov = cv2.filter2D(mel_data, -1, filter)
        librosa.display.specshow(librosa.power_to_db(cov, ref=np.max), y_axis='mel', fmax=8000, x_axis='time')
        plt.colorbar(format='%+2.0f dB')
        plt.title('Mel spectrogram')
        plt.tight_layout()
        plt.show()

except KeyboardInterrupt:
    cv2.destroyAllWindows()

cv2.waitKey(0)
cv2.destroyAllWindows()

