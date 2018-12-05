import unittest, sound, memory
from data_service import DataService
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from db_tinydb import DB_TinyDB
from db_CodernityDB import DB_CodernityDB


class TestDB(unittest.TestCase):
    data_service = None

    def setUp(self):
        database = DB_TinyDB(TinyDB(storage=MemoryStorage))
        # database = DB_CodernityDB()
        self.data_service = DataService(database)
        for el in database.get_all():
            database.remove(el.get('_id'))

    def test_get_memory(self):
        id = self.data_service._add_memory()
        record = self.data_service._get_memory(id)
        self.assertIsNotNone(record)

    # def test1(self):
    #     rwd=0
    #     record1 = self.data.add_memory(
    #         {'lrc': 1543983890, 'rwd': rwd, 'str': 100, 'mid': '43b79e1abadd4a809f0ac87bbb2841af', 'pmy': [],
    #          'hpt': 1543983860.155, 'rcl': 1,
    #          'cmy': ['1d931e95406c4b65a3dc7f1a30996368', '65e7e567a7d94c95aec0deaf723994d5',
    #                  '739046def392446c935ec85635e2961d', '621b6fbfe16e42b5801b7658a0e6ff79'], 'mmd': '5itm',
    #          '_id': '43b79e1abadd4a809f0ac87bbb2841af'})
    #     print record1

if __name__ == "__main__":
    unittest.main()
