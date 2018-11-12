import numpy as np
import random

nFilters=np.load("vision_kernels90.npy")

def getFilter():
    shape=nFilters.shape
    index=random.randint(0, shape[0]-1)
    return _getFilter(index)

def _getFilter(index):
    return nFilters[index]