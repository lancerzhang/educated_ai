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
        first=True
        first_time=0
        for key,value in working_memories_arr.items():
            if first:
                first_time=value[memory.HAPPEN_TIME]
        self.assertEqual(1,first_time)




if __name__ == "__main__":
    unittest.main()
