import unittest, sound
import numpy as np


class TestSound(unittest.TestCase):

    def setUp(self):
        pass

    # def test_impress(self):
    #     y = np.load('hi1.npy')
    #     sound.phases.append(y)
    #     sound.impress()

    def test_get_strongest_energy_segment1(self):
        data = np.array([1, 2, 3, 4])
        self.assertEqual(7, sound.get_max_energy(data))

    def test_get_strongest_energy_segment2(self):
        data = np.array([1, 2, 4, 3])
        self.assertEqual(9, sound.get_max_energy(data))

    def test_get_strongest_energy_segment3(self):
        data = np.array([3,2,1])
        self.assertEqual(5, sound.get_max_energy(data))

if __name__ == "__main__":
    unittest.main()
