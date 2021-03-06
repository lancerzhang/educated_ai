import time
import unittest
from collections import deque

from src.memory_list import TimedItem
from src.memory_list import MemoryList

time_unit = 1


class TestTimedQueue(unittest.TestCase):
    timed_queue = None
    item1 = None

    def setUp(self):
        tq = MemoryList(5, 2, pop_count=2)
        data = deque()
        item1 = TimedItem(f'feature1')
        data.append(item1)
        tq.data = data
        self.item1 = item1
        self.timed_queue = tq

    def prepare_full_data(self):
        data = deque()
        created_time = time.time() - 5
        # print(f'prepare_full_data: created_time {created_time}')
        for i in reversed(range(5)):
            item = TimedItem(f'feature{i}')
            if (i + 1) % 2 == 1:
                created_time += 1.1
            else:
                created_time += 0.1
            item.created_time = created_time
            # print(created_time)
            data.append(item)
        self.timed_queue.data = data

    def test_init(self):
        self.assertRaises(RuntimeError, MemoryList, 1, 2, 2)
        self.assertRaises(RuntimeError, MemoryList, 2, 2, 2)

    def test_pop_left_no_data(self):
        # test no data
        tq = MemoryList(5, 2)
        self.assertIsNone(tq.pop_left())

    def test_pop_left_not_enough_count_and_duration(self):
        # test not enough duration to read
        self.assertIsNone(self.timed_queue.pop_left())

    def test_pop_left_not_enough_count(self):
        self.prepare_full_data()
        self.timed_queue.pop_count = 6
        self.timed_queue.pop_duration = 9999
        self.assertIsNone(self.timed_queue.pop_left())

    def test_pop_left_not_enough_duration(self):
        self.prepare_full_data()
        self.timed_queue.pop_count = 9999
        self.timed_queue.pop_duration = 6
        self.assertIsNone(self.timed_queue.pop_left())

    def test_pop_left_split_by_duration(self):
        self.prepare_full_data()
        self.timed_queue.pop_duration = 1
        self.timed_queue.pop_count = 9999
        # test split by get duration
        items = self.timed_queue.pop_left()
        self.assertEqual(2, len(items))
        items = self.timed_queue.pop_left()
        self.assertEqual(2, len(items))
        items = self.timed_queue.pop_left()
        self.assertEqual(1, len(items))

    def test_pop_left_split_by_count(self):
        self.prepare_full_data()
        self.timed_queue.pop_duration = 2
        self.timed_queue.pop_count = 2
        items = self.timed_queue.pop_left()
        self.assertEqual(2, len(items))
        items = self.timed_queue.pop_left()
        self.assertEqual(2, len(items))
        items = self.timed_queue.pop_left()
        self.assertIsNone(items)

    def test_pop_left_in_one_go(self):
        self.prepare_full_data()
        self.timed_queue.pop_duration = 3
        self.timed_queue.pop_count = 5
        items = self.timed_queue.pop_left()
        self.assertEqual(5, len(items))
        items = self.timed_queue.pop_left()
        self.assertIsNone(items)

    def test_pop_left_in_one_go_with_no_end_element(self):
        data = deque()
        created_time = time.time() - 8
        # print(f'prepare_full_data: created_time {created_time}')
        for i in reversed(range(5)):
            item = TimedItem(f'feature{i}')
            if (i + 1) % 2 == 1:
                created_time += 1.1
            else:
                created_time += 0.1
            item.created_time = created_time
            # print(created_time)
            data.append(item)
        self.timed_queue.data = data
        self.timed_queue.pop_duration = 6
        self.timed_queue.pop_count = 9999
        items = self.timed_queue.pop_left()
        self.assertIsNotNone(items)
        self.assertEqual(5, len(items))

    def test_pop_left_break_time(self):
        self.prepare_full_data()
        self.timed_queue.pop_duration = 2
        self.timed_queue.pop_count = 5
        self.timed_queue.break_time = 0.9
        items = self.timed_queue.pop_left()
        self.assertEqual(2, len(items))
        items = self.timed_queue.pop_left()
        self.assertEqual(2, len(items))
        items = self.timed_queue.pop_left()
        self.assertIsNone(items)

    def prepare_consecutive_duplicates(self):
        self.prepare_full_data()
        new_data = deque()
        for i in range(len(self.timed_queue.data)):
            item = self.timed_queue.data[i]
            if 0 < i < len(self.timed_queue.data) - 1:
                item.content = 'duplicates'
            new_data.append(item)
            # print(item.content)
        self.timed_queue.pop_duration = 3
        self.timed_queue.pop_count = 5

    def test_pop_left_consecutive_duplicates_true(self):
        self.prepare_consecutive_duplicates()
        items = self.timed_queue.pop_left()
        self.assertEqual(5, len(items))

    def test_pop_left_consecutive_duplicates_false(self):
        self.prepare_consecutive_duplicates()
        self.timed_queue.consecutive_duplicates = False
        items = self.timed_queue.pop_left()
        self.assertEqual(3, len(items))

    def test_delete_expired(self):
        self.assertEqual(1, len(self.timed_queue))
        self.item1.created_time = time.time() - 6
        self.timed_queue.delete_expired()
        self.assertEqual(0, len(self.timed_queue))
