import time
import unittest
from collections import deque

from src.timed_queue import TimedItem
from src.timed_queue import TimedQueue

time_unit = 1


class TestTimedQueue(unittest.TestCase):
    timed_queue = None
    item1 = None

    def setUp(self):
        tq = TimedQueue(5, 2, 3)
        data = deque()
        item1 = TimedItem(f'feature1')
        data.append(item1)
        tq.data = data
        self.item1 = item1
        self.timed_queue = tq

    def prepare_full_data(self):
        data = deque()
        for i in reversed(range(5)):
            item = TimedItem(f'feature{i}')
            item.time = time.time() - (i + 1) * time_unit
            data.append(item)
        self.timed_queue.data = data

    def test_init(self):
        self.assertRaises(RuntimeError, TimedQueue, 1, 2, 2)
        self.assertRaises(RuntimeError, TimedQueue, 2, 2, 2)

    def test_append(self):
        self.timed_queue.append('feature2')
        self.assertEqual(2, len(self.timed_queue))
        self.assertEqual(self.item1.item, self.timed_queue[0])
        self.assertTrue(self.timed_queue.data[1].time > self.timed_queue.data[0].time)
        tq2 = TimedQueue(10, 2, 3)
        tq2.extend(self.timed_queue.data)
        self.assertEqual(2, len(tq2))

    def test_pop_left_no_data(self):
        # test no data
        tq = TimedQueue(5, 2, 3)
        self.assertIsNone(tq.pop_left())

    def test_pop_left_not_enough_data(self):
        # test not enough duration to read
        self.assertIsNone(self.timed_queue.pop_left())

    def test_pop_left_split_by_duration(self):
        self.prepare_full_data()
        # test split by get duration
        items = self.timed_queue.pop_left()
        self.assertEqual(2, len(items))
        items = self.timed_queue.pop_left()
        self.assertEqual(2, len(items))
        items = self.timed_queue.pop_left()
        self.assertIsNone(items)

    def test_pop_left_split_by_count(self):
        self.prepare_full_data()
        items = self.timed_queue.pop_left()
        self.assertEqual(2, len(items))
        items = self.timed_queue.pop_left()
        self.assertEqual(2, len(items))
        items = self.timed_queue.pop_left()
        self.assertIsNone(items)

    def test_pop_left_in_one_go(self):
        self.prepare_full_data()
        self.timed_queue.pop_duration = self.timed_queue.total_duration
        self.timed_queue.total_duration += 0.1
        self.timed_queue.pop_count = 5
        items = self.timed_queue.pop_left()
        self.assertEqual(5, len(items))
        items = self.timed_queue.pop_left()
        self.assertIsNone(items)

    def test_clean(self):
        self.assertEqual(1, len(self.timed_queue))
        self.item1.time = time.time() - 6
        self.timed_queue.clean()
        self.assertEqual(0, len(self.timed_queue))
