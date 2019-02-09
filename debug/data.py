import constants
import numpy as np
import util
from data_adaptor import DataAdaptor
from data_CodernityDB import DataCodernityDB

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


# print count_memories()
field = constants.RECALL
# field = constants.REWARD
# memories = list_top_memories(field,50)
field = constants.PARENT_MEM
memories = list_top_sub_memories(field, 50)
print [len(x[field]) for x in memories]
# print data_service.get_memory('6df897947e1d45eb8913bbc0af7ab5b2')

# print_used_data()
