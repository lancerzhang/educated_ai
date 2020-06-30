import glob
import os

import librosa
import numpy as np

# https://github.com/pierre-rouanet/dtw/blob/master/examples/speech-recognition.ipynb

DATABASE_PATH = 'speech_dataset'
labels = {'cat', 'dog', 'house', 'happy', 'zero'}
N = 25

mfccs = []
true_labels = []

for l in labels:
    sounds = glob.glob(os.path.join(DATABASE_PATH, l, '*.wav'))
    np.random.shuffle(sounds)
    sounds = sounds[:N]

    for s in sounds:
        y, sr = librosa.load(s)
        mfcc = librosa.feature.mfcc(y, sr, n_mfcc=13).T
        mfcc1 = mfcc[:, 1:]
        mfccs.append(mfcc)
        true_labels.append(l)

mfccs = np.array(mfccs)
true_labels = np.array(true_labels)

val_percent = 0.2
n_val = int(val_percent * len(true_labels))

I = np.random.permutation(len(true_labels))
I_val, I_train = I[:n_val], I[n_val:]

from dtw import dtw


def cross_validation(train_indices, val_indices):
    score = 0.0

    for i in val_indices:
        x = mfccs[i]

        dmin, jmin = np.inf, -1
        for j in train_indices:
            y = mfccs[j]
            d, _, _, _ = dtw(x, y, dist=lambda x, y: np.linalg.norm(x - y, ord=1))

            if d < dmin:
                dmin = d
                jmin = j

        score += 1.0 if (true_labels[i] == true_labels[jmin]) else 0.0

    return score / len(val_indices)


rec_rate = cross_validation(I_train, I_val)
print('Recognition rate {}%'.format(100. * rec_rate))
