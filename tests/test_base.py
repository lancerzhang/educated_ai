import unittest
from components import constants, bio_memory
from components.data_adaptor import DataAdaptor
from tinydb import TinyDB
from tinydb.storages import MemoryStorage
from components.data_tinydb import DataTinyDB


class TestUtil(unittest.TestCase):
    data = None
    database = None

    def setUp(self):
        database = DataTinyDB(TinyDB(storage=MemoryStorage))
        self.data = DataAdaptor(database)
        bio_memory.forget_memory = False
        bio_memory.data_adaptor = self.data

    def test_sort(self):
        el1 = self.data.add_memory({constants.HAPPEN_TIME: 1})
        el2 = self.data.add_memory({constants.HAPPEN_TIME: 2})
        working_memories_arr = {}
        working_memories_arr.update({el1[constants.MID]: el1})
        working_memories_arr.update({el2[constants.MID]: el2})
        asc_list = [key for key, value in
                    sorted(list(working_memories_arr.items()), key=lambda d: d[1][constants.HAPPEN_TIME], reverse=False)]
        happen_time = working_memories_arr.get(asc_list[0])[constants.HAPPEN_TIME]
        self.assertEqual(1, happen_time)
        reverse_list = [key for key, value in
                        sorted(list(working_memories_arr.items()), key=lambda d: d[1][constants.HAPPEN_TIME], reverse=True)]
        happen_time = working_memories_arr.get(reverse_list[0])[constants.HAPPEN_TIME]
        self.assertEqual(2, happen_time)


if __name__ == "__main__":
    unittest.main()
