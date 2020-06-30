import librosa.display
import matplotlib.pyplot as plt
from dtw import dtw
from matplotlib import cm
from numpy.linalg import norm

y1, sr1 = librosa.load('speech_dataset/yes/0a2b400e_nohash_0.wav')
y2, sr2 = librosa.load('speech_dataset/yes/5e3b7a84_nohash_0.wav')


def manhattan_distance(x, y):
    # print(f'x:{x}')
    # print(f'y:{y}')
    d = norm(x - y, ord=1)
    # print(f'd:{d}')
    return d


ax1 = plt.subplot(1, 3, 1)
mfcc1 = librosa.feature.mfcc(y1, sr1).T
print(mfcc1.shape)
ax1.imshow(mfcc1, interpolation='nearest', cmap=cm.coolwarm, origin='lower')

ax2 = plt.subplot(1, 3, 2)
mfcc2 = librosa.feature.mfcc(y2, sr2).T
ax2.imshow(mfcc2, interpolation='nearest', cmap=cm.coolwarm, origin='lower')

# mfcc1 = mfcc1.T[:, 1:]
# mfcc2 = mfcc2.T[:, 1:]
dist, cost, acc_cost, path = dtw(mfcc1, mfcc2, dist=manhattan_distance)
print('Normalized distance between the two sounds:', dist)
# print(f'cost:{cost}')
# print(f'acc_cost:{acc_cost}')
# print(f'path:{path}')
ax3 = plt.subplot(1, 3, 3)
ax3.imshow(cost.T, origin='lower', cmap=cm.gray, interpolation='nearest')
plt.plot(path[0], path[1], 'w')
plt.xlim((-0.5, cost.shape[0] - 0.5))
plt.ylim((-0.5, cost.shape[1] - 0.5))
plt.show()
