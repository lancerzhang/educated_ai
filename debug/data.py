from components import constants
import numpy as np
from components.data_adaptor import DataAdaptor
from components.data_CodernityDB import DataCodernityDB

data_service = DataAdaptor(DataCodernityDB(folder='../data/CodernityDB/'))


def count_memories():
    all_memories = data_service.get_all_memories()
    return len(all_memories)


def list_top_memories(field, limit=20):
    all_memories = data_service.get_all_memories()
    sorted_all_memories = sorted(all_memories, key=lambda x: (x[field]), reverse=True)
    return sorted_all_memories[0:limit]


def list_top_sub_memories(field, limit=20):
    all_memories = data_service.get_all_memories()
    sorted_all_memories = sorted(all_memories, key=lambda x: (len(x[field])), reverse=True)
    return sorted_all_memories[0:limit]


def list_physical_memories():
    all_memories = data_service.get_all_memories()
    for mem in all_memories:
        if constants.PHYSICAL_MEMORY_TYPE in mem:
            print mem


def print_used_data():
    print 'used kernels is {0}'.format(np.load('../data/vuk.npy'))
    print 'used speed is {0}'.format(np.load('../data/vus.npy'))
    print 'used degrees is {0}'.format(np.load('../data/vud.npy'))


print count_memories()

# field = constants.RECALL_COUNT
# field = constants.REWARD
# memories = list_top_memories(field, 50)
# print [x[field] for x in memories]

# field = constants.CHILD_MEM
# memories = list_top_sub_memories(field, 20)
# print [len(x[field]) for x in memories]

# print data_service.get_memory('d2b375ed4eef4ae2a8ba5087059c799a')

# print_used_data()
# data_service.db.db.compact()
all_memories = data_service.get_all_memories()
memories = [bm for bm in all_memories if
            constants.PHYSICAL_MEMORY_TYPE in bm and bm[constants.PHYSICAL_MEMORY_TYPE] == constants.SOUND_FEATURE]
print len(memories)
