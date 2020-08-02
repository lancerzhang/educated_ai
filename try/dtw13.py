import glob
import hashlib
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
from fastdtw import fastdtw
from numpy.linalg import norm
from scipy.spatial.distance import euclidean

np.set_printoptions(threshold=sys.maxsize)
DATABASE_PATH = 'speech_dataset'
SEARCH_FOLDER = 'yes'
# SEARCH_FOLDER = 'no'
# SEARCH_FOLDER = 'stop'
# SEARCH_FOLDER = 'nine'
SEARCH_FILE_NUM = 3
base_file = 'speech_dataset/yes/0a2b400e_nohash_0.wav_conv.npy'
feature_map_files = glob.glob(os.path.join(DATABASE_PATH, SEARCH_FOLDER, '*conv.npy'))
n_feature_map_files = len(feature_map_files)
base_feature_map = np.load(base_file)
batches = [3, 9, 99, 999]

MIN_FRAME = 2
MAX_FRAME = 5
MIN_ENERGY = 10


def manhattan_distance(x, y):
    return norm(x - y, ord=1)


def find_similar_dtw(section, feature_map2):
    for j in range(len(feature_map2)):
        for width in range(MIN_FRAME, MAX_FRAME + 1):
            if (j + width) > len(feature_map2):
                continue
            section2 = feature_map2[j:j + width]
            # distance, _, _, _ = dtw(section, section2, dist=manhattan_distance)
            distance, path = fastdtw(section, section2, dist=euclidean)
            energy = np.sum(np.abs(section))
            if distance < energy * 0.2:
                return distance


def find_common_conv_dtw(section, feature_index, batch_n):
    batch_num = batches[batch_n]
    files = feature_map_files[:batch_num]
    commons = []
    non_commons = []
    n_files = 0
    for file in files:
        if file == base_file:
            continue
        n_files += 1
        feature_map2 = np.load(file)
        feature_map2 = feature_map2[:, :, feature_index]
        result = find_similar_dtw(section, feature_map2)
        if result is not None:
            commons.append(result)
        else:
            non_commons.append(result)
        if len(non_commons) > n_feature_map_files * 0.2:
            print(
                f'section len {len(section)}, too many non commons, {len(commons)} commons, {len(non_commons)} non commons, skip this section')
            return
    n_common = len(commons)
    # print(f'batch_num:{batch_num} n_files:{n_files}')
    if n_common > n_files // 2:
        energy = np.sum(np.abs(section))
        b = section.view(np.uint8)
        b = hashlib.sha1(b).hexdigest()
        # print(section)
        print(f'{b}, feature_index {feature_index}, found {n_common} commons, energy {energy}')
        return True
    else:
        return False


def find_conv_tw(conv, frame_index):
    if (frame_index + (MIN_FRAME - 1)) >= len(conv):
        return
    temp_frames = [conv[frame_index]]
    if np.sum(np.abs(temp_frames)) < MIN_ENERGY:
        return
    wrappers = []
    for frame_index in range(frame_index + 1, len(conv)):
        if len(temp_frames) > MAX_FRAME:
            return wrappers
        next_frame = conv[frame_index]
        if np.sum(np.abs(next_frame)) < MIN_ENERGY:
            return wrappers
        temp_frames.append(next_frame)
        if len(temp_frames) < MIN_FRAME:
            continue
        wrappers.append(np.array(temp_frames))
    return wrappers


def find_common_conv_dtws(params):
    frame_n = params[0]
    batch_n = params[1]
    dtws = params[2]
    print(f'batch {batch_n} comparing frame {frame_n}')
    all_frame_dtws = []
    if batch_n == 0:
        for feature_index in range(64):
            feature_map = base_feature_map[:, :, feature_index]
            sections = find_conv_tw(feature_map, frame_n)
            if sections is None:
                continue
            for section in sections:
                is_common_dtws = find_common_conv_dtw(section, feature_index, batch_n)
                if is_common_dtws:
                    all_frame_dtws.append((section, feature_index))
        return all_frame_dtws
    else:
        for dtw in dtws:
            section = dtw[0]
            feature_index = dtw[1]
            is_common_dtws = find_common_conv_dtw(section, feature_index, batch_n)
            if is_common_dtws:
                all_frame_dtws.append((section, feature_index))
        return all_frame_dtws


if __name__ == '__main__':
    time1 = time.time()
    pool = Pool()
    batch_index = 0
    common_dtws = []
    for _ in batches:
        pool_params = []
        for i in range(len(base_feature_map)):
            pool_params.append((i, batch_index, common_dtws))
        all_dtws = pool.map(find_common_conv_dtws, pool_params)
        common_dtws = []
        dtw_hash_set = set()
        for ls in all_dtws:
            for item in ls:
                npa = np.append(item[0], item[1])
                npv = npa.view()
                nph = hashlib.sha1(npv).hexdigest()
                if nph not in dtw_hash_set:
                    common_dtws.append(item)
                    dtw_hash_set.add(nph)
        batch_index = batch_index + 1
        print(f'len of batch {batch_index} is {len(common_dtws)}')
        print(common_dtws)
    time2 = time.time()
    print(f'used time {time2 - time1}')
