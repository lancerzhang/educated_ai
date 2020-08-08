import glob
import os
import time
from multiprocessing import Pool

import numpy as np
from scipy.spatial.distance import euclidean

base_file = 'speech_dataset/yes/0a2b400e_nohash_0.wav_mfcc.npy'
BLOCK_WIDTH = 2
BLOCK_HEIGHT = 2
MIN_ENERGY = 50
MIN_DISTANCE_UNIT = 0.1
DATABASE_PATH = 'speech_dataset'
SEARCH_FOLDER = 'yes'
mfcc_files = glob.glob(os.path.join(DATABASE_PATH, SEARCH_FOLDER, '*mfcc.npy'))
SEARCH_FILE_NUM = 999
n_mfcc_files = len(mfcc_files)
base_mfcc = np.load(base_file)
batches = [9, 99, 500]


def find_blocks(mfcc):
    mfcc = mfcc[:, 1:]
    # print(mfcc.astype(int))
    height, width = mfcc.shape
    # print(height)
    blocks = []
    for i in range(width - BLOCK_WIDTH + 1):
        for j in range(height - BLOCK_HEIGHT + 1):
            block = mfcc[j:j + BLOCK_HEIGHT, i:i + BLOCK_WIDTH]
            if np.sum(np.abs(block)) > MIN_ENERGY:
                norm_block = block / np.abs(block).max()
                blocks.append(norm_block)
    return blocks


def has_similar_dtw1(params):
    block1 = params[0]
    common_blocks = params[1]
    for block2 in common_blocks:
        distance = euclidean(block1[0], block2[0]) + euclidean(block1[1], block2[1])
        if distance < MIN_DISTANCE_UNIT * BLOCK_WIDTH * BLOCK_HEIGHT:
            return True
    return False


def has_similar_dtw2(params):
    block1 = params[0]
    file = params[1]
    all_blocks = find_blocks(np.load(file))
    for block2 in all_blocks:
        distance = euclidean(block1[0], block2[0]) + euclidean(block1[1], block2[1])
        if distance < MIN_DISTANCE_UNIT * BLOCK_WIDTH * BLOCK_HEIGHT:
            return True
    return False


def find_similar_blocks(mfcc_file):
    mfcc = np.load(mfcc_file)
    all_blocks = find_blocks(mfcc)
    similar_blocks = []
    for block in all_blocks:
        if not has_similar_dtw1([block, similar_blocks]):
            similar_blocks.append(block)
    return similar_blocks


def common_blocks_search(mfcc_file, old_common_blocks):
    mfcc = np.load(mfcc_file)
    all_blocks = find_blocks(mfcc)
    new_common_blocks = []
    for block in old_common_blocks:
        if has_similar_dtw1([block, all_blocks]):
            new_common_blocks.append(block)
    return new_common_blocks


if __name__ == '__main__':
    time1 = time.time()
    pool = Pool()
    all_common_blocks = find_similar_blocks(base_file)
    # all_common_blocks = np.load('common_blocks_yes.npy')
    print(len(all_common_blocks))
    non_common_blocks = []
    for i in range(len(batches)):
        print(f'start batch {i + 1}')
        new_common_blocks = []
        files_n = batches[i]
        files = mfcc_files[:files_n]
        for common_block in all_common_blocks:
            common_n = 0
            pool_params = []
            for file in files:
                pool_params.append([common_block, file])
            results = pool.map(has_similar_dtw2, pool_params)
            for result in results:
                if result:
                    common_n += 1
            # print(f'common_n {common_n}')
            # for file in files:
            #     all_blocks = find_blocks(np.load(file))
            #     if has_similar_dtw([common_block, all_blocks]):
            #         common_n += 1
            if common_n / files_n > 0.8:
                new_common_blocks.append(common_block)
            else:
                non_common_blocks.append(common_block)
        print(f'commons in batch {i + 1} is {len(new_common_blocks)}')
        print(f'non commons in batch {i + 1} is {len(non_common_blocks)}')
        all_common_blocks = new_common_blocks
    np.save(f'common_blocks_{SEARCH_FOLDER}', all_common_blocks)
    np.save(f'non_common_yes_{SEARCH_FOLDER}', non_common_blocks)
    time2 = time.time()
    print(f'used time {time2 - time1}')
