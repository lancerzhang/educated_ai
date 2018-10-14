import unittest, memory, sound, time, copy
from db import Database
from tinydb import TinyDB
from tinydb.storages import MemoryStorage
from tinydb.database import Document


class TestMemory(unittest.TestCase):
    database = None

    def setUp(self):
        self.database = Database(TinyDB(storage=MemoryStorage))
        memory.forget_memory = False
        memory.db = self.database

    def test_associate_slice_empty(self):
        memories = []
        result = memory.split_seq_time_memories(memories)
        self.assertEqual(0, len(result[memory.NEW_MEMORIES]))
        self.assertEqual(0, len(result[memory.REST_OF_MEMORIES]))


if __name__ == "__main__":
    unittest.main()
