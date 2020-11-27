import _thread
import time

import librosa
import librosa.display as dsp
import matplotlib.pyplot as plt
import numpy as np

from src import voice

_thread.start_new_thread(voice.receive, ())

try:
    while 1:
        time.sleep(0.2)
        if len(voice.phases) > 3:
            break

except KeyboardInterrupt:
    voice.start_thread = False
    print("quiting...")

print('got phase ', len(voice.phases))
data = np.concatenate(voice.phases)
mel_data = librosa.feature.melspectrogram(y=data, sr=44100, n_mels=128, fmax=8000)
plt.figure(figsize=(6, 4))
librosa.display.specshow(librosa.power_to_db(mel_data, ref=np.max), y_axis='mel', fmax=8000, x_axis='time')
plt.colorbar(format='%+2.0f dB')
plt.title('Mel spectrogram')
plt.tight_layout()
plt.show()
