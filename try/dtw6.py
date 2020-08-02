import time

import librosa
import numpy as np
from numpy.linalg import norm

y1, sr1 = librosa.load('speech_dataset/yes/0a2b400e_nohash_0.wav')
y2, sr2 = librosa.load('speech_dataset/no/0a2b400e_nohash_0.wav')


# y2, sr2 = librosa.load('speech_dataset/no/0a2b400e_nohash_1.wav')


def manhattan_distance(x, y):
    d = norm(x - y, ord=1)
    return d


time1 = time.time()
distances = []
mfcc1 = librosa.feature.mfcc(y1, sr1, n_mfcc=13).T[:, 1:]
mfcc2 = librosa.feature.mfcc(y2, sr2, n_mfcc=13).T[:, 1:]
for i in range(len(mfcc1)):
    v1 = mfcc1[i]
    v1abs = np.abs(v1)
    n_peak = 2
    peak_indices = sorted(np.argpartition(v1abs, -n_peak)[-n_peak:])
    v1_peek = v1[peak_indices]
    for j in range(len(mfcc2)):
        v2_peek = mfcc2[j][peak_indices]
        distance = int(manhattan_distance(v1_peek, v2_peek))
        energy = int(np.sum(np.abs(v2_peek)))
        if energy > 100 and distance<20:
            distances.append((i, j, peak_indices, distance, energy, v1_peek, v2_peek))
distances = sorted(distances, key=lambda x: x[3], reverse=True)
time2 = time.time()
# print(f'min distance:{distances[0]}')
for d in distances:
    print(f'd:{d}')
print(f'used time {time2 - time1}')
