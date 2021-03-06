import random
import time
import unittest
from itertools import groupby

import numpy as np

from src import constants
from src import util
from src.memory import Memory


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
        list3 = util.np_array_concat(list1, list2)
        self.assertEqual(4, len(list3))

    def test_list_concat_empty(self):
        list1 = []
        list2 = [3, 4]
        list3 = util.np_array_concat(list1, list2)
        self.assertEqual(2, len(list3))

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
        self.assertEqual(2, util.list_avg(arr))

    def test_avg_float(self):
        arr = [1.5, 2.5, 3.5]
        self.assertEqual(2.5, util.list_avg(arr))

    def test_standardize_feature1(self):
        matrix = np.array([[0, 0, 0],
                           [0, 1, 2],
                           [0, 3, 4]])
        standard = util.standardize_feature(matrix)
        result = [[1, 2, 0],
                  [3, 4, 0],
                  [0, 0, 0]]
        self.assertEqual(result, standard.tolist())

    def test_standardize_feature2(self):
        matrix = np.array([[0, 0, 0],
                           [0, 0, 0],
                           [0, 0, 4]])
        standard = util.standardize_feature(matrix)
        result = [[4, 0, 0],
                  [0, 0, 0],
                  [0, 0, 0]]
        self.assertEqual(result, standard.tolist())

    def test_standardize_feature3(self):
        matrix = np.array([[0, 1, 2],
                           [0, 0, 0],
                           [0, 3, 4]])
        standard = util.standardize_feature(matrix)
        result = [[1, 2, 0],
                  [0, 0, 0],
                  [3, 4, 0]]
        self.assertEqual(result, standard.tolist())

    def test_standardize_feature3(self):
        matrix = np.array([[0, 1, 2],
                           [0, 3, 4],
                           [0, 0, 0]])
        standard = util.standardize_feature(matrix)
        result = [[1, 2, 0],
                  [3, 4, 0],
                  [0, 0, 0]]
        self.assertEqual(result, standard.tolist())

    def test_update_rank_list(self):
        SPEED = 'spd'
        rank_list = np.array(
            [{SPEED: 1, util.USED_COUNT: 1}, {SPEED: 2, util.USED_COUNT: 2}, {SPEED: 3, util.USED_COUNT: 3}])
        rank_list = util.update_rank_list(SPEED, 3, rank_list)
        self.assertEqual(3, len(rank_list))
        self.assertEqual(4, rank_list[0][util.USED_COUNT])
        rank_list = util.update_rank_list(SPEED, 4, rank_list)
        self.assertEqual(4, len(rank_list))
        rank_list2 = np.array([])
        kernel0 = '1, -1, 1,-1, -1, 0, 1, 0, 1'
        rank_list2 = util.update_rank_list('knl', kernel0, rank_list2)
        kernel1 = '-1, -1, 1,-1, -1, 0, 1, 0, 1'
        rank_list2 = util.update_rank_list('knl', kernel1, rank_list2)
        kernel2 = '-1, -1, 1,-1, -1, 0, 1, 0, 1'
        rank_list2 = util.update_rank_list('knl', kernel2, rank_list2)
        self.assertEqual(2, rank_list2[0][util.USED_COUNT])

    def test_get_high_rank(self):
        SPEED = 'spd'
        rank_list = np.array([])
        sp1 = util.get_high_rank(rank_list)
        self.assertIsNone(sp1)
        rank_list = np.array(
            [{SPEED: 1, util.USED_COUNT: 1}, {SPEED: 2, util.USED_COUNT: 2}, {SPEED: 3, util.USED_COUNT: 3}])
        rank_list = util.update_rank_list(SPEED, 3, rank_list)
        sp2 = util.get_high_rank(rank_list)
        # sometimes it will fail
        print("Don't be panic, this case has 10% chance of failure!")
        self.assertGreater(sp2[util.USED_COUNT], 0)

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

    def test_matrix_diff(self):
        arr1 = np.array([[0, 1], [2, 3]])
        arr2 = np.array([[0, 1], [2, 3]])
        difference = util.np_matrix_diff(arr1, arr2)
        self.assertEqual(0, util.list_avg(difference))
        arr3 = np.array([[5, 1], [2, 3]])
        arr4 = np.array([[1, 1], [2, 3]])
        difference2 = util.np_matrix_diff(arr3, arr4)
        self.assertEqual(0.2, util.list_avg(difference2))

    def test_find_2d_index(self):
        tuple = util.find_2d_index(0, 2)
        self.assertEqual(0, tuple[0])
        self.assertEqual(0, tuple[1])
        tuple = util.find_2d_index(1, 2)
        self.assertEqual(1, tuple[0])
        self.assertEqual(0, tuple[1])
        tuple = util.find_2d_index(2, 2)
        self.assertEqual(0, tuple[0])
        self.assertEqual(1, tuple[1])
        tuple = util.find_2d_index(3, 2)
        self.assertEqual(1, tuple[0])
        self.assertEqual(1, tuple[1])
        tuple = util.find_2d_index(4, 2)
        self.assertEqual(0, tuple[0])
        self.assertEqual(2, tuple[1])

    def test_list_equal_no_order(self):
        a1 = ['ab', 'cd']
        a2 = ['ab', 'cd']
        self.assertTrue(util.list_equal_no_order(a1, a2))
        a3 = ['cd', 'ab']
        self.assertTrue(util.list_equal_no_order(a1, a3))
        a4 = ['aa']
        self.assertFalse(util.list_equal_no_order(a1, a4))
        a5 = ['ab', 'cd', 'aa']
        self.assertFalse(util.list_equal_no_order(a1, a5))
        a6 = []
        self.assertFalse(util.list_equal_no_order(a1, a6))
        self.assertFalse(util.list_equal_no_order(a6, a1))
        a7 = []
        self.assertTrue(util.list_equal_no_order(a6, a7))
        a8 = ['ab', 'cd', 'cd']
        self.assertFalse(util.list_equal_no_order(a1, a8))

    def test_list_equal_order(self):
        a1 = ['ab', 'cd']
        a2 = ['ab', 'cd']
        self.assertTrue(util.list_equal_order(a1, a2))
        a3 = ['cd', 'ab']
        self.assertFalse(util.list_equal_order(a1, a3))

    def test_np_array_all_same(self):
        a1 = np.array([1, 2])
        self.assertFalse(util.np_array_all_same(a1))
        a1 = np.array([2, 2])
        self.assertTrue(util.np_array_all_same(a1))

    def test_list_remove_duplicates(self):
        l1 = [1, 2, 3]
        self.assertEqual(3, len(util.list_remove_duplicates(l1)))
        l2 = [1, 2, 3, 2, 1]
        self.assertEqual(3, len(util.list_remove_duplicates(l2)))

    def test_list_element_count(self):
        l1 = [1, 2, 2, 3, 3, 3]
        d1 = util.list_element_count(l1)
        self.assertEqual(2, d1.get(2))
        l1 = ['a', 'b', 'b', 'c', 'c', 'c']
        d1 = util.list_element_count(l1)
        self.assertEqual(3, d1.get('c'))

    def test_group_collection_perf(self):
        s1 = set()
        for i in range(100 * 100):
            s1.add(random.randint(0, 99))
        t1 = time.time()
        l1 = list(s1)
        l1.sort(key=lambda x: x)
        g1 = groupby(l1, lambda x: x)
        t2 = time.time()
        for i in range(100):
            temp = []
            for e in s1:
                if e == i:
                    temp.append(e)
        t3 = time.time()
        d1 = t2 - t1
        d2 = t3 - t2
        # print(f'{d1}, {d2}')
        self.assertTrue(d2 > d1)

    def test_dict_set_add(self):
        d1 = {}
        k1 = 1
        v1 = 'a'
        util.dict_set_add(d1, k1, v1)
        self.assertEqual(1, len(d1.get(k1)))
        k2 = 1
        v2 = 'a'
        util.dict_set_add(d1, k2, v2)
        self.assertEqual(1, len(d1.get(k1)))
        k3 = 1
        v3 = 'b'
        util.dict_set_add(d1, k3, v3)
        self.assertEqual(2, len(d1.get(k1)))
        k4 = 2
        v4 = 'b'
        util.dict_set_add(d1, k4, v4)
        self.assertEqual(2, len(d1.get(k1)))
        self.assertEqual(1, len(d1.get(k4)))

    def test_list_continue_combination(self):
        list1 = [1]
        result1 = util.list_continuous_combination(list1, 1)
        self.assertEqual(1, len(result1))
        result1 = util.list_continuous_combination(list1, 2)
        self.assertEqual(0, len(result1))
        list1 = [1, 2]
        result1 = util.list_continuous_combination(list1, 1)
        self.assertEqual(2, len(result1))
        list1 = [1, 2]
        result1 = util.list_continuous_combination(list1, 2)
        self.assertEqual(1, len(result1))
        list1 = [1, 2, 3]
        result1 = util.list_continuous_combination(list1, 1)
        self.assertEqual(3, len(result1))
        list1 = [1, 2, 3]
        result1 = util.list_continuous_combination(list1, 2)
        self.assertEqual(2, len(result1))
        list1 = [1, 2, 3]
        result1 = util.list_continuous_combination(list1, 3)
        self.assertEqual(1, len(result1))
        list1 = [1, 2, 3, 4]
        result1 = util.list_continuous_combination(list1, 1)
        self.assertEqual(4, len(result1))
        list1 = [1, 2, 3, 4]
        result1 = util.list_continuous_combination(list1, 2)
        self.assertEqual(3, len(result1))
        list1 = [1, 2, 3, 4]
        result1 = util.list_continuous_combination(list1, 3)
        self.assertEqual(2, len(result1))
        list1 = [1, 2, 3, 4]
        result1 = util.list_continuous_combination(list1, 4)
        self.assertEqual(1, len(result1))
        list1 = ['a', 'b', 'c', 'c']
        result1 = util.list_continuous_combination(list1, 3)
        self.assertEqual(2, len(result1))

    def test_test_list_continue_combinations(self):
        list1 = [1, 2, 3, 4]
        result1 = util.list_combinations(list1, True)
        # print(result1)
        self.assertEqual(10, len(result1))
        result1 = util.list_combinations(list1, False)
        # print(result1)
        self.assertEqual(15, len(result1))

    def test_greater_than_half(self):
        self.assertTrue(util.greater_than_half(1, 1))
        self.assertTrue(util.greater_than_half(2, 2))
        self.assertTrue(util.greater_than_half(2, 3))
        self.assertTrue(util.greater_than_half(3, 3))
        self.assertTrue(util.greater_than_half(3, 4))
        self.assertTrue(util.greater_than_half(4, 4))
        self.assertFalse(util.greater_than_half(1, 2))
        self.assertFalse(util.greater_than_half(1, 3))
        self.assertFalse(util.greater_than_half(1, 4))
        self.assertFalse(util.greater_than_half(2, 4))

    def test_get_order(self):
        self.assertEqual(constants.disorder, util.get_order(constants.pack))
        self.assertEqual(constants.disorder, util.get_order(constants.pack_real))
        self.assertEqual(constants.disorder, util.get_order(constants.link))
        self.assertEqual(constants.disorder, util.get_order(constants.instant))
        self.assertEqual(constants.disorder, util.get_order(constants.short))

    def test_is_sublist(self):
        self.assertTrue(util.is_sublist([1], [1, 2]))
        self.assertTrue(util.is_sublist([1, 2], [1, 2]))
        self.assertTrue(util.is_sublist([2, 3], [1, 2, 3]))
        self.assertTrue(util.is_sublist([3], [1, 2, 3]))
        self.assertFalse(util.is_sublist([], [1, 2]))
        self.assertFalse(util.is_sublist([], []))
        self.assertFalse(util.is_sublist([1, 2], [1, 3, 2]))

    def test_is_subset(self):
        self.assertTrue(util.is_subset({1}, {1, 2}))
        self.assertTrue(util.is_subset({1, 2}, {1, 2}))
        self.assertTrue(util.is_subset({2, 3}, {1, 2, 3}))
        self.assertTrue(util.is_subset({3}, {1, 2, 3}))
        self.assertFalse(util.is_subset(set(), {1, 2}))
        self.assertFalse(util.is_subset(set(), set()))
        self.assertTrue(util.is_subset({1, 2}, {1, 3, 2}))

    def test_create_data(self):
        m1 = Memory(constants.short, [])
        m2 = Memory(constants.short, [])
        data = util.create_data(constants.long, [m1, m2])
        self.assertEqual(2, len(data))
        self.assertEqual(int, type(data.pop()))


if __name__ == "__main__":
    unittest.main()
