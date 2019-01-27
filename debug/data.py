import util, constants
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


# print count_memories()
field = constants.RECALL
# field = constants.REWARD
# memories = list_top_memories(field)
# print [x[field] for x in memories]
print data_service.get_memory('46f1ac1dcb694f0780ca9d497e6e85d2')
