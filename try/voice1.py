import _thread
import time

import librosa
import librosa.display as dsp
import matplotlib.pyplot as plt
import numpy as np

from src import speech

_thread.start_new_thread(speech.receive, ())

try:
    while 1:
        time.sleep(0.2)
        if len(speech.phases) > 3:
            break

except KeyboardInterrupt:
    speech.start_thread = False
    print("quiting...")

print('got phase ', len(speech.phases))
data = np.concatenate(speech.phases)
mel_data = librosa.feature.melspectrogram(y=data, sr=44100, n_mels=128, fmax=8000)
plt.figure(figsize=(6, 4))
librosa.display.specshow(librosa.power_to_db(mel_data, ref=np.max), y_axis='mel', fmax=8000, x_axis='time')
plt.colorbar(format='%+2.0f dB')
plt.title('Mel spectrogram')
plt.tight_layout()
plt.show()
