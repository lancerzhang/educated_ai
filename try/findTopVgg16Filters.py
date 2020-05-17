import collections
import pickle

"""
take 6 sample images
below filters looks have contour from human being
<row>.<column>
"""
arr = [2.1, 2.4, 2.5
    , 3.1, 3.2, 3.4
    , 4.4, 4.5, 4.6
    , 5.1
    , 6.1, 6.7
    , 7.5
    , 8.4

    , 2.5
    , 3.1, 3.4
    , 4.4, 4.6, 4.8
    , 5.1
    , 6.1, 6.7
    , 7.5
    , 8.6

    , 2.4, 2.5
    , 3.1, 3.4
    , 4.4, 4.5, 4.6, 4.8
    , 6.1, 6.7
    , 7.5
    , 8.4, 86

    , 2.1, 2.5, 2.7, 2.8
    , 3.1, 3.2, 3.4
    , 4.4
    , 5.1
    , 6.4, 6.7
    , 7.5, 7.6
    , 8.4, 8.6

    , 2.1, 2.8
    , 3.3, 3.4
    , 4.4, 4.6, 4.8
    , 5.1, 5.3, 5.8
    , 7.5
    , 8.4

    , 3.4
    , 4.4, 4.6
    , 5.1
    , 6.7
    , 7.5, 7.6]

print(collections.Counter(arr))
"""
result is below
3.4: 6,
4.4: 6,
7.5: 6,
4.6: 5,
5.1: 5,
6.7: 5,

2.5: 4, 
3.1: 4, 
8.4: 4, 
2.1: 3, 
6.1: 3, 
4.8: 3,
"""

# map to filter index
idxs = [(2 * 8 + 4 - 1), (3 * 8 + 4 - 1), (6 * 8 + 5 - 1), (3 * 8 + 6 - 1), (4 * 8 + 1 - 1), (5 * 8 + 7 - 1),
        (1 * 8 + 5 - 1), (2 * 8 + 1 - 1), (7 * 8 + 4 - 1)]
# same those filters
with open('vgg16.l1.filters', 'rb') as filters:
    vgg16_filters = pickle.load(filters)
ls = []
for idx in idxs:
    ls.append(vgg16_filters[:, :, :, idx])
print(ls)
file = open('vgg16.l1.top.filters', 'wb')
pickle.dump(ls, file)
