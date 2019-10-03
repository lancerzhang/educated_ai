from components.storage import Storage
from components import constants
from components import memory
import time
import unittest


class TestStorage(unittest.TestCase):

    def setUp(self):
        pass

    def test_put_speed(self):
        SPEED = 'speed'
        storage = Storage()
        for i in range(0, 5):
            storage.put_item(SPEED, i)
        storage.put_item(SPEED, 4)
        self.assertEqual(4, storage.get_top(SPEED).key)
        self.assertEqual(2, storage.get_top(SPEED).count)


if __name__ == "__main__":
    unittest.main()
