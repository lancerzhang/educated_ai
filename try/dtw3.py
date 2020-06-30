import librosa.display
from dtw import dtw
from numpy.linalg import norm

y1, sr1 = librosa.load('speech_dataset/yes/0a2b400e_nohash_0.wav')
y2, sr2 = librosa.load('speech_dataset/yes/0a2b400e_nohash_1.wav')
y3, sr3 = librosa.load('speech_dataset/no/0a2b400e_nohash_1.wav')


def compare_mfcc(y1, sr1, y2, sr2):
    print(f'start to compare')
    for i in range(12):
        mfcc1 = librosa.feature.mfcc(y1, sr1).T
        mfcc1 = mfcc1[:, i:i + 1]
        mfcc2 = librosa.feature.mfcc(y2, sr2).T
        mfcc2 = mfcc2[:, i:i + 1]
        dist, cost, acc_cost, path = dtw(mfcc1, mfcc2, dist=lambda x, y: norm(x - y, ord=1))
        print(f'mfcc feature {i} distance:', dist)


compare_mfcc(y1, sr1, y2, sr2)
compare_mfcc(y3, sr3, y2, sr2)
