import constants
import numpy as np
import util
from data_adaptor import DataAdaptor
from db_CodernityDB import DB_CodernityDB

data_service = DataAdaptor(DB_CodernityDB(folder='../data/CodernityDB/'))


def count_memories():
    all_memories = data_service.get_all_memories()
    return len(all_memories)


def list_top_memories(field, limit=20):
    all_memories = data_service.get_all_memories()
    sorted_all_memories = sorted(all_memories, key=lambda x: (x[field]), reverse=True)
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
# memories = list_top_memories(field)
# print [x[field] for x in memories]
print data_service.get_memory('3979da8538a542b08891cc9a80170e3c')

print_used_data()
# kernel = np.load('../data/vuk.npy')
# print util.np_array_group_by_count([x['knl'] for x in kernel])
