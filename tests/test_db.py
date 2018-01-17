import unittest
from db import Database
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


class TestDB(unittest.TestCase):
    database = None

    def setUp(self):
        self.database = Database(TinyDB(storage=MemoryStorage))

    def test_get_memory(self):
        elid = self.database.add_memory()
        record = self.database.get_memory(elid)
        self.assertEqual(record['type'], 'memory')

    def test_add_memory(self):
        self.database.add_memory()
        memory = Query()
        record = self.database.table.search(memory.type == 'memory')[0]
        self.assertEqual(record['type'], 'memory')
        self.assertGreater(record['lastRecall'], 0)

    def test_add_vision(self):
        self.database.add_vision()
        memory = Query()
        record = self.database.table.search(memory.type == 'vision')[0]
        self.assertEqual(record['type'], 'vision')
        self.assertGreater(record['lastRecall'], 0)

    def test_add_sound(self):
        self.database.add_sound()
        memory = Query()
        record = self.database.table.search(memory.type == 'sound')[0]
        self.assertEqual(record['type'], 'sound')
        self.assertGreater(record['lastRecall'], 0)

    def test_add_focus(self):
        self.database.add_focus()
        memory = Query()
        record = self.database.table.search(memory.type == 'focus')[0]
        self.assertEqual(record['type'], 'focus')
        self.assertGreater(record['lastRecall'], 0)

    def test_add_speak(self):
        self.database.add_speak()
        memory = Query()
        record = self.database.table.search(memory.type == 'speak')[0]
        self.assertEqual(record['type'], 'speak')
        self.assertGreater(record['lastRecall'], 0)


if __name__ == "__main__":
    unittest.main()
