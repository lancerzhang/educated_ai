import unittest
from components.data_adaptor import DataAdaptor
from components.data_tinydb import DataTinyDB
from tinydb import TinyDB
from tinydb.storages import MemoryStorage
import os


class TestDB(unittest.TestCase):
    data_service = None

    def setUp(self):
        database = DataTinyDB(TinyDB(storage=MemoryStorage))
        # database = DB_CodernityDB()
        short_id_filename = 'sid.npy'
        DataAdaptor.SHORT_ID_FILE = short_id_filename
        self.data_service = DataAdaptor(database)
        try:
            os.remove(short_id_filename)
        except OSError:
            pass
        self.data_service.SHORT_ID_FILE = short_id_filename
        for el in database.get_all():
            database.remove(el.get('_id'))

    def test_get_memory(self):
        id = self.data_service._add_memory()
        record = self.data_service._get_memory(id)
        self.assertIsNotNone(record)

    def test_get_short_id(self):
        long_id1 = 'abc1'
        self.assertEqual(1, self.data_service.get_short_id(long_id1))
        self.assertEqual(1, self.data_service.get_short_id(long_id1))
        long_id2 = 'abc2'
        self.assertEqual(2, self.data_service.get_short_id(long_id2))
        self.assertEqual(1, self.data_service.get_short_id(long_id1))

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
