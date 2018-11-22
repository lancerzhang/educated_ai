import unittest, util, cv2
import numpy as np


class TestUtil(unittest.TestCase):

    def setUp(self):
        pass

    def test_common_elements(self):
        list1 = [1, 2, 3, 4]
        list2 = [4, 5, 6, 7]
        self.assertEqual([4], util.list_common(list1, list2))

    def test_common_elements2(self):
        list1 = [1, 52, 3, 4, 40, 99]
        list2 = [8, 5, 3, 4, 65, 7, 0, 87]
        self.assertEqual([3, 4], util.list_common(list1, list2))

    def test_common_elements(self):
        list1 = [1, 2, 3, 4]
        list2 = [5, 6, 7]
        self.assertEqual([], util.list_common(list1, list2))

    def list_comprehension_new(self):
        list1 = [1, 2, 3, 4]
        list2 = [2, 3, 4]
        list3 = util.list_comprehension_new(list1, list2)
        self.assertEqual([1], list3)

    def list_comprehension_new2(self):
        list1 = [1, 2, 3, 4]
        list2 = [1, 2, 3]
        list3 = util.list_comprehension_new(list1, list2)
        self.assertEqual([4], list3)

    def list_comprehension_new3(self):
        list1 = [1, 2]
        list2 = [1, 2]
        list3 = util.list_comprehension_new(list1, list2)
        self.assertEqual([], list3)

    def list_comprehension_new4(self):
        list1 = [1, 2]
        list2 = [3, 4]
        list3 = util.list_comprehension_new(list1, list2)
        self.assertEqual([1, 2], list3)

    def test_list_comprehension_existing(self):
        list1 = [1, 2, 3, 4]
        list2 = [2, 3, 4]
        util.list_comprehension_existing(list1, list2)
        self.assertEqual([1], list1)

    def test_list_comprehension_existing2(self):
        list1 = [1, 2, 3, 4]
        list2 = [1, 2, 3]
        util.list_comprehension_existing(list1, list2)
        self.assertEqual([4], list1)

    def test_list_comprehension_existing3(self):
        list1 = [1, 2, 3, 4]
        list2 = [2, 3]
        util.list_comprehension_existing(list1, list2)
        self.assertEqual([1, 4], list1)

    def test_list_comprehension_existing4(self):
        list1 = [1, 2]
        list2 = [1, 2]
        util.list_comprehension_existing(list1, list2)
        self.assertEqual([], list1)

    def test_list_comprehension_existing5(self):
        list1 = [1, 2]
        list2 = [3, 4]
        util.list_comprehension_existing(list1, list2)
        self.assertEqual([1, 2], list1)

    def test_list_concat(self):
        list1 = [1, 2]
        list2 = [3, 4]
        list3 = util.list_concat(list1, list2)
        self.assertEqual(4, len(list3))

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

    def test_standardize_feature1(self):
        matrix = np.array([[0, 0, 0],
                           [0, 1, 2],
                           [0, 3, 4]])
        standard = util.standardize_feature(matrix)
        result = [[1, 2, 0],
                  [3, 4, 0],
                  [0, 0, 0]]
        self.assertEquals(result, standard.tolist())

    def test_standardize_feature2(self):
        matrix = np.array([[0, 0, 0],
                           [0, 0, 0],
                           [0, 0, 4]])
        standard = util.standardize_feature(matrix)
        result = [[4, 0, 0],
                  [0, 0, 0],
                  [0, 0, 0]]
        self.assertEquals(result, standard.tolist())

    def test_standardize_feature3(self):
        matrix = np.array([[0, 1, 2],
                           [0, 0, 0],
                           [0, 3, 4]])
        standard = util.standardize_feature(matrix)
        result = [[1, 2, 0],
                  [0, 0, 0],
                  [3, 4, 0]]
        self.assertEquals(result, standard.tolist())

    def test_standardize_feature3(self):
        matrix = np.array([[0, 1, 2],
                           [0, 3, 4],
                           [0, 0, 0]])
        standard = util.standardize_feature(matrix)
        result = [[1, 2, 0],
                  [3, 4, 0],
                  [0, 0, 0]]
        self.assertEquals(result, standard.tolist())

    def test_update_rank_list(self):
        SPEED = 'spd'
        rank_list = np.array(
            [{SPEED: 1, util.USED_COUNT: 1}, {SPEED: 2, util.USED_COUNT: 2}, {SPEED: 3, util.USED_COUNT: 3}])
        rank_list = util.update_rank_list(SPEED, 3, rank_list)
        self.assertEquals(3, len(rank_list))
        self.assertEquals(4, rank_list[0][util.USED_COUNT])
        rank_list = util.update_rank_list(SPEED, 4, rank_list)
        self.assertEquals(4, len(rank_list))
        rank_list2 = np.array([])
        kernel1 = '-1, -1, 1,-1, -1, 0,1, 0, 1'
        rank_list2 = util.update_rank_list('knl', kernel1, rank_list2)
        kernel2 = '-1, -1, 1,-1, -1, 0,1, 0, 1'
        rank_list2 = util.update_rank_list('knl', kernel2, rank_list2)
        self.assertIsNotNone(rank_list2)

    def test_get_top_rank(self):
        SPEED = 'spd'
        rank_list = np.array([])
        sp1 = util.get_top_rank(rank_list)
        self.assertIsNone(sp1)
        rank_list = np.array(
            [{SPEED: 1, util.USED_COUNT: 1}, {SPEED: 2, util.USED_COUNT: 2}, {SPEED: 3, util.USED_COUNT: 3}])
        rank_list = util.update_rank_list(SPEED, 3, rank_list)
        sp2 = util.get_top_rank(rank_list)
        # sometimes it will fail
        self.assertEquals(4, sp2[util.USED_COUNT])

    def test_matrix_to_string(self):
        kernel = np.array([[-1, -1, 1],
                           [-1, -1, 0],
                           [1, 0, 1]])
        kernel_str = util.matrix_to_string(kernel)
        self.assertEqual('-1,-1,1,-1,-1,0,1,0,1', kernel_str)

    def test_string_to_matrix(self):
        kernel_str = '-1,-1,1,-1,-1,0,1,0,1'
        matrix = util.string_to_feature_matrix(kernel_str)
        self.assertEqual((3, 3), matrix.shape)


if __name__ == "__main__":
    unittest.main()
