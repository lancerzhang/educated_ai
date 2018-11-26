import unittest, sound, memory
from db import Database
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


class TestDB(unittest.TestCase):
    database = None

    def setUp(self):
        self.database = Database(TinyDB(storage=MemoryStorage))

    def test_get_memory(self):
        id = self.database._add_memory()
        record = self.database._get_memory(id)
        self.assertIsNotNone(record)



if __name__ == "__main__":
    unittest.main()
