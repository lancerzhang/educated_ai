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
base_file = 'speech_dataset/yes/0a2b400e_nohash_0.wav_mfcc.npy'

base_mfcc = np.load(base_file)
base_mfcc = base_mfcc[:, 1:]
frame_masks = []
for frame in base_mfcc:
    abs_frame = np.abs(frame)
    peak = np.max(abs_frame)
    frame_masks.append(np.where(abs_frame == peak, 1, 0))
print(base_mfcc.astype(int))
MIN_FRAME = 2
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


def find_mfcc_tw(i):
    if (i + (MIN_FRAME - 1)) >= len(frame_masks):
        return
    temp_masks = [frame_masks[i]]
    temp_frames = [base_mfcc[i] * frame_masks[i]]
    if np.sum(np.abs(temp_frames)) < MIN_ENERGY:
        return
    wrappers = []
    for j in range(i + 1, len(frame_masks)):
        if len(temp_frames) >= MAX_FRAME:
            return wrappers
        next_frame = base_mfcc[j] * frame_masks[j]
        if np.sum(np.abs(next_frame)) < MIN_ENERGY:
            return wrappers
        temp_masks.append(frame_masks[j])
        temp_frames.append(next_frame)
        if len(temp_frames) < MIN_FRAME:
            continue
        wrappers.append((np.array(temp_masks), np.array(temp_frames).astype(int)))
    return wrappers


def find_common_mfcc_dtw(i):
    wrappers = find_mfcc_tw(i)
    if wrappers is None:
        return
    for wrapper in wrappers:
        files = glob.glob(os.path.join(DATABASE_PATH, SEARCH_FOLDER, '*mfcc.npy'))
        files = files[:SEARCH_FILE_NUM]
        commons = []
        n_files = 0
        for file in files:
            if file == base_file:
                continue
            n_files += 1
            mfcc2 = np.load(file)
            mfcc2 = mfcc2[:, 1:]
            result = find_similar_dtw(wrapper, mfcc2)
            if result is not None:
                commons.append(result)
        n_common = len(commons)
        if n_common > n_files // 2:
            value1 = wrapper[1]
            energy = np.sum(np.abs(value1))

            b = value1.view(np.uint8)
            b = hashlib.sha1(b).hexdigest()
            # print(wrapper[0])
            # print(wrapper[1])
            print(f'{b} len: {len(value1)}, found {n_common} commons, energy {energy}')


if __name__ == '__main__':
    time1 = time.time()
    pool = Pool()
    pool.map(find_common_mfcc_dtw, range(len(frame_masks)))
    time2 = time.time()
    print(f'used time {time2 - time1}')
