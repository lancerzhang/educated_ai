import unittest

from components.favor import Favor


class TestFavor(unittest.TestCase):

    def setUp(self):
        pass

    def test_put_speed(self):
        _speed = 'speed'
        favor = Favor()
        for i in range(0, 5):
            favor.update(_speed, i)
        favor.update(_speed, 4)
        self.assertEqual(4, favor.top(_speed).key)
        self.assertEqual(2, favor.top(_speed).count)

    def test_save_load(self):
        _vuk = "vuk"
        _suk = "suk"
        _speed = 'speed'
        _degrees = "degrees"
        _channel = "channel"
        favor = Favor()
        favor.update(_vuk, "111")
        favor.update(_suk, "222")
        favor.update(_speed, 300)
        favor.update(_degrees, 36)
        favor.update(_channel, "y")
        favor.save()
        favor2 = Favor()
        favor2.load()
        self.assertEqual("111", favor2.top(_vuk).key)
        self.assertEqual("222", favor2.top(_suk).key)
        self.assertEqual(300, favor2.top(_speed).key)
        self.assertEqual(36, favor2.top(_degrees).key)
        self.assertEqual("y", favor2.top(_channel).key)


if __name__ == "__main__":
    unittest.main()
