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

    def test_add_vision(self):
        self.database._add_vision()
        query = Query()
        record = self.database.table.search(query[memory.FEATURE_TYPE] == memory.VISION)[0]
        self.assertEqual(record[memory.FEATURE_TYPE], memory.VISION)
        self.assertGreater(record[memory.LAST_RECALL], 0)

    def test_add_sound(self):
        self.database._add_sound()
        query = Query()
        record = self.database.table.search(query[memory.FEATURE_TYPE] == memory.SOUND)[0]
        self.assertEqual(record[memory.FEATURE_TYPE], memory.SOUND)
        self.assertGreater(record[memory.LAST_RECALL], 0)

    def test_add_action(self):
        self.database._add_action()
        query = Query()
        record = self.database.table.search(query[memory.FEATURE_TYPE] == memory.ACTION)[0]
        self.assertEqual(record[memory.FEATURE_TYPE], memory.ACTION)
        self.assertGreater(record[memory.LAST_RECALL], 0)


if __name__ == "__main__":
    unittest.main()
