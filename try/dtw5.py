import glob
import os
from multiprocessing import Pool

import librosa
import numpy as np
from dtw import dtw
from numpy.linalg import norm
import time

DATABASE_PATH = 'speech_dataset'
labels = {'nine'}


def save_mfcc(s):
    y, sr = librosa.load(s)
    mfcc = librosa.feature.mfcc(y, sr, n_mfcc=13).T
    np.save(f'{s}_mfcc', mfcc)


def save_mfccs():
    for l in labels:
        sounds = glob.glob(os.path.join(DATABASE_PATH, l, '*.wav'))
        pool = Pool()
        pool.map(save_mfcc, sounds)


def compare():
    base = np.load('speech_dataset/yes/0a2b400e_nohash_0.wav_mfcc.npy')
    base = base[:, 1:]
    for l in labels:
        files = glob.glob(os.path.join(DATABASE_PATH, l, '*.npy'))
        files = files[:25]
        for file in files:
            print(f'comparing to {file}')
            mfcc = np.load(file)
            mfcc = mfcc[:, 1:]
            dist, cost, acc_cost, path = dtw(base, mfcc, dist=lambda x, y: norm(x - y, ord=1))
            print(dist)


if __name__ == '__main__':
    time1 = time.time()
    save_mfccs()
    # compare()
    time2 = time.time()
    print(f'used time {time2 - time1}')

