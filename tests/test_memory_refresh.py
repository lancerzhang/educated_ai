import unittest, memory, time


class TestMemory(unittest.TestCase):

    def setUp(self):
        memory.forget_memory = False

    # test memory refresh of zero recall

    def test0_refresh_60s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['strength'] = 100
        mem['lastRecall'] = time.time() - 50
        memory.refresh(mem)
        self.assertEqual(100, mem['strength'])

    def test0_refresh_62s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['lastRecall'] = time.time() - 62
        memory.refresh(mem)
        self.assertEqual(98, mem['strength'])

    def test0_refresh_20m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['lastRecall'] = time.time() - 1200
        memory.refresh(mem)
        self.assertEqual(57, mem['strength'])

    def test0_refresh_1h(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['lastRecall'] = time.time() - 3600
        memory.refresh(mem)
        self.assertEqual(43, mem['strength'])

    def test0_refresh_1d(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['lastRecall'] = time.time() - 86400
        memory.refresh(mem)
        self.assertEqual(31, mem['strength'])

    def test0_refresh_1w(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['lastRecall'] = time.time() - 604800
        memory.refresh(mem)
        self.assertEqual(24, mem['strength'])

    def test0_refresh_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['lastRecall'] = time.time() - 2592000
        memory.refresh(mem)
        self.assertEqual(21, mem['strength'])

    def test0_refresh_greater_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['lastRecall'] = time.time() - 3200140
        memory.refresh(mem)
        self.assertEqual(20, mem['strength'])

    def test0_refresh_greater_1y(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['lastRecall'] = time.time() - 31536000
        memory.refresh(mem)
        self.assertEqual(5, mem['strength'])

    # test memory refresh of one recall

    def test1_refresh_60s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['strength'] = 100
        mem['recall'] = 1
        mem['lastRecall'] = time.time() - 50
        memory.refresh(mem)
        self.assertEqual(100, mem['strength'])

    def test1_refresh_62s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 1
        mem['lastRecall'] = time.time() - 62
        memory.refresh(mem)
        self.assertEqual(99, mem['strength'])

    def test1_refresh_20m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 1
        mem['lastRecall'] = time.time() - 1200
        memory.refresh(mem)
        self.assertEqual(58, mem['strength'])

    def test1_refresh_1h(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 1
        mem['lastRecall'] = time.time() - 3600
        memory.refresh(mem)
        self.assertEqual(44, mem['strength'])

    def test1_refresh_1d(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 1
        mem['lastRecall'] = time.time() - 86400
        memory.refresh(mem)
        self.assertEqual(32, mem['strength'])

    def test1_refresh_1w(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 1
        mem['lastRecall'] = time.time() - 604800
        memory.refresh(mem)
        self.assertEqual(25, mem['strength'])

    def test1_refresh_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 1
        mem['lastRecall'] = time.time() - 2592000
        memory.refresh(mem)
        self.assertEqual(22, mem['strength'])

    def test1_refresh_greater_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 1
        mem['lastRecall'] = time.time() - 3200140
        memory.refresh(mem)
        self.assertEqual(21, mem['strength'])

    def test1_refresh_greater_1y(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 1
        mem['lastRecall'] = time.time() - 31536000
        memory.refresh(mem)
        self.assertEqual(6, mem['strength'])

    # test memory refresh of night recall

    def test9_refresh_60s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['strength'] = 100
        mem['recall'] = 9
        mem['lastRecall'] = time.time() - 50
        memory.refresh(mem)
        self.assertEqual(100, mem['strength'])

    def test9_refresh_62s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 9
        mem['lastRecall'] = time.time() - 62
        memory.refresh(mem)
        self.assertEqual(100, mem['strength'])

    def test9_refresh_20m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 9
        mem['lastRecall'] = time.time() - 1200
        memory.refresh(mem)
        self.assertEqual(66, mem['strength'])

    def test9_refresh_1h(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 9
        mem['lastRecall'] = time.time() - 3600
        memory.refresh(mem)
        self.assertEqual(52, mem['strength'])

    def test9_refresh_1d(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 9
        mem['lastRecall'] = time.time() - 86400
        memory.refresh(mem)
        self.assertEqual(40, mem['strength'])

    def test9_refresh_1w(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 9
        mem['lastRecall'] = time.time() - 604800
        memory.refresh(mem)
        self.assertEqual(33, mem['strength'])

    def test9_refresh_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 9
        mem['lastRecall'] = time.time() - 2592000
        memory.refresh(mem)
        self.assertEqual(30, mem['strength'])

    def test9_refresh_greater_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 9
        mem['lastRecall'] = time.time() - 3200140
        memory.refresh(mem)
        self.assertEqual(29, mem['strength'])

    def test9_refresh_greater_1y(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 9
        mem['lastRecall'] = time.time() - 31536000
        memory.refresh(mem)
        self.assertEqual(14, mem['strength'])


    # test memory refresh of twenty recall

    def test20_refresh_60s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['strength'] = 100
        mem['recall'] = 20
        mem['lastRecall'] = time.time() - 50
        memory.refresh(mem)
        self.assertEqual(100, mem['strength'])

    def test20_refresh_62s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 20
        mem['lastRecall'] = time.time() - 62
        memory.refresh(mem)
        self.assertEqual(100, mem['strength'])

    def test20_refresh_20m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 20
        mem['lastRecall'] = time.time() - 1200
        memory.refresh(mem)
        self.assertEqual(77, mem['strength'])

    def test20_refresh_1h(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 20
        mem['lastRecall'] = time.time() - 3600
        memory.refresh(mem)
        self.assertEqual(63, mem['strength'])

    def test20_refresh_1d(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 20
        mem['lastRecall'] = time.time() - 86400
        memory.refresh(mem)
        self.assertEqual(51, mem['strength'])

    def test20_refresh_1w(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 20
        mem['lastRecall'] = time.time() - 604800
        memory.refresh(mem)
        self.assertEqual(44, mem['strength'])

    def test20_refresh_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 20
        mem['lastRecall'] = time.time() - 2592000
        memory.refresh(mem)
        self.assertEqual(41, mem['strength'])

    def test20_refresh_greater_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 20
        mem['lastRecall'] = time.time() - 3200140
        memory.refresh(mem)
        self.assertEqual(40, mem['strength'])

    def test20_refresh_greater_1y(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 20
        mem['lastRecall'] = time.time() - 31536000
        memory.refresh(mem)
        self.assertEqual(25, mem['strength'])

# test memory refresh of fourty recall

    def test40_refresh_60s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['strength'] = 100
        mem['recall'] = 40
        mem['lastRecall'] = time.time() - 50
        memory.refresh(mem)
        self.assertEqual(100, mem['strength'])

    def test40_refresh_62s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 40
        mem['lastRecall'] = time.time() - 62
        memory.refresh(mem)
        self.assertEqual(100, mem['strength'])

    def test40_refresh_20m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 40
        mem['lastRecall'] = time.time() - 1200
        memory.refresh(mem)
        self.assertEqual(97, mem['strength'])

    def test40_refresh_1h(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 40
        mem['lastRecall'] = time.time() - 3600
        memory.refresh(mem)
        self.assertEqual(83, mem['strength'])

    def test40_refresh_1d(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 40
        mem['lastRecall'] = time.time() - 86400
        memory.refresh(mem)
        self.assertEqual(71, mem['strength'])

    def test40_refresh_1w(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 40
        mem['lastRecall'] = time.time() - 604800
        memory.refresh(mem)
        self.assertEqual(64, mem['strength'])

    def test40_refresh_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 40
        mem['lastRecall'] = time.time() - 2592000
        memory.refresh(mem)
        self.assertEqual(61, mem['strength'])

    def test40_refresh_greater_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 40
        mem['lastRecall'] = time.time() - 3200140
        memory.refresh(mem)
        self.assertEqual(60, mem['strength'])

    def test40_refresh_greater_1y(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 40
        mem['lastRecall'] = time.time() - 31536000
        memory.refresh(mem)
        self.assertEqual(45, mem['strength'])

# test memory refresh of seventy eight recall

    def test78_refresh_60s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['strength'] = 100
        mem['recall'] = 78
        mem['lastRecall'] = time.time() - 50
        memory.refresh(mem)
        self.assertEqual(100, mem['strength'])

    def test78_refresh_62s(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 78
        mem['lastRecall'] = time.time() - 62
        memory.refresh(mem)
        self.assertEqual(100, mem['strength'])

    def test78_refresh_20m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 78
        mem['lastRecall'] = time.time() - 1200
        memory.refresh(mem)
        self.assertEqual(100, mem['strength'])

    def test78_refresh_1h(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 78
        mem['lastRecall'] = time.time() - 3600
        memory.refresh(mem)
        self.assertEqual(100, mem['strength'])

    def test78_refresh_1d(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 78
        mem['lastRecall'] = time.time() - 86400
        memory.refresh(mem)
        self.assertEqual(100, mem['strength'])

    def test78_refresh_1w(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 78
        mem['lastRecall'] = time.time() - 604800
        memory.refresh(mem)
        self.assertEqual(100, mem['strength'])

    def test78_refresh_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 78
        mem['lastRecall'] = time.time() - 2592000
        memory.refresh(mem)
        self.assertEqual(99, mem['strength'])

    def test78_refresh_greater_1m(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 78
        mem['lastRecall'] = time.time() - 3200140
        memory.refresh(mem)
        self.assertEqual(98, mem['strength'])

    def test78_refresh_greater_1y(self):
        mem = memory.BASIC_MEMORY.copy()
        mem['recall'] = 78
        mem['lastRecall'] = time.time() - 31536000
        memory.refresh(mem)
        self.assertEqual(83, mem['strength'])


if __name__ == "__main__":
    unittest.main()
