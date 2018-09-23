import unittest, util, cv2
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

    def test_calculate_similarity1(self):
        value = 100.0
        similarity = 0.1
        sim_result = util.calculate_similarity(value, similarity)
        min = sim_result[0]
        max = sim_result[1]
        self.assertGreater(max, min)

    def test_calculate_similarity2(self):
        value = -100.0
        similarity = 0.1
        sim_result = util.calculate_similarity(value, similarity)
        min = sim_result[0]
        max = sim_result[1]
        self.assertGreater(max, min)

    def test_calculate_similarity3(self):
        value = 0.0
        similarity = 0.1
        sim_result = util.calculate_similarity(value, similarity)
        min = sim_result[0]
        max = sim_result[1]
        self.assertEqual(max, min)

    def test_colorHist(self):
        arr1 = np.array([[[100, 200, 30], [14, 155, 256]],
                         [[79, 118, 190], [60, 110, 230]]])
        hist = util.color_hist(arr1, 3)
        self.assertEqual([3, 1, 0, 0, 3, 1, 1, 0, 3], hist.tolist())

    # def test_compareColorHist(self):
    #     arr1 = np.array([[[100, 200, 30], [14, 155, 256]],
    #                      [[79, 118, 190], [60, 110, 230]]])
    #     hist=util.color_hist(arr1, 3)
    #     print cv2.compareHist(hist,hist,cv2.HISTCMP_BHATTACHARYYA)

    def test_avg_int(self):
        arr = [1, 2, 3]
        self.assertEqual(2, util.avg(arr))

    def test_avg_float(self):
        arr = [1.5, 2.5, 3.5]
        self.assertEqual(2.5, util.avg(arr))


if __name__ == "__main__":
    unittest.main()
