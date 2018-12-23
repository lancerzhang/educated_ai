import util, constants
from data_adaptor import DataAdaptor
from db_CodernityDB import DB_CodernityDB

data_service = DataAdaptor(DB_CodernityDB(folder='data/CodernityDB/'))

data_service.full_housekeep()

data_service.cleanup_fields()

all_memories = data_service.get_all_memories()
sorted_all_memories = sorted(all_memories, key=lambda x: (x[constants.RECALL]), reverse=True)
print sorted_all_memories[0:20]

# print str(len(all_memories)) + ' memories'
# for mem in all_memories:
#     if len(mem[constants.PARENT_MEM])>400:
#         print mem
# print data_service.get_memory('8e86de49fd2e44e88a014829a063ec2c')
# count=0
# a1=['60c71f26728f47e4880ed6f54501dbd9', '60c71f26728f47e4880ed6f54501dbd9']
# for mem in all_memories:
#     if util.list_equal(mem[constants.CHILD_MEM],a1):
#         count=count+1
# print count

# field1 = constants.PARENT_MEM
# print str(data_service.find_duplication(field1)) + ' are equal in field ' + field1

# field2 = constants.CHILD_MEM
# print str(data_service.find_duplication(field2)) + ' are equal in field ' + field2
