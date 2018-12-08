import util, constants
from data_service import DataService
from db_CodernityDB import DB_CodernityDB

data_service = DataService(DB_CodernityDB(folder='data/CodernityDB/'))
all_memories = data_service.get_all_memories()
print str(len(all_memories)) + ' memories'

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
