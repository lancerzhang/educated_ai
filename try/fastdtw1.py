import numpy as np
from fastdtw import fastdtw
from numpy.linalg import norm


def manhattan_distance(x, y):
    d = norm(x - y, ord=1)
    return d


x = np.array([[1, 1, 1], [1, 1, 0]])
y = np.array([[1, 1, 1], [0, 0, 0]])
distance, path = fastdtw(x, y, dist=manhattan_distance)
print(distance)
