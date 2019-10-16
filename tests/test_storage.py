from components.storage import Storage
from components import constants
from components import memory
import time
import unittest


class TestStorage(unittest.TestCase):

    def setUp(self):
        pass

    def test_put_speed(self):
        _speed = 'speed'
        storage = Storage()
        for i in range(0, 5):
            storage.update(_speed, i)
        storage.update(_speed, 4)
        self.assertEqual(4, storage.top(_speed).key)
        self.assertEqual(2, storage.top(_speed).count)


if __name__ == "__main__":
    unittest.main()
