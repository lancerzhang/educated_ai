import unittest, memory, time


class TestMemory(unittest.TestCase):

    def setUp(self):
        memory.forget_memory = False
    # test memory refresh of zero recall

    def test0_refresh_60s(self):
        mem = memory.basic_memory.copy()
        mem['strength'] = 100
        mem['lastRecall'] = time.time() - 50
        memory.refresh(mem,True)
        self.assertEqual(0, mem['recall'])

    def test0_refresh_62s(self):
        mem = memory.basic_memory.copy()
        mem['lastRecall'] = time.time() - 62
        memory.refresh(mem,True)
        self.assertEqual(1, mem['recall'])

    def test0_refresh_20m(self):
        mem = memory.basic_memory.copy()
        mem['lastRecall'] = time.time() - 1200
        memory.refresh(mem,True)
        self.assertEqual(1, mem['recall'])

    def test0_refresh_1h(self):
        mem = memory.basic_memory.copy()
        mem['lastRecall'] = time.time() - 3600
        memory.refresh(mem,True)
        self.assertEqual(1, mem['recall'])

    def test0_refresh_1d(self):
        mem = memory.basic_memory.copy()
        mem['lastRecall'] = time.time() - 86400
        memory.refresh(mem,True)
        self.assertEqual(1, mem['recall'])

    def test0_refresh_1w(self):
        mem = memory.basic_memory.copy()
        mem['lastRecall'] = time.time() - 604800
        memory.refresh(mem,True)
        self.assertEqual(1, mem['recall'])

    def test0_refresh_1m(self):
        mem = memory.basic_memory.copy()
        mem['lastRecall'] = time.time() - 2592000
        memory.refresh(mem,True)
        self.assertEqual(1, mem['recall'])

    def test0_refresh_greater_1m(self):
        mem = memory.basic_memory.copy()
        mem['lastRecall'] = time.time() - 3200140
        memory.refresh(mem,True)
        self.assertEqual(1, mem['recall'])

    def test0_refresh_greater_1y(self):
        mem = memory.basic_memory.copy()
        mem['lastRecall'] = time.time() - 31536000
        memory.refresh(mem,True)
        self.assertEqual(1, mem['recall'])


    # test memory refresh of one recall

    def test1_refresh_60s(self):
        mem = memory.basic_memory.copy()
        mem['strength'] = 100
        mem['recall'] = 1
        mem['lastRecall'] = time.time() - 50
        memory.refresh(mem,True)
        self.assertEqual(1, mem['recall'])

    def test1_refresh_62s(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 1
        mem['lastRecall'] = time.time() - 62
        memory.refresh(mem,True)
        self.assertEqual(2, mem['recall'])

    def test1_refresh_20m(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 1
        mem['lastRecall'] = time.time() - 1200
        memory.refresh(mem,True)
        self.assertEqual(2, mem['recall'])

    def test1_refresh_1h(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 1
        mem['lastRecall'] = time.time() - 3600
        memory.refresh(mem,True)
        self.assertEqual(2, mem['recall'])

    def test1_refresh_1d(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 1
        mem['lastRecall'] = time.time() - 86400
        memory.refresh(mem,True)
        self.assertEqual(2, mem['recall'])

    def test1_refresh_1w(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 1
        mem['lastRecall'] = time.time() - 604800
        memory.refresh(mem,True)
        self.assertEqual(2, mem['recall'])

    def test1_refresh_1m(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 1
        mem['lastRecall'] = time.time() - 2592000
        memory.refresh(mem,True)
        self.assertEqual(2, mem['recall'])

    def test1_refresh_greater_1m(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 1
        mem['lastRecall'] = time.time() - 3200140
        memory.refresh(mem,True)
        self.assertEqual(2, mem['recall'])

    def test1_refresh_greater_1y(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 1
        mem['lastRecall'] = time.time() - 31536000
        memory.refresh(mem,True)
        self.assertEqual(2, mem['recall'])


    # test memory refresh of night recall

    def test9_refresh_60s(self):
        mem = memory.basic_memory.copy()
        mem['strength'] = 100
        mem['recall'] = 9
        mem['lastRecall'] = time.time() - 50
        memory.refresh(mem,True)
        self.assertEqual(9, mem['recall'])

    def test9_refresh_62s(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 9
        mem['lastRecall'] = time.time() - 62
        memory.refresh(mem,True)
        self.assertEqual(9, mem['recall'])

    def test9_refresh_20m(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 9
        mem['lastRecall'] = time.time() - 1200
        memory.refresh(mem,True)
        self.assertEqual(10, mem['recall'])

    def test9_refresh_1h(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 9
        mem['lastRecall'] = time.time() - 3600
        memory.refresh(mem,True)
        self.assertEqual(10, mem['recall'])

    def test9_refresh_1d(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 9
        mem['lastRecall'] = time.time() - 86400
        memory.refresh(mem,True)
        self.assertEqual(10, mem['recall'])

    def test9_refresh_1w(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 9
        mem['lastRecall'] = time.time() - 604800
        memory.refresh(mem,True)
        self.assertEqual(10, mem['recall'])

    def test9_refresh_1m(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 9
        mem['lastRecall'] = time.time() - 2592000
        memory.refresh(mem,True)
        self.assertEqual(10, mem['recall'])

    def test9_refresh_greater_1m(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 9
        mem['lastRecall'] = time.time() - 3200140
        memory.refresh(mem,True)
        self.assertEqual(10, mem['recall'])

    def test9_refresh_greater_1y(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 9
        mem['lastRecall'] = time.time() - 31536000
        memory.refresh(mem,True)
        self.assertEqual(10, mem['recall'])


    # test memory refresh of twenty recall

    def test20_refresh_60s(self):
        mem = memory.basic_memory.copy()
        mem['strength'] = 100
        mem['recall'] = 20
        mem['lastRecall'] = time.time() - 50
        memory.refresh(mem,True)
        self.assertEqual(20, mem['recall'])

    def test20_refresh_62s(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 20
        mem['lastRecall'] = time.time() - 62
        memory.refresh(mem,True)
        self.assertEqual(20, mem['recall'])

    def test20_refresh_20m(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 20
        mem['lastRecall'] = time.time() - 1200
        memory.refresh(mem,True)
        self.assertEqual(21, mem['recall'])

    def test20_refresh_1h(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 20
        mem['lastRecall'] = time.time() - 3600
        memory.refresh(mem,True)
        self.assertEqual(21, mem['recall'])

    def test20_refresh_1d(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 20
        mem['lastRecall'] = time.time() - 86400
        memory.refresh(mem,True)
        self.assertEqual(21, mem['recall'])

    def test20_refresh_1w(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 20
        mem['lastRecall'] = time.time() - 604800
        memory.refresh(mem,True)
        self.assertEqual(21, mem['recall'])

    def test20_refresh_1m(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 20
        mem['lastRecall'] = time.time() - 2592000
        memory.refresh(mem,True)
        self.assertEqual(21, mem['recall'])

    def test20_refresh_greater_1m(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 20
        mem['lastRecall'] = time.time() - 3200140
        memory.refresh(mem,True)
        self.assertEqual(21, mem['recall'])

    def test20_refresh_greater_1y(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 20
        mem['lastRecall'] = time.time() - 31536000
        memory.refresh(mem,True)
        self.assertEqual(21, mem['recall'])



# test memory refresh of fourty recall

    def test40_refresh_60s(self):
        mem = memory.basic_memory.copy()
        mem['strength'] = 100
        mem['recall'] = 40
        mem['lastRecall'] = time.time() - 50
        memory.refresh(mem,True)
        self.assertEqual(40, mem['recall'])

    def test40_refresh_62s(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 40
        mem['lastRecall'] = time.time() - 62
        memory.refresh(mem,True)
        self.assertEqual(40, mem['recall'])

    def test40_refresh_20m(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 40
        mem['lastRecall'] = time.time() - 1200
        memory.refresh(mem,True)
        self.assertEqual(41, mem['recall'])

    def test40_refresh_1h(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 40
        mem['lastRecall'] = time.time() - 3600
        memory.refresh(mem,True)
        self.assertEqual(41, mem['recall'])

    def test40_refresh_1d(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 40
        mem['lastRecall'] = time.time() - 86400
        memory.refresh(mem,True)
        self.assertEqual(41, mem['recall'])

    def test40_refresh_1w(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 40
        mem['lastRecall'] = time.time() - 604800
        memory.refresh(mem,True)
        self.assertEqual(41, mem['recall'])

    def test40_refresh_1m(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 40
        mem['lastRecall'] = time.time() - 2592000
        memory.refresh(mem,True)
        self.assertEqual(41, mem['recall'])

    def test40_refresh_greater_1m(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 40
        mem['lastRecall'] = time.time() - 3200140
        memory.refresh(mem,True)
        self.assertEqual(41, mem['recall'])

    def test40_refresh_greater_1y(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 40
        mem['lastRecall'] = time.time() - 31536000
        memory.refresh(mem,True)
        self.assertEqual(41, mem['recall'])


# test memory refresh of seventy eight recall

    def test78_refresh_60s(self):
        mem = memory.basic_memory.copy()
        mem['strength'] = 100
        mem['recall'] = 78
        mem['lastRecall'] = time.time() - 50
        memory.refresh(mem,True)
        self.assertEqual(78, mem['recall'])

    def test78_refresh_62s(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 78
        mem['lastRecall'] = time.time() - 62
        memory.refresh(mem,True)
        self.assertEqual(78, mem['recall'])

    def test78_refresh_20m(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 78
        mem['lastRecall'] = time.time() - 1200
        memory.refresh(mem,True)
        self.assertEqual(78, mem['recall'])

    def test78_refresh_1h(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 78
        mem['lastRecall'] = time.time() - 3600
        memory.refresh(mem,True)
        self.assertEqual(78, mem['recall'])

    def test78_refresh_1d(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 78
        mem['lastRecall'] = time.time() - 86400
        memory.refresh(mem,True)
        self.assertEqual(78, mem['recall'])

    def test78_refresh_1w(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 78
        mem['lastRecall'] = time.time() - 604800
        memory.refresh(mem,True)
        self.assertEqual(78, mem['recall'])

    def test78_refresh_1m(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 78
        mem['lastRecall'] = time.time() - 2592000
        memory.refresh(mem,True)
        self.assertEqual(79, mem['recall'])

    def test78_refresh_greater_1m(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 78
        mem['lastRecall'] = time.time() - 3200140
        memory.refresh(mem,True)
        self.assertEqual(79, mem['recall'])

    def test78_refresh_greater_1y(self):
        mem = memory.basic_memory.copy()
        mem['recall'] = 78
        mem['lastRecall'] = time.time() - 31536000
        memory.refresh(mem,True)
        self.assertEqual(79, mem['recall'])


if __name__ == "__main__":
    unittest.main()
