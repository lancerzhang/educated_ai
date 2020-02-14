from components.memory import Memory
from components import constants
from components import memory
from components.memory import MemoryType
from components.memory import FeatureType
import time
import unittest


class TestMemory(unittest.TestCase):

    def test0_refresh_5s(self):
        mem = Memory(MemoryType.LONG)
        mem.strength = 100
        mem.last_recall_time = int(time.time()) - 4
        mem.refresh_self(recall=True)
        self.assertEqual(0, mem.recall_count)

    def test0_refresh_6s(self):
        mem = Memory(MemoryType.LONG)
        mem.last_recall_time = int(time.time()) - 5
        mem.refresh_self(recall=True)
        self.assertEqual(1, mem.recall_count)

    def test0_refresh_20m(self):
        mem = Memory(MemoryType.LONG)
        mem.last_recall_time = int(time.time()) - 1200
        mem.refresh_self(recall=True)
        self.assertEqual(1, mem.recall_count)

    def test0_refresh_1h(self):
        mem = Memory(MemoryType.LONG)
        mem.last_recall_time = int(time.time()) - 3600
        mem.refresh_self(recall=True)
        self.assertEqual(1, mem.recall_count)

    def test0_refresh_1d(self):
        mem = Memory(MemoryType.LONG)
        mem.last_recall_time = int(time.time()) - 86400
        mem.refresh_self(recall=True)
        self.assertEqual(1, mem.recall_count)

    def test0_refresh_1w(self):
        mem = Memory(MemoryType.LONG)
        mem.last_recall_time = int(time.time()) - 604800
        mem.refresh_self(recall=True)
        self.assertEqual(1, mem.recall_count)

    def test0_refresh_1m(self):
        mem = Memory(MemoryType.LONG)
        mem.last_recall_time = int(time.time()) - 2592000
        mem.refresh_self(recall=True)
        self.assertEqual(1, mem.recall_count)

    def test0_refresh_greater_1m(self):
        mem = Memory(MemoryType.LONG)
        mem.last_recall_time = int(time.time()) - 3200140
        mem.refresh_self(recall=True)
        self.assertEqual(1, mem.recall_count)

    def test0_refresh_greater_1y(self):
        mem = Memory(MemoryType.LONG)
        mem.last_recall_time = int(time.time()) - 31536000
        mem.refresh_self(recall=True)
        self.assertEqual(1, mem.recall_count)

    # test memory refresh of one recall

    def test1_refresh_5s(self):
        mem = Memory(MemoryType.LONG)
        mem.strength = 100
        mem.recall_count = 1
        mem.last_recall_time = int(time.time()) - 4
        mem.refresh_self(recall=True)
        self.assertEqual(1, mem.recall_count)

    def test1_refresh_6s(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 1
        mem.last_recall_time = int(time.time()) - 6
        mem.refresh_self(recall=True)
        self.assertEqual(2, mem.recall_count)

    def test1_refresh_20m(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 1
        mem.last_recall_time = int(time.time()) - 1200
        mem.refresh_self(recall=True)
        self.assertEqual(2, mem.recall_count)

    def test1_refresh_1h(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 1
        mem.last_recall_time = int(time.time()) - 3600
        mem.refresh_self(recall=True)
        self.assertEqual(2, mem.recall_count)

    def test1_refresh_1d(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 1
        mem.last_recall_time = int(time.time()) - 86400
        mem.refresh_self(recall=True)
        self.assertEqual(2, mem.recall_count)

    def test1_refresh_1w(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 1
        mem.last_recall_time = int(time.time()) - 604800
        mem.refresh_self(recall=True)
        self.assertEqual(2, mem.recall_count)

    def test1_refresh_1m(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 1
        mem.last_recall_time = int(time.time()) - 2592000
        mem.refresh_self(recall=True)
        self.assertEqual(2, mem.recall_count)

    def test1_refresh_greater_1m(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 1
        mem.last_recall_time = int(time.time()) - 3200140
        mem.refresh_self(recall=True)
        self.assertEqual(2, mem.recall_count)

    def test1_refresh_greater_1y(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 1
        mem.last_recall_time = int(time.time()) - 31536000
        mem.refresh_self(recall=True)
        self.assertEqual(2, mem.recall_count)

    # test memory refresh of night recall

    def test9_refresh_5s(self):
        mem = Memory(MemoryType.LONG)
        mem.strength = 100
        mem.recall_count = 9
        mem.last_recall_time = int(time.time()) - 4
        mem.refresh_self(recall=True)
        self.assertEqual(9, mem.recall_count)

    def test9_refresh_6s(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 9
        mem.last_recall_time = int(time.time()) - 5
        mem.refresh_self(recall=True)
        self.assertEqual(9, mem.recall_count)

    def test9_refresh_20m(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 9
        mem.last_recall_time = int(time.time()) - 1200
        mem.refresh_self(recall=True)
        self.assertEqual(10, mem.recall_count)

    def test9_refresh_1h(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 9
        mem.last_recall_time = int(time.time()) - 3600
        mem.refresh_self(recall=True)
        self.assertEqual(10, mem.recall_count)

    def test9_refresh_1d(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 9
        mem.last_recall_time = int(time.time()) - 86400
        mem.refresh_self(recall=True)
        self.assertEqual(10, mem.recall_count)

    def test9_refresh_1w(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 9
        mem.last_recall_time = int(time.time()) - 604800
        mem.refresh_self(recall=True)
        self.assertEqual(10, mem.recall_count)

    def test9_refresh_1m(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 9
        mem.last_recall_time = int(time.time()) - 2592000
        mem.refresh_self(recall=True)
        self.assertEqual(10, mem.recall_count)

    def test9_refresh_greater_1m(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 9
        mem.last_recall_time = int(time.time()) - 3200140
        mem.refresh_self(recall=True)
        self.assertEqual(10, mem.recall_count)

    def test9_refresh_greater_1y(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 9
        mem.last_recall_time = int(time.time()) - 31536000
        mem.refresh_self(recall=True)
        self.assertEqual(10, mem.recall_count)

    # test memory refresh of twenty recall

    def test20_refresh_60s(self):
        mem = Memory(MemoryType.LONG)
        mem.strength = 100
        mem.recall_count = 20
        mem.last_recall_time = int(time.time()) - 50
        mem.refresh_self(recall=True)
        self.assertEqual(20, mem.recall_count)

    def test20_refresh_62s(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 20
        mem.last_recall_time = int(time.time()) - 62
        mem.refresh_self(recall=True)
        self.assertEqual(20, mem.recall_count)

    def test20_refresh_20m(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 20
        mem.last_recall_time = int(time.time()) - 1200
        mem.refresh_self(recall=True)
        self.assertEqual(21, mem.recall_count)

    def test20_refresh_1h(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 20
        mem.last_recall_time = int(time.time()) - 3600
        mem.refresh_self(recall=True)
        self.assertEqual(21, mem.recall_count)

    def test20_refresh_1d(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 20
        mem.last_recall_time = int(time.time()) - 86400
        mem.refresh_self(recall=True)
        self.assertEqual(21, mem.recall_count)

    def test20_refresh_1w(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 20
        mem.last_recall_time = int(time.time()) - 604800
        mem.refresh_self(recall=True)
        self.assertEqual(21, mem.recall_count)

    def test20_refresh_1m(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 20
        mem.last_recall_time = int(time.time()) - 2592000
        mem.refresh_self(recall=True)
        self.assertEqual(21, mem.recall_count)

    def test20_refresh_greater_1m(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 20
        mem.last_recall_time = int(time.time()) - 3200140
        mem.refresh_self(recall=True)
        self.assertEqual(21, mem.recall_count)

    def test20_refresh_greater_1y(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 20
        mem.last_recall_time = int(time.time()) - 31536000
        mem.refresh_self(recall=True)
        self.assertEqual(21, mem.recall_count)

    # test memory refresh of fourty recall

    def test40_refresh_60s(self):
        mem = Memory(MemoryType.LONG)
        mem.strength = 100
        mem.recall_count = 40
        mem.last_recall_time = int(time.time()) - 50
        mem.refresh_self(recall=True)
        self.assertEqual(40, mem.recall_count)

    def test40_refresh_62s(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 40
        mem.last_recall_time = int(time.time()) - 62
        mem.refresh_self(recall=True)
        self.assertEqual(40, mem.recall_count)

    def test40_refresh_20m(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 40
        mem.last_recall_time = int(time.time()) - 1200
        mem.refresh_self(recall=True)
        self.assertEqual(41, mem.recall_count)

    def test40_refresh_1h(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 40
        mem.last_recall_time = int(time.time()) - 3600
        mem.refresh_self(recall=True)
        self.assertEqual(41, mem.recall_count)

    def test40_refresh_1d(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 40
        mem.last_recall_time = int(time.time()) - 86400
        mem.refresh_self(recall=True)
        self.assertEqual(41, mem.recall_count)

    def test40_refresh_1w(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 40
        mem.last_recall_time = int(time.time()) - 604800
        mem.refresh_self(recall=True)
        self.assertEqual(41, mem.recall_count)

    def test40_refresh_1m(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 40
        mem.last_recall_time = int(time.time()) - 2592000
        mem.refresh_self(recall=True)
        self.assertEqual(41, mem.recall_count)

    def test40_refresh_greater_1m(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 40
        mem.last_recall_time = int(time.time()) - 3200140
        mem.refresh_self(recall=True)
        self.assertEqual(41, mem.recall_count)

    def test40_refresh_greater_1y(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 40
        mem.last_recall_time = int(time.time()) - 31536000
        mem.refresh_self(recall=True)
        self.assertEqual(41, mem.recall_count)

    # test memory refresh of seventy eight recall

    def test78_refresh_60s(self):
        mem = Memory(MemoryType.LONG)
        mem.strength = 100
        mem.recall_count = 78
        mem.last_recall_time = int(time.time()) - 50
        mem.refresh_self(recall=True)
        self.assertEqual(78, mem.recall_count)

    def test78_refresh_62s(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 78
        mem.last_recall_time = int(time.time()) - 62
        mem.refresh_self(recall=True)
        self.assertEqual(78, mem.recall_count)

    def test78_refresh_20m(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 78
        mem.last_recall_time = int(time.time()) - 1200
        mem.refresh_self(recall=True)
        self.assertEqual(78, mem.recall_count)

    def test78_refresh_1h(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 78
        mem.last_recall_time = int(time.time()) - 3600
        mem.refresh_self(recall=True)
        self.assertEqual(78, mem.recall_count)

    def test78_refresh_1d(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 78
        mem.last_recall_time = int(time.time()) - 86400
        mem.refresh_self(recall=True)
        self.assertEqual(78, mem.recall_count)

    def test78_refresh_1w(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 78
        mem.last_recall_time = int(time.time()) - 604800
        mem.refresh_self(recall=True)
        self.assertEqual(78, mem.recall_count)

    def test78_refresh_1m(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 78
        mem.last_recall_time = int(time.time()) - 2592000
        mem.refresh_self(recall=True)
        self.assertEqual(79, mem.recall_count)

    def test78_refresh_greater_1m(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 78
        mem.last_recall_time = int(time.time()) - 3200140
        mem.refresh_self(recall=True)
        self.assertEqual(79, mem.recall_count)

    def test78_refresh_greater_1y(self):
        mem = Memory(MemoryType.LONG)
        mem.recall_count = 78
        mem.last_recall_time = int(time.time()) - 31536000
        mem.refresh_self(recall=True)
        self.assertEqual(79, mem.recall_count)


if __name__ == "__main__":
    unittest.main()
