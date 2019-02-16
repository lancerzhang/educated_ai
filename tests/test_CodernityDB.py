import unittest
from components import constants
from components.data_CodernityDB import DataCodernityDB


class TestDB(unittest.TestCase):
    database = None

    def setUp(self):
        self.database = DataCodernityDB()
        for el in self.database.get_all():
            self.database.remove(el.get('_id'))
        self.database.db.compact()

    # def tearDown(self):
    # for el in self.database.get_all():
    #     self.database.remove(el.get('_id'))
    # self.database.db.compact()

    # def test_insert_update_search_by_last_call(self):
    #     record = self.database.insert(
    #         {'lrc': 1578892851, 'rwd': 0, 'cmy': [], 'pmy': [], 'mid': '773701af1bb745d4a21be7defbfc53f2', 'rcl': 1,
    #          'str': 100})
    #     id1 = record.get('_id')
    #     record1 = self.database.get_by_id(id1)
    #     self.assertIsNotNone(record1)
    #     self.database.update({'lrc': 1478892851}, id1)
    #     record2 = self.database.get_by_id(id1)
    #     self.assertEqual(1478892851, record2['lrc'])
    #     record = self.database.insert(
    #         {'lrc': 1578892851, 'rwd': 0, 'cmy': [], 'pmy': [], 'mid': 'a94816e514844ae7a389cab8d84f6ccd', 'rcl': 1,
    #          'str': 100})
    #     clean_time = time.time() - 60
    #     clean_time = int(clean_time)
    #     records = self.database.search_by_last_call(clean_time)
    #     for el in self.database.get_all():
    #         self.database.remove(el.get('_id'))
    #     self.database.db.compact()

    def test_child_memory_index(self):
        child_mem1 = ['073cc59a9f02487db39b2c201e61dfbc', 'e6347111c9424a8f81b0d07df6f264ec']
        reverse_chile_mem1 = ['e6347111c9424a8f81b0d07df6f264ec', '073cc59a9f02487db39b2c201e61dfbc']
        self.database.insert(
            {'lrc': 1578892851, 'rwd': 0, 'cmy': [], 'pmy': [], 'mid': '773701af1bb745d4a21be7defbfc53f2', 'rcl': 1,
             'str': 100, constants.CHILD_MEM: child_mem1})
        self.assertIsNotNone(self.database.get_by_child_memories(child_mem1))
        self.assertIsNotNone(self.database.get_by_child_memories(reverse_chile_mem1))


if __name__ == "__main__":
    unittest.main()
