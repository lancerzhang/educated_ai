import unittest, time, memory, constants
from db import Database
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


class TestDB(unittest.TestCase):
    database = None

    def setUp(self):
        self.database = Database(TinyDB(storage=MemoryStorage))
        memory.forget_memory = True

    def test_housekeep0(self):
        self.database._add_memory({constants.LAST_RECALL: time.time() - 50})
        cleaned = self.database.housekeep()
        self.assertEqual(0, cleaned)

    # there is 1% chance this case will fail, as we turn on forget_memory
    def test_housekeep1(self):
        last_recall = time.time() - 65000000
        el = self.database._add_memory()
        self.database.table.update({constants.LAST_RECALL: last_recall}, Query()[constants.ID] == el)
        cleaned = self.database.housekeep()
        self.assertEqual(1, cleaned)
        self.assertEqual(0, len(self.database.table.all()))

    # there is 1% chance this case will fail, as we turn on forget_memory
    def test_housekeep2(self):
        last_recall1 = time.time() - 65000000
        el1 = self.database._add_memory()
        self.database.table.update({constants.LAST_RECALL: last_recall1}, Query()[constants.ID] == el1)
        last_recall2 = time.time() - 50
        el2 = self.database._add_memory()
        self.database.table.update({constants.LAST_RECALL: last_recall2}, Query()[constants.ID] == el2)
        cleaned = self.database.housekeep()
        self.assertEqual(1, cleaned)
        self.assertEqual(1, len(self.database.table.all()))

    # there is 1% chance this case will fail, as we turn on forget_memory
    def test_housekeep3(self):
        last_recall1 = time.time() - 65000000
        el1 = self.database._add_memory()
        self.database.table.update({constants.LAST_RECALL: last_recall1}, Query()[constants.ID] == el1)
        last_recall2 = time.time() - 50
        el2 = self.database._add_memory()
        self.database.table.update({constants.LAST_RECALL: last_recall2}, Query()[constants.ID] == el2)
        el3 = self.database._add_memory()
        self.database.table.update({constants.LAST_RECALL: last_recall1}, Query()[constants.ID] == el3)
        cleaned = self.database.housekeep()
        self.assertEqual(2, cleaned)
        self.assertEqual(1, len(self.database.table.all()))


if __name__ == "__main__":
    unittest.main()
