import time, numpy


def time_diff(start):
    return time.time() - start


def between(val, m, n):
    return m <= val <= n


# TODO, need to consider other audio format
# normalize audio data
def normalizeAudioData(raw):
    return raw / 32768.0  # assume 16 bit


# calculate energy
def rms(x):
    return numpy.sqrt(x.dot(x) / x.size)


# return common elements in 2 lists
def common_elements(list1, list2):
    return list(set(list1).intersection(list2))


# count each element in a list, return a dict, key is the element in list, value is count
def list_element_count(list1):
    return dict((a, list1.count(a)) for a in list1)


# list a - b, return new list
def comprehension_new(list1, list2):
    return [x for x in list1 if x not in list2]


def comprehension(list1, list2):
    tobe_remove=common_elements(list1,list2)
    for el1 in tobe_remove:
        list1.remove(el1)
