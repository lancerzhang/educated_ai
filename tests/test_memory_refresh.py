import unittest, memory, time, constants


class TestMemory(unittest.TestCase):

    def setUp(self):
        memory.forget_memory = False

    # test memory refresh of zero recall

    def test0_refresh_5s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.STRENGTH] = 100
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 4
        memory.refresh(mem)
        self.assertEqual(100, mem[constants.STRENGTH])

    def test0_refresh_6s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 5
        memory.refresh(mem)
        self.assertEqual(99, mem[constants.STRENGTH])

    def test0_refresh_20m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 1290
        memory.refresh(mem)
        self.assertEqual(57, mem[constants.STRENGTH])

    def test0_refresh_1h(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 3600
        memory.refresh(mem)
        self.assertEqual(43, mem[constants.STRENGTH])

    def test0_refresh_1d(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 86400
        memory.refresh(mem)
        self.assertEqual(31, mem[constants.STRENGTH])

    def test0_refresh_1w(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 604800
        memory.refresh(mem)
        self.assertEqual(24, mem[constants.STRENGTH])

    def test0_refresh_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 2592000
        memory.refresh(mem)
        self.assertEqual(21, mem[constants.STRENGTH])

    def test0_refresh_greater_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 3200140
        memory.refresh(mem)
        self.assertEqual(20, mem[constants.STRENGTH])

    def test0_refresh_greater_1y(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 31536000
        memory.refresh(mem)
        self.assertEqual(5, mem[constants.STRENGTH])

    # test memory refresh of one recall

    def test1_refresh_5s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.STRENGTH] = 100
        mem[constants.RECALL] = 1
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 4
        memory.refresh(mem)
        self.assertEqual(100, mem[constants.STRENGTH])

    def test1_refresh_6s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 1
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 5
        memory.refresh(mem)
        self.assertEqual(100, mem[constants.STRENGTH])

    def test1_refresh_20m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 1
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 1290
        memory.refresh(mem)
        self.assertEqual(58, mem[constants.STRENGTH])

    def test1_refresh_1h(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 1
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 3600
        memory.refresh(mem)
        self.assertEqual(44, mem[constants.STRENGTH])

    def test1_refresh_1d(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 1
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 86400
        memory.refresh(mem)
        self.assertEqual(32, mem[constants.STRENGTH])

    def test1_refresh_1w(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 1
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 604800
        memory.refresh(mem)
        self.assertEqual(25, mem[constants.STRENGTH])

    def test1_refresh_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 1
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 2592000
        memory.refresh(mem)
        self.assertEqual(22, mem[constants.STRENGTH])

    def test1_refresh_greater_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 1
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 3200140
        memory.refresh(mem)
        self.assertEqual(21, mem[constants.STRENGTH])

    def test1_refresh_greater_1y(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 1
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 31536000
        memory.refresh(mem)
        self.assertEqual(6, mem[constants.STRENGTH])

    # test memory refresh of night recall

    def test9_refresh_5s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.STRENGTH] = 100
        mem[constants.RECALL] = 9
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 4
        memory.refresh(mem)
        self.assertEqual(100, mem[constants.STRENGTH])

    def test9_refresh_6s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 9
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 5
        memory.refresh(mem)
        self.assertEqual(100, mem[constants.STRENGTH])

    def test9_refresh_20m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 9
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 1290
        memory.refresh(mem)
        self.assertEqual(66, mem[constants.STRENGTH])

    def test9_refresh_1h(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 9
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 3600
        memory.refresh(mem)
        self.assertEqual(52, mem[constants.STRENGTH])

    def test9_refresh_1d(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 9
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 86400
        memory.refresh(mem)
        self.assertEqual(40, mem[constants.STRENGTH])

    def test9_refresh_1w(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 9
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 604800
        memory.refresh(mem)
        self.assertEqual(33, mem[constants.STRENGTH])

    def test9_refresh_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 9
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 2592000
        memory.refresh(mem)
        self.assertEqual(30, mem[constants.STRENGTH])

    def test9_refresh_greater_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 9
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 3200140
        memory.refresh(mem)
        self.assertEqual(29, mem[constants.STRENGTH])

    def test9_refresh_greater_1y(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 9
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 31536000
        memory.refresh(mem)
        self.assertEqual(14, mem[constants.STRENGTH])


    # test memory refresh of twenty recall
    def test20_refresh_60s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.STRENGTH] = 100
        mem[constants.RECALL] = 20
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 50
        memory.refresh(mem)
        self.assertEqual(100, mem[constants.STRENGTH])

    def test20_refresh_62s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 20
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 62
        memory.refresh(mem)
        self.assertEqual(100, mem[constants.STRENGTH])

    def test20_refresh_20m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 20
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 1290
        memory.refresh(mem)
        self.assertEqual(77, mem[constants.STRENGTH])

    def test20_refresh_1h(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 20
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 3600
        memory.refresh(mem)
        self.assertEqual(63, mem[constants.STRENGTH])

    def test20_refresh_1d(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 20
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 86400
        memory.refresh(mem)
        self.assertEqual(51, mem[constants.STRENGTH])

    def test20_refresh_1w(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 20
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 604800
        memory.refresh(mem)
        self.assertEqual(44, mem[constants.STRENGTH])

    def test20_refresh_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 20
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 2592000
        memory.refresh(mem)
        self.assertEqual(41, mem[constants.STRENGTH])

    def test20_refresh_greater_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 20
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 3200140
        memory.refresh(mem)
        self.assertEqual(40, mem[constants.STRENGTH])

    def test20_refresh_greater_1y(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 20
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 31536000
        memory.refresh(mem)
        self.assertEqual(25, mem[constants.STRENGTH])

# test memory refresh of fourty recall

    def test40_refresh_60s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.STRENGTH] = 100
        mem[constants.RECALL] = 40
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 50
        memory.refresh(mem)
        self.assertEqual(100, mem[constants.STRENGTH])

    def test40_refresh_62s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 40
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 62
        memory.refresh(mem)
        self.assertEqual(100, mem[constants.STRENGTH])

    def test40_refresh_20m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 40
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 1290
        memory.refresh(mem)
        self.assertEqual(97, mem[constants.STRENGTH])

    def test40_refresh_1h(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 40
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 3600
        memory.refresh(mem)
        self.assertEqual(83, mem[constants.STRENGTH])

    def test40_refresh_1d(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 40
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 86400
        memory.refresh(mem)
        self.assertEqual(71, mem[constants.STRENGTH])

    def test40_refresh_1w(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 40
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 604800
        memory.refresh(mem)
        self.assertEqual(64, mem[constants.STRENGTH])

    def test40_refresh_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 40
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 2592000
        memory.refresh(mem)
        self.assertEqual(61, mem[constants.STRENGTH])

    def test40_refresh_greater_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 40
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 3200140
        memory.refresh(mem)
        self.assertEqual(60, mem[constants.STRENGTH])

    def test40_refresh_greater_1y(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 40
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 31536000
        memory.refresh(mem)
        self.assertEqual(45, mem[constants.STRENGTH])

# test memory refresh of seventy eight recall

    def test78_refresh_60s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.STRENGTH] = 100
        mem[constants.RECALL] = 78
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 50
        memory.refresh(mem)
        self.assertEqual(100, mem[constants.STRENGTH])

    def test78_refresh_62s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 78
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 62
        memory.refresh(mem)
        self.assertEqual(100, mem[constants.STRENGTH])

    def test78_refresh_20m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 78
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 1200
        memory.refresh(mem)
        self.assertEqual(100, mem[constants.STRENGTH])

    def test78_refresh_1h(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 78
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 3600
        memory.refresh(mem)
        self.assertEqual(100, mem[constants.STRENGTH])

    def test78_refresh_1d(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 78
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 86400
        memory.refresh(mem)
        self.assertEqual(100, mem[constants.STRENGTH])

    def test78_refresh_1w(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 78
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 604800
        memory.refresh(mem)
        self.assertEqual(100, mem[constants.STRENGTH])

    def test78_refresh_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 78
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 2592000
        memory.refresh(mem)
        self.assertEqual(99, mem[constants.STRENGTH])

    def test78_refresh_greater_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 78
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 3200140
        memory.refresh(mem)
        self.assertEqual(98, mem[constants.STRENGTH])

    def test78_refresh_greater_1y(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[constants.RECALL] = 78
        mem[constants.LAST_RECALL_TIME] = int(time.time()) - 31536000
        memory.refresh(mem)
        self.assertEqual(83, mem[constants.STRENGTH])


if __name__ == "__main__":
    unittest.main()
