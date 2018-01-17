import unittest, time, memory
from db import Database
from tinydb import TinyDB
from tinydb.storages import MemoryStorage


class TestDB(unittest.TestCase):
    database = None

    def setUp(self):
        self.database = Database(TinyDB(storage=MemoryStorage))
        memory.forget_memory = True

    def test_cleanup_memory0(self):
        self.database.add_memory({'lastRecall': time.time() - 50})
        cleaned = self.database.cleanup_memory()
        self.assertEqual(0, cleaned)

    # there is 1% chance this case will fail, as we turn on forget_memory
    def test_cleanup_memory1(self):
        last_recall = time.time() - 65000000
        el = self.database.add_memory()
        self.database.table.update({'lastRecall': last_recall}, eids=[el])
        cleaned = self.database.cleanup_memory()
        self.assertEqual(1, cleaned)
        self.assertEqual(0, len(self.database.table.all()))

    # there is 1% chance this case will fail, as we turn on forget_memory
    def test_cleanup_memory2(self):
        last_recall1 = time.time() - 65000000
        el1 = self.database.add_memory()
        self.database.table.update({'lastRecall': last_recall1}, eids=[el1])
        last_recall2 = time.time() - 50
        el2 = self.database.add_memory()
        self.database.table.update({'lastRecall': last_recall2}, eids=[el2])
        cleaned = self.database.cleanup_memory()
        self.assertEqual(1, cleaned)
        self.assertEqual(1, len(self.database.table.all()))


if __name__ == "__main__":
    unittest.main()
