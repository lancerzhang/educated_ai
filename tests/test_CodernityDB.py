import unittest, sound, memory, time
from data import Data
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from db_tinydb import DB_TinyDB
from db_CodernityDB import DB_CodernityDB


class TestDB(unittest.TestCase):
    database = None

    def setUp(self):
        self.database = DB_CodernityDB()
        for el in self.database.get_all():
            self.database.remove(el.get('_id'))

    def test_get_memory(self):
        record = self.database.insert(
            {'lrc': 1578892851, 'rwd': 0, 'cmy': [], 'pmy': [], 'mid': '773701af1bb745d4a21be7defbfc53f2', 'rcl': 1,
             'str': 100})
        id1 = record.get('_id')
        record1 = self.database.get_by_id(id1)
        self.assertIsNotNone(record1)
        self.database.update({'lrc': 1478892851}, id1)
        record2 = self.database.get_by_id(id1)
        self.assertEqual(1478892851, record2['lrc'])
        record = self.database.insert(
            {'lrc': 1578892851, 'rwd': 0, 'cmy': [], 'pmy': [], 'mid': 'a94816e514844ae7a389cab8d84f6ccd', 'rcl': 1,
             'str': 100})
        clean_time = time.time() - 60
        clean_time = int(clean_time)
        records = self.database.search_by_last_call(clean_time)
        print records


if __name__ == "__main__":
    unittest.main()
