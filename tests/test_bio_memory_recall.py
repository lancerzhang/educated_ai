import time
import unittest

from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from components import constants
from components.bio_memory import BioMemory
from components.data_adaptor import DataAdaptor
from components.data_tinydb import DataTinyDB


class TestBioMemory(unittest.TestCase):

    def setUp(self):
        database = DataTinyDB(TinyDB(storage=MemoryStorage))
        da = DataAdaptor(database)
        bm = BioMemory(da)
        bm.forget_memory = False
        self.bio_memory = bm
        self.data_adaptor = da

    # test memory refresh of zero recall

    def test0_refresh_5s(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.STRENGTH] = 100
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 4
        self.bio_memory.refresh(mem, True)
        self.assertEqual(0, mem[constants.RECALL_COUNT])

    def test0_refresh_6s(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 5
        self.bio_memory.refresh(mem, True)
        self.assertEqual(1, mem[constants.RECALL_COUNT])

    def test0_refresh_20m(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 1200
        self.bio_memory.refresh(mem, True)
        self.assertEqual(1, mem[constants.RECALL_COUNT])

    def test0_refresh_1h(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 3600
        self.bio_memory.refresh(mem, True)
        self.assertEqual(1, mem[constants.RECALL_COUNT])

    def test0_refresh_1d(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 86400
        self.bio_memory.refresh(mem, True)
        self.assertEqual(1, mem[constants.RECALL_COUNT])

    def test0_refresh_1w(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 604800
        self.bio_memory.refresh(mem, True)
        self.assertEqual(1, mem[constants.RECALL_COUNT])

    def test0_refresh_1m(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 2592000
        self.bio_memory.refresh(mem, True)
        self.assertEqual(1, mem[constants.RECALL_COUNT])

    def test0_refresh_greater_1m(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 3200140
        self.bio_memory.refresh(mem, True)
        self.assertEqual(1, mem[constants.RECALL_COUNT])

    def test0_refresh_greater_1y(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 31536000
        self.bio_memory.refresh(mem, True)
        self.assertEqual(1, mem[constants.RECALL_COUNT])

    # test memory refresh of one recall

    def test1_refresh_5s(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.STRENGTH] = 100
        mem[constants.RECALL_COUNT] = 1
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 4
        self.bio_memory.refresh(mem, True)
        self.assertEqual(1, mem[constants.RECALL_COUNT])

    def test1_refresh_6s(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 1
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 6
        self.bio_memory.refresh(mem, True)
        self.assertEqual(2, mem[constants.RECALL_COUNT])

    def test1_refresh_20m(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 1
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 1200
        self.bio_memory.refresh(mem, True)
        self.assertEqual(2, mem[constants.RECALL_COUNT])

    def test1_refresh_1h(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 1
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 3600
        self.bio_memory.refresh(mem, True)
        self.assertEqual(2, mem[constants.RECALL_COUNT])

    def test1_refresh_1d(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 1
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 86400
        self.bio_memory.refresh(mem, True)
        self.assertEqual(2, mem[constants.RECALL_COUNT])

    def test1_refresh_1w(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 1
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 604800
        self.bio_memory.refresh(mem, True)
        self.assertEqual(2, mem[constants.RECALL_COUNT])

    def test1_refresh_1m(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 1
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 2592000
        self.bio_memory.refresh(mem, True)
        self.assertEqual(2, mem[constants.RECALL_COUNT])

    def test1_refresh_greater_1m(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 1
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 3200140
        self.bio_memory.refresh(mem, True)
        self.assertEqual(2, mem[constants.RECALL_COUNT])

    def test1_refresh_greater_1y(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 1
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 31536000
        self.bio_memory.refresh(mem, True)
        self.assertEqual(2, mem[constants.RECALL_COUNT])

    # test memory refresh of night recall

    def test9_refresh_5s(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.STRENGTH] = 100
        mem[constants.RECALL_COUNT] = 9
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 4
        self.bio_memory.refresh(mem, True)
        self.assertEqual(9, mem[constants.RECALL_COUNT])

    def test9_refresh_6s(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 9
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 5
        self.bio_memory.refresh(mem, True)
        self.assertEqual(9, mem[constants.RECALL_COUNT])

    def test9_refresh_20m(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 9
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 1200
        self.bio_memory.refresh(mem, True)
        self.assertEqual(10, mem[constants.RECALL_COUNT])

    def test9_refresh_1h(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 9
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 3600
        self.bio_memory.refresh(mem, True)
        self.assertEqual(10, mem[constants.RECALL_COUNT])

    def test9_refresh_1d(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 9
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 86400
        self.bio_memory.refresh(mem, True)
        self.assertEqual(10, mem[constants.RECALL_COUNT])

    def test9_refresh_1w(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 9
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 604800
        self.bio_memory.refresh(mem, True)
        self.assertEqual(10, mem[constants.RECALL_COUNT])

    def test9_refresh_1m(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 9
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 2592000
        self.bio_memory.refresh(mem, True)
        self.assertEqual(10, mem[constants.RECALL_COUNT])

    def test9_refresh_greater_1m(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 9
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 3200140
        self.bio_memory.refresh(mem, True)
        self.assertEqual(10, mem[constants.RECALL_COUNT])

    def test9_refresh_greater_1y(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 9
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 31536000
        self.bio_memory.refresh(mem, True)
        self.assertEqual(10, mem[constants.RECALL_COUNT])

    # test memory refresh of twenty recall

    def test20_refresh_60s(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.STRENGTH] = 100
        mem[constants.RECALL_COUNT] = 20
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 50
        self.bio_memory.refresh(mem, True)
        self.assertEqual(20, mem[constants.RECALL_COUNT])

    def test20_refresh_62s(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 20
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 62
        self.bio_memory.refresh(mem, True)
        self.assertEqual(20, mem[constants.RECALL_COUNT])

    def test20_refresh_20m(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 20
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 1200
        self.bio_memory.refresh(mem, True)
        self.assertEqual(21, mem[constants.RECALL_COUNT])

    def test20_refresh_1h(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 20
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 3600
        self.bio_memory.refresh(mem, True)
        self.assertEqual(21, mem[constants.RECALL_COUNT])

    def test20_refresh_1d(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 20
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 86400
        self.bio_memory.refresh(mem, True)
        self.assertEqual(21, mem[constants.RECALL_COUNT])

    def test20_refresh_1w(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 20
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 604800
        self.bio_memory.refresh(mem, True)
        self.assertEqual(21, mem[constants.RECALL_COUNT])

    def test20_refresh_1m(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 20
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 2592000
        self.bio_memory.refresh(mem, True)
        self.assertEqual(21, mem[constants.RECALL_COUNT])

    def test20_refresh_greater_1m(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 20
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 3200140
        self.bio_memory.refresh(mem, True)
        self.assertEqual(21, mem[constants.RECALL_COUNT])

    def test20_refresh_greater_1y(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 20
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 31536000
        self.bio_memory.refresh(mem, True)
        self.assertEqual(21, mem[constants.RECALL_COUNT])

    # test memory refresh of fourty recall

    def test40_refresh_60s(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.STRENGTH] = 100
        mem[constants.RECALL_COUNT] = 40
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 50
        self.bio_memory.refresh(mem, True)
        self.assertEqual(40, mem[constants.RECALL_COUNT])

    def test40_refresh_62s(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 40
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 62
        self.bio_memory.refresh(mem, True)
        self.assertEqual(40, mem[constants.RECALL_COUNT])

    def test40_refresh_20m(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 40
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 1200
        self.bio_memory.refresh(mem, True)
        self.assertEqual(41, mem[constants.RECALL_COUNT])

    def test40_refresh_1h(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 40
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 3600
        self.bio_memory.refresh(mem, True)
        self.assertEqual(41, mem[constants.RECALL_COUNT])

    def test40_refresh_1d(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 40
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 86400
        self.bio_memory.refresh(mem, True)
        self.assertEqual(41, mem[constants.RECALL_COUNT])

    def test40_refresh_1w(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 40
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 604800
        self.bio_memory.refresh(mem, True)
        self.assertEqual(41, mem[constants.RECALL_COUNT])

    def test40_refresh_1m(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 40
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 2592000
        self.bio_memory.refresh(mem, True)
        self.assertEqual(41, mem[constants.RECALL_COUNT])

    def test40_refresh_greater_1m(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 40
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 3200140
        self.bio_memory.refresh(mem, True)
        self.assertEqual(41, mem[constants.RECALL_COUNT])

    def test40_refresh_greater_1y(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 40
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 31536000
        self.bio_memory.refresh(mem, True)
        self.assertEqual(41, mem[constants.RECALL_COUNT])

    # test memory refresh of seventy eight recall

    def test78_refresh_60s(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.STRENGTH] = 100
        mem[constants.RECALL_COUNT] = 78
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 50
        self.bio_memory.refresh(mem, True)
        self.assertEqual(78, mem[constants.RECALL_COUNT])

    def test78_refresh_62s(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 78
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 62
        self.bio_memory.refresh(mem, True)
        self.assertEqual(78, mem[constants.RECALL_COUNT])

    def test78_refresh_20m(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 78
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 1200
        self.bio_memory.refresh(mem, True)
        self.assertEqual(78, mem[constants.RECALL_COUNT])

    def test78_refresh_1h(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 78
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 3600
        self.bio_memory.refresh(mem, True)
        self.assertEqual(78, mem[constants.RECALL_COUNT])

    def test78_refresh_1d(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 78
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 86400
        self.bio_memory.refresh(mem, True)
        self.assertEqual(78, mem[constants.RECALL_COUNT])

    def test78_refresh_1w(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 78
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 604800
        self.bio_memory.refresh(mem, True)
        self.assertEqual(78, mem[constants.RECALL_COUNT])

    def test78_refresh_1m(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 78
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 2592000
        self.bio_memory.refresh(mem, True)
        self.assertEqual(79, mem[constants.RECALL_COUNT])

    def test78_refresh_greater_1m(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 78
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 3200140
        self.bio_memory.refresh(mem, True)
        self.assertEqual(79, mem[constants.RECALL_COUNT])

    def test78_refresh_greater_1y(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem[constants.RECALL_COUNT] = 78
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 31536000
        self.bio_memory.refresh(mem, True)
        self.assertEqual(79, mem[constants.RECALL_COUNT])


if __name__ == "__main__":
    unittest.main()
