import unittest, memory, time, constants


class TestMemory(unittest.TestCase):

    def setUp(self):
        memory.forget_memory = False

    # test memory refresh of zero recall

    def test0_refresh_5s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.STRENGTH] = 100
        mem[constants.LAST_RECALL] = int(time.time()) - 4
        memory.refresh(mem, True)
        self.assertEqual(0, mem[constants.RECALL])

    def test0_refresh_6s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.LAST_RECALL] = int(time.time()) - 5
        memory.refresh(mem, True)
        self.assertEqual(1, mem[constants.RECALL])

    def test0_refresh_20m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.LAST_RECALL] = int(time.time()) - 1200
        memory.refresh(mem, True)
        self.assertEqual(1, mem[constants.RECALL])

    def test0_refresh_1h(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.LAST_RECALL] = int(time.time()) - 3600
        memory.refresh(mem, True)
        self.assertEqual(1, mem[constants.RECALL])

    def test0_refresh_1d(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.LAST_RECALL] = int(time.time()) - 86400
        memory.refresh(mem, True)
        self.assertEqual(1, mem[constants.RECALL])

    def test0_refresh_1w(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.LAST_RECALL] = int(time.time()) - 604800
        memory.refresh(mem, True)
        self.assertEqual(1, mem[constants.RECALL])

    def test0_refresh_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.LAST_RECALL] = int(time.time()) - 2592000
        memory.refresh(mem, True)
        self.assertEqual(1, mem[constants.RECALL])

    def test0_refresh_greater_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.LAST_RECALL] = int(time.time()) - 3200140
        memory.refresh(mem, True)
        self.assertEqual(1, mem[constants.RECALL])

    def test0_refresh_greater_1y(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.LAST_RECALL] = int(time.time()) - 31536000
        memory.refresh(mem, True)
        self.assertEqual(1, mem[constants.RECALL])

    # test memory refresh of one recall

    def test1_refresh_5s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.STRENGTH] = 100
        mem[constants.RECALL] = 1
        mem[constants.LAST_RECALL] = int(time.time()) - 4
        memory.refresh(mem, True)
        self.assertEqual(1, mem[constants.RECALL])

    def test1_refresh_6s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 1
        mem[constants.LAST_RECALL] = int(time.time()) - 6
        memory.refresh(mem, True)
        self.assertEqual(2, mem[constants.RECALL])

    def test1_refresh_20m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 1
        mem[constants.LAST_RECALL] = int(time.time()) - 1200
        memory.refresh(mem, True)
        self.assertEqual(2, mem[constants.RECALL])

    def test1_refresh_1h(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 1
        mem[constants.LAST_RECALL] = int(time.time()) - 3600
        memory.refresh(mem, True)
        self.assertEqual(2, mem[constants.RECALL])

    def test1_refresh_1d(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 1
        mem[constants.LAST_RECALL] = int(time.time()) - 86400
        memory.refresh(mem, True)
        self.assertEqual(2, mem[constants.RECALL])

    def test1_refresh_1w(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 1
        mem[constants.LAST_RECALL] = int(time.time()) - 604800
        memory.refresh(mem, True)
        self.assertEqual(2, mem[constants.RECALL])

    def test1_refresh_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 1
        mem[constants.LAST_RECALL] = int(time.time()) - 2592000
        memory.refresh(mem, True)
        self.assertEqual(2, mem[constants.RECALL])

    def test1_refresh_greater_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 1
        mem[constants.LAST_RECALL] = int(time.time()) - 3200140
        memory.refresh(mem, True)
        self.assertEqual(2, mem[constants.RECALL])

    def test1_refresh_greater_1y(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 1
        mem[constants.LAST_RECALL] = int(time.time()) - 31536000
        memory.refresh(mem, True)
        self.assertEqual(2, mem[constants.RECALL])

    # test memory refresh of night recall

    def test9_refresh_5s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.STRENGTH] = 100
        mem[constants.RECALL] = 9
        mem[constants.LAST_RECALL] = int(time.time()) - 4
        memory.refresh(mem, True)
        self.assertEqual(9, mem[constants.RECALL])

    def test9_refresh_6s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 9
        mem[constants.LAST_RECALL] = int(time.time()) - 5
        memory.refresh(mem, True)
        self.assertEqual(9, mem[constants.RECALL])

    def test9_refresh_20m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 9
        mem[constants.LAST_RECALL] = int(time.time()) - 1200
        memory.refresh(mem, True)
        self.assertEqual(10, mem[constants.RECALL])

    def test9_refresh_1h(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 9
        mem[constants.LAST_RECALL] = int(time.time()) - 3600
        memory.refresh(mem, True)
        self.assertEqual(10, mem[constants.RECALL])

    def test9_refresh_1d(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 9
        mem[constants.LAST_RECALL] = int(time.time()) - 86400
        memory.refresh(mem, True)
        self.assertEqual(10, mem[constants.RECALL])

    def test9_refresh_1w(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 9
        mem[constants.LAST_RECALL] = int(time.time()) - 604800
        memory.refresh(mem, True)
        self.assertEqual(10, mem[constants.RECALL])

    def test9_refresh_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 9
        mem[constants.LAST_RECALL] = int(time.time()) - 2592000
        memory.refresh(mem, True)
        self.assertEqual(10, mem[constants.RECALL])

    def test9_refresh_greater_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 9
        mem[constants.LAST_RECALL] = int(time.time()) - 3200140
        memory.refresh(mem, True)
        self.assertEqual(10, mem[constants.RECALL])

    def test9_refresh_greater_1y(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 9
        mem[constants.LAST_RECALL] = int(time.time()) - 31536000
        memory.refresh(mem, True)
        self.assertEqual(10, mem[constants.RECALL])

    # test memory refresh of twenty recall

    def test20_refresh_60s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.STRENGTH] = 100
        mem[constants.RECALL] = 20
        mem[constants.LAST_RECALL] = int(time.time()) - 50
        memory.refresh(mem, True)
        self.assertEqual(20, mem[constants.RECALL])

    def test20_refresh_62s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 20
        mem[constants.LAST_RECALL] = int(time.time()) - 62
        memory.refresh(mem, True)
        self.assertEqual(20, mem[constants.RECALL])

    def test20_refresh_20m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 20
        mem[constants.LAST_RECALL] = int(time.time()) - 1200
        memory.refresh(mem, True)
        self.assertEqual(21, mem[constants.RECALL])

    def test20_refresh_1h(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 20
        mem[constants.LAST_RECALL] = int(time.time()) - 3600
        memory.refresh(mem, True)
        self.assertEqual(21, mem[constants.RECALL])

    def test20_refresh_1d(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 20
        mem[constants.LAST_RECALL] = int(time.time()) - 86400
        memory.refresh(mem, True)
        self.assertEqual(21, mem[constants.RECALL])

    def test20_refresh_1w(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 20
        mem[constants.LAST_RECALL] = int(time.time()) - 604800
        memory.refresh(mem, True)
        self.assertEqual(21, mem[constants.RECALL])

    def test20_refresh_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 20
        mem[constants.LAST_RECALL] = int(time.time()) - 2592000
        memory.refresh(mem, True)
        self.assertEqual(21, mem[constants.RECALL])

    def test20_refresh_greater_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 20
        mem[constants.LAST_RECALL] = int(time.time()) - 3200140
        memory.refresh(mem, True)
        self.assertEqual(21, mem[constants.RECALL])

    def test20_refresh_greater_1y(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 20
        mem[constants.LAST_RECALL] = int(time.time()) - 31536000
        memory.refresh(mem, True)
        self.assertEqual(21, mem[constants.RECALL])

    # test memory refresh of fourty recall

    def test40_refresh_60s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.STRENGTH] = 100
        mem[constants.RECALL] = 40
        mem[constants.LAST_RECALL] = int(time.time()) - 50
        memory.refresh(mem, True)
        self.assertEqual(40, mem[constants.RECALL])

    def test40_refresh_62s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 40
        mem[constants.LAST_RECALL] = int(time.time()) - 62
        memory.refresh(mem, True)
        self.assertEqual(40, mem[constants.RECALL])

    def test40_refresh_20m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 40
        mem[constants.LAST_RECALL] = int(time.time()) - 1200
        memory.refresh(mem, True)
        self.assertEqual(41, mem[constants.RECALL])

    def test40_refresh_1h(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 40
        mem[constants.LAST_RECALL] = int(time.time()) - 3600
        memory.refresh(mem, True)
        self.assertEqual(41, mem[constants.RECALL])

    def test40_refresh_1d(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 40
        mem[constants.LAST_RECALL] = int(time.time()) - 86400
        memory.refresh(mem, True)
        self.assertEqual(41, mem[constants.RECALL])

    def test40_refresh_1w(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 40
        mem[constants.LAST_RECALL] = int(time.time()) - 604800
        memory.refresh(mem, True)
        self.assertEqual(41, mem[constants.RECALL])

    def test40_refresh_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 40
        mem[constants.LAST_RECALL] = int(time.time()) - 2592000
        memory.refresh(mem, True)
        self.assertEqual(41, mem[constants.RECALL])

    def test40_refresh_greater_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 40
        mem[constants.LAST_RECALL] = int(time.time()) - 3200140
        memory.refresh(mem, True)
        self.assertEqual(41, mem[constants.RECALL])

    def test40_refresh_greater_1y(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 40
        mem[constants.LAST_RECALL] = int(time.time()) - 31536000
        memory.refresh(mem, True)
        self.assertEqual(41, mem[constants.RECALL])

    # test memory refresh of seventy eight recall

    def test78_refresh_60s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.STRENGTH] = 100
        mem[constants.RECALL] = 78
        mem[constants.LAST_RECALL] = int(time.time()) - 50
        memory.refresh(mem, True)
        self.assertEqual(78, mem[constants.RECALL])

    def test78_refresh_62s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 78
        mem[constants.LAST_RECALL] = int(time.time()) - 62
        memory.refresh(mem, True)
        self.assertEqual(78, mem[constants.RECALL])

    def test78_refresh_20m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 78
        mem[constants.LAST_RECALL] = int(time.time()) - 1200
        memory.refresh(mem, True)
        self.assertEqual(78, mem[constants.RECALL])

    def test78_refresh_1h(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 78
        mem[constants.LAST_RECALL] = int(time.time()) - 3600
        memory.refresh(mem, True)
        self.assertEqual(78, mem[constants.RECALL])

    def test78_refresh_1d(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 78
        mem[constants.LAST_RECALL] = int(time.time()) - 86400
        memory.refresh(mem, True)
        self.assertEqual(78, mem[constants.RECALL])

    def test78_refresh_1w(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 78
        mem[constants.LAST_RECALL] = int(time.time()) - 604800
        memory.refresh(mem, True)
        self.assertEqual(78, mem[constants.RECALL])

    def test78_refresh_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 78
        mem[constants.LAST_RECALL] = int(time.time()) - 2592000
        memory.refresh(mem, True)
        self.assertEqual(79, mem[constants.RECALL])

    def test78_refresh_greater_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 78
        mem[constants.LAST_RECALL] = int(time.time()) - 3200140
        memory.refresh(mem, True)
        self.assertEqual(79, mem[constants.RECALL])

    def test78_refresh_greater_1y(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 78
        mem[constants.LAST_RECALL] = int(time.time()) - 31536000
        memory.refresh(mem, True)
        self.assertEqual(79, mem[constants.RECALL])


if __name__ == "__main__":
    unittest.main()
