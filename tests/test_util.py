import unittest, util
import numpy as np


class TestUtil(unittest.TestCase):

    def setUp(self):
        pass

    def test_common_elements(self):
        list1 = [1, 2, 3, 4]
        list2 = [4, 5, 6, 7]
        self.assertEqual([4], util.common_elements(list1, list2))

    def test_common_elements2(self):
        list1 = [1, 52, 3, 4, 40, 99]
        list2 = [8, 5, 3, 4, 65, 7, 0, 87]
        self.assertEqual([3, 4], util.common_elements(list1, list2))

    def test_common_elements(self):
        list1 = [1, 2, 3, 4]
        list2 = [5, 6, 7]
        self.assertEqual([], util.common_elements(list1, list2))

    def test_comprehension_new(self):
        list1 = [1, 2, 3, 4]
        list2 = [2, 3, 4]
        list3 = util.comprehension_new(list1, list2)
        self.assertEqual([1], list3)

    def test_comprehension_new2(self):
        list1 = [1, 2, 3, 4]
        list2 = [1, 2, 3]
        list3 = util.comprehension_new(list1, list2)
        self.assertEqual([4], list3)

    def test_comprehension_new3(self):
        list1 = [1, 2]
        list2 = [1, 2]
        list3 = util.comprehension_new(list1, list2)
        self.assertEqual([], list3)

    def test_comprehension_new4(self):
        list1 = [1, 2]
        list2 = [3, 4]
        list3 = util.comprehension_new(list1, list2)
        self.assertEqual([1, 2], list3)

    def test_comprehension(self):
        list1 = [1, 2, 3, 4]
        list2 = [2, 3, 4]
        util.comprehension(list1, list2)
        self.assertEqual([1], list1)

    def test_comprehension2(self):
        list1 = [1, 2, 3, 4]
        list2 = [1, 2, 3]
        util.comprehension(list1, list2)
        self.assertEqual([4], list1)

    def test_comprehension3(self):
        list1 = [1, 2, 3, 4]
        list2 = [2, 3]
        util.comprehension(list1, list2)
        self.assertEqual([1, 4], list1)

    def test_comprehension4(self):
        list1 = [1, 2]
        list2 = [1, 2]
        util.comprehension(list1, list2)
        self.assertEqual([], list1)

    def test_comprehension5(self):
        list1 = [1, 2]
        list2 = [3, 4]
        util.comprehension(list1, list2)
        self.assertEqual([1, 2], list1)


if __name__ == "__main__":
    unittest.main()
