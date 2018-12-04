import unittest, time, memory, constants
from data import Data
from tinydb import TinyDB
from tinydb.storages import MemoryStorage
from db_tinydb import DB_TinyDB
from db_CodernityDB import DB_CodernityDB
from CodernityDB.database import Database


class TestDB(unittest.TestCase):
    data = None
    database = None

    def setUp(self):
        # database = DB_TinyDB(TinyDB(storage=MemoryStorage))
        database = DB_CodernityDB()
        for el in database.get_all():
            database.remove(el.get('_id'))
        self.data = Data(database)
        memory.forget_memory = True

    def test_housekeep0(self):
        self.data._add_memory({constants.LAST_RECALL: time.time() - 50})
        cleaned = self.data.housekeep()
        self.assertEqual(0, cleaned)

    # there is 1% chance this case will fail, as we turn on forget_memory
    def test_housekeep1(self):
        last_recall = time.time() - 65000000
        last_recall = int(last_recall)
        eid = self.data._add_memory()
        self.data.update_memory({constants.LAST_RECALL: last_recall}, eid)
        cleaned = self.data.housekeep()
        self.assertEqual(1, cleaned)
        self.assertEqual(0, len(self.data.get_all_memories()))

    # there is 1% chance this case will fail, as we turn on forget_memory
    def test_housekeep2(self):
        last_recall1 = time.time() - 65000000
        last_recall1 = int(last_recall1)
        eid1 = self.data._add_memory()
        self.data.update_memory({constants.LAST_RECALL: last_recall1}, eid1)
        last_recall2 = time.time() - 50
        last_recall2 = int(last_recall2)
        eid2 = self.data._add_memory()
        self.data.update_memory({constants.LAST_RECALL: last_recall2}, eid2)
        cleaned = self.data.housekeep()
        self.assertEqual(1, cleaned)
        self.assertEqual(1, len(self.data.get_all_memories()))

    # there is 1% chance this case will fail, as we turn on forget_memory
    def test_housekeep3(self):
        last_recall1 = time.time() - 65000000
        last_recall1 = int(last_recall1)
        eid1 = self.data._add_memory()
        self.data.update_memory({constants.LAST_RECALL: last_recall1}, eid1)
        last_recall2 = time.time() - 50
        last_recall2 = int(last_recall2)
        eid2 = self.data._add_memory()
        self.data.update_memory({constants.LAST_RECALL: last_recall2}, eid2)
        eid3 = self.data._add_memory()
        self.data.update_memory({constants.LAST_RECALL: last_recall1}, eid3)
        cleaned = self.data.housekeep()
        self.assertEqual(2, cleaned)
        self.assertEqual(1, len(self.data.get_all_memories()))


if __name__ == "__main__":
    unittest.main()
