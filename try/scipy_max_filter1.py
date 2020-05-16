import numpy as np
from scipy import ndimage

arr = [[3, 4, 5, 2, 3],
       [3, 5, 1, 2, 7],
       [2, 2, 5, 6, 7]]

out = arr * (arr == ndimage.maximum_filter(arr, footprint=np.ones((3, 3))))

print(out)
