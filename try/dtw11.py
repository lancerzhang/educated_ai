import glob
import hashlib
import os
import time
from multiprocessing import Pool

import numpy as np
from dtw import dtw
from numpy.linalg import norm

DATABASE_PATH = 'speech_dataset'
# SEARCH_FOLDER = 'yes'
# SEARCH_FOLDER = 'no'
SEARCH_FOLDER = 'stop'
# SEARCH_FOLDER = 'nine'
SEARCH_FILE_NUM = 30
base_file = 'speech_dataset/no/0a2b400e_nohash_0.wav_mfcc.npy'
mfcc_files = glob.glob(os.path.join(DATABASE_PATH, SEARCH_FOLDER, '*mfcc.npy'))
n_mfcc_files = len(mfcc_files)
base_mfcc = np.load(base_file)
base_mfcc = base_mfcc[:, 1:]

MIN_FRAME = 2
MAX_FRAME = 5
MIN_ENERGY = 100


def manhattan_distance(x, y):
    return norm(x - y, ord=1)


def find_similar_dtw(section, mfcc2):
    for j in range(len(mfcc2) - len(section)):
        section2 = mfcc2[j:j + len(section)]
        distance, _, _, _ = dtw(section, section2, dist=manhattan_distance)
        energy = np.sum(np.abs(section))
        # print(distance)
        if distance < energy * 0.8:
            return distance


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


def find_common_mfcc_dtw(section):
    # files = files[:SEARCH_FILE_NUM]
    commons = []
    non_commons = []
    n_files = 0
    for file in mfcc_files:
        if file == base_file:
            continue
        n_files += 1
        mfcc2 = np.load(file)
        mfcc2 = mfcc2[:, 1:]
        result = find_similar_dtw(section, mfcc2)
        if result is not None:
            commons.append(result)
        else:
            non_commons.append(result)
        if len(non_commons) > n_mfcc_files * 0.1:
            # print(
            #     f'section len {len(section)}, too many non commons, {len(commons)} commons, {len(non_commons)} non commons, skip this section')
            return
    n_common = len(commons)
    if n_common > n_files // 2:
        energy = np.sum(np.abs(section))

        b = section.view(np.uint8)
        b = hashlib.sha1(b).hexdigest()
        print(section)
        print(f'{b}, found {n_common} commons, energy {energy}')


def find_common_mfcc_dtws(i):
    sections = find_mfcc_tw(i)
    if sections is None:
        return
    for section in sections:
        find_common_mfcc_dtw(section)


if __name__ == '__main__':
    time1 = time.time()
    pool = Pool()
    pool.map(find_common_mfcc_dtws, range(len(base_mfcc)))
    time2 = time.time()
    print(f'used time {time2 - time1}')
