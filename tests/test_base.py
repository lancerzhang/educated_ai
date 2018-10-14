import unittest, memory, copy,time
from db import Database
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

class TestUtil(unittest.TestCase):
    database = None

    def setUp(self):
        self.database = Database(TinyDB(storage=MemoryStorage))
        memory.forget_memory = False
        memory.db = self.database

    def test_sort(self):
        el1 = self.database.add_memory({memory.HAPPEN_TIME:1})
        el2 = self.database.add_memory({memory.HAPPEN_TIME:2})
        working_memories_arr = {}
        working_memories_arr.update({el1[memory.ID]:el1})
        working_memories_arr.update({el2[memory.ID]:el2})
        asc_list=[key for key,value in sorted(working_memories_arr.items(),key=lambda d: d[1][memory.HAPPEN_TIME],reverse=False)]
        happen_time=working_memories_arr.get(asc_list[0])[memory.HAPPEN_TIME]
        self.assertEqual(1,happen_time)
        reverse_list=[key for key,value in sorted(working_memories_arr.items(),key=lambda d: d[1][memory.HAPPEN_TIME],reverse=True)]
        happen_time=working_memories_arr.get(reverse_list[0])[memory.HAPPEN_TIME]
        self.assertEqual(2, happen_time)




if __name__ == "__main__":
    unittest.main()
