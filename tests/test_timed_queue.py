import time
import unittest
from collections import deque

from src.timed_queue import TimedItem
from src.timed_queue import TimedQueue

time_unit = 1


class TestTimedQueue(unittest.TestCase):

    def test_init(self):
        self.assertRaises(RuntimeError, TimedQueue, 1, 2, 2)
        self.assertRaises(RuntimeError, TimedQueue, 2, 2, 2)

    def test_append(self):
        tq = TimedQueue(5, 2, 3)
        item1 = 'feature1'
        tq.append(item1)
        tq.append('feature2')
        self.assertEqual(2, len(tq))
        self.assertEqual(item1, tq[0])
        self.assertTrue(tq.data[1].time > tq.data[0].time)
        tq2 = TimedQueue(10, 2, 3)
        tq2.extend(tq.data)
        self.assertEqual(2, len(tq2))

    def test_pop_left(self):
        # test no data
        tq = TimedQueue(5 * time_unit, 2 * time_unit, 3)
        self.assertIsNone(tq.pop_left())
        # test not enough duration to read
        item1 = 'feature1'
        tq.append(item1)
        self.assertIsNone(tq.pop_left())
        # prepare full data
        data = deque()
        for i in reversed(range(5)):
            tt = TimedItem(f'feature{i}')
            tt.time = time.time() - (i + 1) * time_unit
            data.append(tt)
        tq.data = data.copy()
        # test split by get duration
        tts = tq.pop_left()
        self.assertEqual(2, len(tts))
        tts = tq.pop_left()
        self.assertEqual(2, len(tts))
        tts = tq.pop_left()
        self.assertIsNone(tts)
        # test split by get count
        tq = TimedQueue(5 * time_unit, 3 * time_unit, 2)
        tq.data = data.copy()
        tts = tq.pop_left()
        self.assertEqual(2, len(tts))
        tts = tq.pop_left()
        self.assertEqual(2, len(tts))
        tts = tq.pop_left()
        self.assertIsNone(tts)
        # test get all once
        tq = TimedQueue(5 * time_unit+0.1, 5 * time_unit, 5)
        tq.data = data.copy()
        tts = tq.pop_left()
        self.assertEqual(5, len(tts))
        tts = tq.pop_left()
        self.assertIsNone(tts)
