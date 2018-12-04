import unittest, sound, memory
from data import Data
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from db_tinydb import DB_TinyDB
from db_CodernityDB import DB_CodernityDB


class TestDB(unittest.TestCase):
    data = None

    def setUp(self):
        database = DB_TinyDB(TinyDB(storage=MemoryStorage))
        # database = DB_CodernityDB()
        self.data = Data(database)
        for el in database.get_all():
            database.remove(el.get('_id'))

    def test_get_memory(self):
        id = self.data._add_memory()
        record = self.data._get_memory(id)
        self.assertIsNotNone(record)


if __name__ == "__main__":
    unittest.main()
