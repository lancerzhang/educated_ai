import time

import librosa
import numpy as np
from dtw import dtw
from numpy.linalg import norm

y1, sr1 = librosa.load('speech_dataset/yes/0a2b400e_nohash_0.wav')
y2, sr2 = librosa.load('speech_dataset/yes/0a2b400e_nohash_1.wav')
# y2, sr2 = librosa.load('speech_dataset/no/0a2b400e_nohash_1.wav')
base_mfcc = librosa.feature.mfcc(y1, sr1, n_mfcc=13).T[:, 1:]
mfcc2 = librosa.feature.mfcc(y2, sr2, n_mfcc=13).T[:, 1:]

MIN_FRAME = 2
MAX_FRAME = 5
MIN_ENERGY = 100


# print(base_mfcc.astype(int))
# print(mfcc2.astype(int))

def manhattan_distance(x, y):
    d = norm(x - y, ord=1)
    return d


def find_mfcc_tw(i):
    if (i + (MIN_FRAME - 1)) >= len(base_mfcc):
        return
    temp_frames = [base_mfcc[i]]
    if np.sum(np.abs(temp_frames)) < MIN_ENERGY:
        return
    wrappers = []
    for j in range(i + 1, len(base_mfcc)):
        if len(temp_frames) >= MAX_FRAME:
            return wrappers
        next_frame = base_mfcc[j]
        if np.sum(np.abs(next_frame)) < MIN_ENERGY:
            return wrappers
        temp_frames.append(next_frame)
        if len(temp_frames) < MIN_FRAME:
            continue
        wrappers.append(np.array(temp_frames).astype(int))
    return wrappers


def find_similar_dtw(section, i):
    for j in range(len(mfcc2) - len(section)):
        section2 = mfcc2[j:j + len(section)]
        section2 = section2.astype(int)
        distance, _, _, _ = dtw(section, section2, dist=manhattan_distance)
        distance = int(distance)
        energy = np.sum(np.abs(section))
        ratio = distance / energy
        # print(f' {i} {j} {distance} {energy} {ratio} ')
        if distance < energy * 0.4:
            print(f' {i} {j} {distance} {ratio} \ns1\n{section} \ns2\n {section2}')
            return distance, energy, ratio


def find_common_mfcc_dtws(i):
    sections = find_mfcc_tw(i)
    if sections is None:
        return []
    distances = []
    for section in sections:
        distance = find_similar_dtw(section, i)
        if distance is not None:
            distances.append((len(section), distance[0], distance[1], distance[2]))
    return distances


if __name__ == '__main__':
    time1 = time.time()
    total_distances = []
    for i in range(len(base_mfcc)):
        sub_distances = find_common_mfcc_dtws(i)
        total_distances = total_distances + sub_distances
    sorted_distances = sorted(total_distances, key=lambda x: x[3], reverse=True)
    for d in sorted_distances:
        print(f'len {d[0]}, distance {d[1]}, energy {d[2]}, ratio {d[3]}')
    time2 = time.time()
    print(f'used time {time2 - time1}')
