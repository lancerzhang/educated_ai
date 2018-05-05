import unittest,vFilter

class TestUtil(unittest.TestCase):

    def setUp(self):
        pass

    def test_getFilter(self):
        filter=vFilter.getFilter()
        self.assertIsNotNone(filter)

    def test_getFilter2(self):
        filter=vFilter._getFilter(0)
        self.assertIsNotNone(filter)