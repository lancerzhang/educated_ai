import numpy as np
from components import util

dict={}
filters = []
for p1 in range(1,3):
    for p2 in range(1,3):
        for p3 in range(1,3):
            for p4 in range(1,3):
                for p5 in range(1,3):
                    for p6 in range(1,3):
                        for p7 in range(1,3):
                            for p8 in range(1,3):
                                for p9 in range(1,3):
                                    # count = count + 1
                                    # print count
                                    filter = np.array([[p1 - 1, p2 - 1, p3 - 1], [p4 - 1, p5 - 1, p6 - 1], [p7 - 1, p8 - 1, p9 - 1]])
                                    arr2= util.delete_empty_surround(filter)
                                    arr1=arr2.flatten()
                                    str=np.array_str(arr1)
                                    if not dict.has_key(str):
                                        dict.update({str:0})
                                        filters.append(arr2)
                                        print arr2

print len(filters)