import matplotlib.pyplot as plt
import numpy as np
from numpy.linalg import norm

# We define two sequences x, y as numpy array
# where y is actually a sub-sequence from x
x = np.array([[1, 1], [2, 2], [2, 2]])
y = np.array([[2, 2], [2, 2]])
print(x)
print(y)
from dtw import dtw


def manhattan_distance(x, y):
    print(f'x:{x}')
    print(f'y:{y}')
    d = norm(x - y, ord=1)
    print(f'd:{d}')
    return d


d, cost_matrix, acc_cost_matrix, path = dtw(x, y, dist=manhattan_distance)

print(f'final d:{d}')
print(f'cost_matrix:{cost_matrix}')
print(f'acc_cost_matrix:{acc_cost_matrix}')
print(f'path:{path}')

# You can also visualise the accumulated cost and the shortest path

print(acc_cost_matrix.T)
print(path)
plt.imshow(acc_cost_matrix.T, origin='lower', cmap='gray')
plt.plot(path[0], path[1], 'w')
plt.show()
