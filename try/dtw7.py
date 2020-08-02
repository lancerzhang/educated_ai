import glob
import os
import time
from multiprocessing import Pool

import numpy as np
from numpy.linalg import norm

DATABASE_PATH = 'speech_dataset'
SEARCH_FOLDER = 'no'
SEARCH_FILE_NUM = 20
base_file = 'speech_dataset/yes/0a2b400e_nohash_0.wav_mfcc.npy'

base_mfcc = np.load(base_file)
base_mfcc = base_mfcc[:, 1:]

n_peak = 1


def manhattan_distance(x, y):
    return norm(x - y, ord=1)


def sort_similar_mfcc_vector(i, peak_indices, v1_peek, mfcc2):
    distances = []
    for j in range(len(mfcc2)):
        v2_peek = mfcc2[j][peak_indices]
        distance = manhattan_distance(v1_peek, v2_peek)
        energy = np.sum(np.abs(v2_peek))
        if energy > 50 * n_peak:
            distances.append((i, j, peak_indices, int(distance), int(energy), v1_peek, v2_peek))
    distances = sorted(distances, key=lambda x: x[3])
    if len(distances) > 0:
        min_d = distances[0]
        if min_d[3] < 10 * n_peak:
            return min_d


def find_similar_mfcc_vector(i, peak_indices, v1_peek, mfcc2):
    for j in range(len(mfcc2)):
        v2_peek = mfcc2[j][peak_indices]
        distance = manhattan_distance(v1_peek, v2_peek)
        energy = np.sum(np.abs(v2_peek))
        if energy > 50 * n_peak and distance < energy // 10:
            return i, j, peak_indices, int(distance), int(energy), v1_peek, v2_peek


def find_common_mfcc_vector(i):
    v1 = base_mfcc[i]
    v1abs = np.abs(v1)
    peak_indices = sorted(np.argpartition(v1abs, -n_peak)[-n_peak:])
    v1_peek = v1[peak_indices]
    files = glob.glob(os.path.join(DATABASE_PATH, SEARCH_FOLDER, '*mfcc.npy'))
    # files = files[:SEARCH_FILE_NUM]
    n_files = 0
    vectors = []
    for file in files:
        if file == base_file:
            continue
        n_files += 1
        # print(f'comparing {file}')
        mfcc2 = np.load(file)
        mfcc2 = mfcc2[:, 1:]
        vector = find_similar_mfcc_vector(i, peak_indices, v1_peek, mfcc2)
        if vector is not None:
            # print(f'found similar vector in {file}, {vector}')
            vectors.append(vector)
    n_common = len(vectors)
    return f'{i} vector found {n_common} common'


if __name__ == '__main__':
    time1 = time.time()
    pool = Pool()
    similar_vectors = pool.map(find_common_mfcc_vector, range(len(base_mfcc)))
    for r in similar_vectors:
        print(r)
    time2 = time.time()
    print(f'used time {time2 - time1}')
