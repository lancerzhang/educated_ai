import glob
import hashlib
import os
import time
from multiprocessing import Pool

import numpy as np
from dtw import dtw
from numpy.linalg import norm

DATABASE_PATH = 'speech_dataset'
SEARCH_FOLDER = 'yes'
SEARCH_FILE_NUM = 30

section_masks = np.array([
    [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
    [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
])
sections = np.array([
    np.array([[128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 101, 0, 0, 0, 0, 0, 0, 0, 0, 0]]),
    np.array([[128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 101, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 107, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
])
MIN_FRAME = 3
MAX_FRAME = 5
MIN_ENERGY = 100


def manhattan_distance(x, y):
    return norm(x - y, ord=1)


def find_similar_dtw(wrapper, mfcc2):
    section_mask = wrapper[0]
    section = wrapper[1]
    for j in range(len(mfcc2) - len(section_mask)):
        section2 = mfcc2[j:j + len(section_mask)] * section_mask
        distance, _, _, _ = dtw(section, section2, dist=manhattan_distance)
        energy = np.sum(np.abs(section))
        if distance < energy * 0.15:
            return distance


def find_common_mfcc_dtw(i):
    section_mask = section_masks[i]
    section = sections[i]
    wrapper = (section_mask, section)
    files = glob.glob(os.path.join(DATABASE_PATH, SEARCH_FOLDER, '*mfcc.npy'))
    # files = files[:SEARCH_FILE_NUM]
    commons = []
    n_files = 0
    for file in files:
        n_files += 1
        mfcc2 = np.load(file)
        mfcc2 = mfcc2[:, 1:]
        result = find_similar_dtw(wrapper, mfcc2)
        if result is not None:
            commons.append(result)
    n_common = len(commons)
    energy = np.sum(np.abs(section))
    b = section.view(np.uint8)
    b = hashlib.sha1(b).hexdigest()
    print(f'{b} len: {len(section)}, found {n_common} commons, energy {energy}')


if __name__ == '__main__':
    time1 = time.time()
    pool = Pool()
    pool.map(find_common_mfcc_dtw, range(len(section_masks)))
    time2 = time.time()
    print(f'used time {time2 - time1}')
