import numpy as np

from src import constants

data_service = DataAdaptor(DataSqlite3('../data/dump.sql'))


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
            print(mem)


def print_used_data():
    # print 'used vision kernels is {0}'.format(np.load('../data/vuk.npy'))
    # print 'used vision speed is {0}'.format(np.load('../data/vus.npy'))
    # print 'used vision degrees is {0}'.format(np.load('../data/vud.npy'))
    print('used sound kernels is {0}'.format(np.load('../data/suk.npy')))


def load_short_id():
    print(np.load('../data/sid.npy'))


print(count_memories())

field1 = constants.RECALL_COUNT
key1 = constants.PHYSICAL_MEMORY_TYPE
# value1 = constants.VISION_FEATURE
value1 = constants.SOUND_FEATURE
# key1 = constants.VIRTUAL_MEMORY_TYPE
# key1 = None
# value1 = None
# field = constants.REWARD
memories = list_top_memories(field1, constants.PHYSICAL_MEMORY_TYPE, constants.VISION_FEATURE, 50)
print([x[field1] for x in memories])
memories = list_top_memories(field1, constants.PHYSICAL_MEMORY_TYPE, constants.SOUND_FEATURE, 50)
print([x[field1] for x in memories])
memories = list_top_memories(field1, constants.VIRTUAL_MEMORY_TYPE, None, 50)
print([x[field1] for x in memories])

# field = constants.CHILD_MEM
# memories = list_top_sub_memories(field, 20)
# print [len(x[field]) for x in memories]

# print data_service.get_mouse_click_memory(constants.LEFT_CLICK)
# print data_service.get_memory('22197af12f3344fca23dd17844617912')
# data_service.display_bm_tree_leaf('7efd1bda06364a28a265f4efb2d00ddd', 0, 5)
roots = []
# data_service.find_bm_tree_roots('b51333e7aabc40d9904b9527dd047fac',roots)
# print roots
# print_used_data()
# load_short_id()
# memoris=['b51333e7aabc40d9904b9527dd047fac', 'e2640996f41946c2aa7230a9a3ba5c60', '469f64505da743e581890c1f2062b420', 'f013049055ec4cd6b0c8f7affe3e96e5', '168620e5cbdf4e6caf563b034e5de0f8', 'b35503c3ebd94f7883b860c7c12c96b9', 'a376b516fbf04ca28a87301168e3649e', 'd6aadc78e04f47b3b1b95b905c94c319', '673da552aac94fc5bc62e1bf8ff4978e', '1c10110c27a44a9d88547a79364687af', '2f962a923fc345bab8ae86976c7358f8', '86ee8d51479d41968de5e3c457961a24', 'e48804af41664ae79b123f42bf8aa413']
# for m in memoris:
#     print data_service.get_memory(m)
# data_service.db.search_all('select * from bm where mod(_id)=1')
