import _thread
import time

import librosa
import librosa.display as dsp
import matplotlib.pyplot as plt
import numpy as np

from components import sound

_thread.start_new_thread(sound.receive, ())

try:
    while 1:
        time.sleep(0.2)
        if len(sound.phases) > 3:
            break

except KeyboardInterrupt:
    sound.start_thread = False
    print("quiting...")

print('got phase ', len(sound.phases))
data = np.concatenate(sound.phases)
mel_data = librosa.feature.melspectrogram(y=data, sr=44100, n_mels=128, fmax=8000)
plt.figure(figsize=(6, 4))
librosa.display.specshow(librosa.power_to_db(mel_data, ref=np.max), y_axis='mel', fmax=8000, x_axis='time')
plt.colorbar(format='%+2.0f dB')
plt.title('Mel spectrogram')
plt.tight_layout()
plt.show()
