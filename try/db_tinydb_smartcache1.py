from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from tinydb_smartcache import SmartCacheTable

db = TinyDB(storage=MemoryStorage)
db.table_class = SmartCacheTable
table = db.table('Memory')
# below is a memory, which can be a Q(s,a)
docId1 = table.insert({'strength': 100, 'type': 'memory', 'recall': 1, 'reward': 1, 'lastRecall': 20180106, 'children': [123, 123]})
docId2 = table.insert({'strength': 100, 'type': 'vision', 'recall': 1, 'reward': 1, 'lastRecall': 20180106, 'filter': 'vf1', 'data': 'abc'})
table.insert({'strength': 99, 'type': 'sound', 'recall': 1, 'reward': 1, 'lastRecall': 20180106, 'data': '123'})
table.insert({'strength': 99, 'type': 'move_vision', 'recall': 1, 'reward': 1, 'lastRecall': 20180106, 'angle': 10, 'speed': 10, 'duration': 10})
table.insert({'strength': 99, 'type': 'speak', 'recall': 1, 'reward': 1, 'lastRecall': 20180106, 'word': 'yes'})

Memory = Query()
print(table.search(Memory.strength == 100))
print(table.search(Memory.strength == 100 and Memory.type == 'vision'))
docs = table.search(Memory.strength == 100 and Memory.type == 'vision')
print(docId1, ' ', docId2)
print(docs[0].doc_id)
doc = table.get(Memory.strength == 100 and Memory.type == 'vision')
print(doc.doc_id)
