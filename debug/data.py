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


def load_short_id():
    print np.load('../data/sid.npy')


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
# print memories
#
memories = list_top_memories(field1, constants.PHYSICAL_MEMORY_TYPE, constants.SOUND_FEATURE, 50)
print [x[field1] for x in memories]
#
# memories = list_top_memories(field1, constants.VIRTUAL_MEMORY_TYPE, None, 10)
# print memories

# field = constants.CHILD_MEM
# memories = list_top_sub_memories(field, 20)
# print [len(x[field]) for x in memories]

# print data_service.get_memory('da605430f6ec4bc99cc53c24825ea44d')
# print data_service.get_mouse_click_memory(constants.LEFT_CLICK)
# data_service.display_bm_tree_leaf('f99815a369bf4b99af854be4e1c8e390', 0, 15)
# print_used_data()
# load_short_id()
