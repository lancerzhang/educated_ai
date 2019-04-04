from components import constants
import numpy as np
from components.data_adaptor import DataAdaptor
from components.data_CodernityDB import DataCodernityDB

data_service = DataAdaptor(DataCodernityDB(folder='../data/CodernityDB/'))


def count_memories():
    all_memories = data_service.get_all_memories()
    return len(all_memories)


def list_top_memories(field1, key1, value1, limit=20):
    all_memories = data_service.get_all_memories()
    if key1:
        all_memories = [x for x in all_memories if key1 in x]
    if value1:
        all_memories = [x for x in all_memories if x[key1] == value1]
    sorted_all_memories = sorted(all_memories, key=lambda x: (x[field1]), reverse=True)
    return sorted_all_memories[0:limit]


def list_top_sub_memories(key, limit=20):
    all_memories = data_service.get_all_memories()
    sorted_all_memories = sorted(all_memories, key=lambda x: (len(x[key])), reverse=True)
    return sorted_all_memories[0:limit]


def list_physical_memories():
    all_memories = data_service.get_all_memories()
    for mem in all_memories:
        if constants.PHYSICAL_MEMORY_TYPE in mem:
            print mem





def print_used_data():
    # print 'used vision kernels is {0}'.format(np.load('../data/vuk.npy'))
    # print 'used vision speed is {0}'.format(np.load('../data/vus.npy'))
    # print 'used vision degrees is {0}'.format(np.load('../data/vud.npy'))
    print 'used sound kernels is {0}'.format(np.load('../data/suk.npy'))


print count_memories()

field1 = constants.RECALL_COUNT
key1 = constants.PHYSICAL_MEMORY_TYPE
# value1 = constants.VISION_FEATURE
value1 = constants.SOUND_FEATURE
# key1 = constants.VIRTUAL_MEMORY_TYPE
# key1 = None
# value1 = None
# field = constants.REWARD
# memories = list_top_memories(field1, constants.PHYSICAL_MEMORY_TYPE, constants.VISION_FEATURE, 50)
# print [x[field1] for x in memories]
#
# memories = list_top_memories(field1, constants.PHYSICAL_MEMORY_TYPE, constants.SOUND_FEATURE, 50)
# print [x[field1] for x in memories]
#
# memories = list_top_memories(field1, constants.VIRTUAL_MEMORY_TYPE, None, 10)
# print memories

# field = constants.CHILD_MEM
# memories = list_top_sub_memories(field, 20)
# print [len(x[field]) for x in memories]

print data_service.get_memory('ffe7de23616843769f4aa7c814457e0a')
# data_service.display_bm_tree('2d2ba99853734e208e415635298c7b54')
# print_used_data()