import unittest, memory, time


class TestMemory(unittest.TestCase):

    def setUp(self):
        memory.forget_memory = False

    # test memory refresh of zero recall

    def test0_refresh_60s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.STRENGTH] = 100
        mem[memory.LASTRECALL] = time.time() - 50
        memory.refresh(mem)
        self.assertEqual(100, mem[memory.STRENGTH])

    def test0_refresh_62s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.LASTRECALL] = time.time() - 62
        memory.refresh(mem)
        self.assertEqual(98, mem[memory.STRENGTH])

    def test0_refresh_20m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.LASTRECALL] = time.time() - 1200
        memory.refresh(mem)
        self.assertEqual(57, mem[memory.STRENGTH])

    def test0_refresh_1h(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.LASTRECALL] = time.time() - 3600
        memory.refresh(mem)
        self.assertEqual(43, mem[memory.STRENGTH])

    def test0_refresh_1d(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.LASTRECALL] = time.time() - 86400
        memory.refresh(mem)
        self.assertEqual(31, mem[memory.STRENGTH])

    def test0_refresh_1w(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.LASTRECALL] = time.time() - 604800
        memory.refresh(mem)
        self.assertEqual(24, mem[memory.STRENGTH])

    def test0_refresh_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.LASTRECALL] = time.time() - 2592000
        memory.refresh(mem)
        self.assertEqual(21, mem[memory.STRENGTH])

    def test0_refresh_greater_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.LASTRECALL] = time.time() - 3200140
        memory.refresh(mem)
        self.assertEqual(20, mem[memory.STRENGTH])

    def test0_refresh_greater_1y(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.LASTRECALL] = time.time() - 31536000
        memory.refresh(mem)
        self.assertEqual(5, mem[memory.STRENGTH])

    # test memory refresh of one recall

    def test1_refresh_60s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.STRENGTH] = 100
        mem[memory.RECALL] = 1
        mem[memory.LASTRECALL] = time.time() - 50
        memory.refresh(mem)
        self.assertEqual(100, mem[memory.STRENGTH])

    def test1_refresh_62s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 1
        mem[memory.LASTRECALL] = time.time() - 62
        memory.refresh(mem)
        self.assertEqual(99, mem[memory.STRENGTH])

    def test1_refresh_20m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 1
        mem[memory.LASTRECALL] = time.time() - 1200
        memory.refresh(mem)
        self.assertEqual(58, mem[memory.STRENGTH])

    def test1_refresh_1h(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 1
        mem[memory.LASTRECALL] = time.time() - 3600
        memory.refresh(mem)
        self.assertEqual(44, mem[memory.STRENGTH])

    def test1_refresh_1d(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 1
        mem[memory.LASTRECALL] = time.time() - 86400
        memory.refresh(mem)
        self.assertEqual(32, mem[memory.STRENGTH])

    def test1_refresh_1w(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 1
        mem[memory.LASTRECALL] = time.time() - 604800
        memory.refresh(mem)
        self.assertEqual(25, mem[memory.STRENGTH])

    def test1_refresh_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 1
        mem[memory.LASTRECALL] = time.time() - 2592000
        memory.refresh(mem)
        self.assertEqual(22, mem[memory.STRENGTH])

    def test1_refresh_greater_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 1
        mem[memory.LASTRECALL] = time.time() - 3200140
        memory.refresh(mem)
        self.assertEqual(21, mem[memory.STRENGTH])

    def test1_refresh_greater_1y(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 1
        mem[memory.LASTRECALL] = time.time() - 31536000
        memory.refresh(mem)
        self.assertEqual(6, mem[memory.STRENGTH])

    # test memory refresh of night recall

    def test9_refresh_60s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.STRENGTH] = 100
        mem[memory.RECALL] = 9
        mem[memory.LASTRECALL] = time.time() - 50
        memory.refresh(mem)
        self.assertEqual(100, mem[memory.STRENGTH])

    def test9_refresh_62s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 9
        mem[memory.LASTRECALL] = time.time() - 62
        memory.refresh(mem)
        self.assertEqual(100, mem[memory.STRENGTH])

    def test9_refresh_20m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 9
        mem[memory.LASTRECALL] = time.time() - 1200
        memory.refresh(mem)
        self.assertEqual(66, mem[memory.STRENGTH])

    def test9_refresh_1h(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 9
        mem[memory.LASTRECALL] = time.time() - 3600
        memory.refresh(mem)
        self.assertEqual(52, mem[memory.STRENGTH])

    def test9_refresh_1d(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 9
        mem[memory.LASTRECALL] = time.time() - 86400
        memory.refresh(mem)
        self.assertEqual(40, mem[memory.STRENGTH])

    def test9_refresh_1w(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 9
        mem[memory.LASTRECALL] = time.time() - 604800
        memory.refresh(mem)
        self.assertEqual(33, mem[memory.STRENGTH])

    def test9_refresh_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 9
        mem[memory.LASTRECALL] = time.time() - 2592000
        memory.refresh(mem)
        self.assertEqual(30, mem[memory.STRENGTH])

    def test9_refresh_greater_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 9
        mem[memory.LASTRECALL] = time.time() - 3200140
        memory.refresh(mem)
        self.assertEqual(29, mem[memory.STRENGTH])

    def test9_refresh_greater_1y(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 9
        mem[memory.LASTRECALL] = time.time() - 31536000
        memory.refresh(mem)
        self.assertEqual(14, mem[memory.STRENGTH])


    # test memory refresh of twenty recall

    def test20_refresh_60s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.STRENGTH] = 100
        mem[memory.RECALL] = 20
        mem[memory.LASTRECALL] = time.time() - 50
        memory.refresh(mem)
        self.assertEqual(100, mem[memory.STRENGTH])

    def test20_refresh_62s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 20
        mem[memory.LASTRECALL] = time.time() - 62
        memory.refresh(mem)
        self.assertEqual(100, mem[memory.STRENGTH])

    def test20_refresh_20m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 20
        mem[memory.LASTRECALL] = time.time() - 1200
        memory.refresh(mem)
        self.assertEqual(77, mem[memory.STRENGTH])

    def test20_refresh_1h(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 20
        mem[memory.LASTRECALL] = time.time() - 3600
        memory.refresh(mem)
        self.assertEqual(63, mem[memory.STRENGTH])

    def test20_refresh_1d(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 20
        mem[memory.LASTRECALL] = time.time() - 86400
        memory.refresh(mem)
        self.assertEqual(51, mem[memory.STRENGTH])

    def test20_refresh_1w(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 20
        mem[memory.LASTRECALL] = time.time() - 604800
        memory.refresh(mem)
        self.assertEqual(44, mem[memory.STRENGTH])

    def test20_refresh_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 20
        mem[memory.LASTRECALL] = time.time() - 2592000
        memory.refresh(mem)
        self.assertEqual(41, mem[memory.STRENGTH])

    def test20_refresh_greater_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 20
        mem[memory.LASTRECALL] = time.time() - 3200140
        memory.refresh(mem)
        self.assertEqual(40, mem[memory.STRENGTH])

    def test20_refresh_greater_1y(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 20
        mem[memory.LASTRECALL] = time.time() - 31536000
        memory.refresh(mem)
        self.assertEqual(25, mem[memory.STRENGTH])

# test memory refresh of fourty recall

    def test40_refresh_60s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.STRENGTH] = 100
        mem[memory.RECALL] = 40
        mem[memory.LASTRECALL] = time.time() - 50
        memory.refresh(mem)
        self.assertEqual(100, mem[memory.STRENGTH])

    def test40_refresh_62s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 40
        mem[memory.LASTRECALL] = time.time() - 62
        memory.refresh(mem)
        self.assertEqual(100, mem[memory.STRENGTH])

    def test40_refresh_20m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 40
        mem[memory.LASTRECALL] = time.time() - 1200
        memory.refresh(mem)
        self.assertEqual(97, mem[memory.STRENGTH])

    def test40_refresh_1h(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 40
        mem[memory.LASTRECALL] = time.time() - 3600
        memory.refresh(mem)
        self.assertEqual(83, mem[memory.STRENGTH])

    def test40_refresh_1d(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 40
        mem[memory.LASTRECALL] = time.time() - 86400
        memory.refresh(mem)
        self.assertEqual(71, mem[memory.STRENGTH])

    def test40_refresh_1w(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 40
        mem[memory.LASTRECALL] = time.time() - 604800
        memory.refresh(mem)
        self.assertEqual(64, mem[memory.STRENGTH])

    def test40_refresh_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 40
        mem[memory.LASTRECALL] = time.time() - 2592000
        memory.refresh(mem)
        self.assertEqual(61, mem[memory.STRENGTH])

    def test40_refresh_greater_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 40
        mem[memory.LASTRECALL] = time.time() - 3200140
        memory.refresh(mem)
        self.assertEqual(60, mem[memory.STRENGTH])

    def test40_refresh_greater_1y(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 40
        mem[memory.LASTRECALL] = time.time() - 31536000
        memory.refresh(mem)
        self.assertEqual(45, mem[memory.STRENGTH])

# test memory refresh of seventy eight recall

    def test78_refresh_60s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.STRENGTH] = 100
        mem[memory.RECALL] = 78
        mem[memory.LASTRECALL] = time.time() - 50
        memory.refresh(mem)
        self.assertEqual(100, mem[memory.STRENGTH])

    def test78_refresh_62s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 78
        mem[memory.LASTRECALL] = time.time() - 62
        memory.refresh(mem)
        self.assertEqual(100, mem[memory.STRENGTH])

    def test78_refresh_20m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 78
        mem[memory.LASTRECALL] = time.time() - 1200
        memory.refresh(mem)
        self.assertEqual(100, mem[memory.STRENGTH])

    def test78_refresh_1h(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 78
        mem[memory.LASTRECALL] = time.time() - 3600
        memory.refresh(mem)
        self.assertEqual(100, mem[memory.STRENGTH])

    def test78_refresh_1d(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 78
        mem[memory.LASTRECALL] = time.time() - 86400
        memory.refresh(mem)
        self.assertEqual(100, mem[memory.STRENGTH])

    def test78_refresh_1w(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 78
        mem[memory.LASTRECALL] = time.time() - 604800
        memory.refresh(mem)
        self.assertEqual(100, mem[memory.STRENGTH])

    def test78_refresh_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 78
        mem[memory.LASTRECALL] = time.time() - 2592000
        memory.refresh(mem)
        self.assertEqual(99, mem[memory.STRENGTH])

    def test78_refresh_greater_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 78
        mem[memory.LASTRECALL] = time.time() - 3200140
        memory.refresh(mem)
        self.assertEqual(98, mem[memory.STRENGTH])

    def test78_refresh_greater_1y(self):
        mem = memory.BASIC_MEMORY.copy()
        mem[memory.RECALL] = 78
        mem[memory.LASTRECALL] = time.time() - 31536000
        memory.refresh(mem)
        self.assertEqual(83, mem[memory.STRENGTH])


if __name__ == "__main__":
    unittest.main()
