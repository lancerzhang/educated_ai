import unittest, sound, memory
import numpy as np
from db import Database
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


class TestSound(unittest.TestCase):
    database = None

    def setUp(self):
        self.database = Database(TinyDB(storage=MemoryStorage))
        sound.db = self.database

    # def test_impress(self):
    #     y = np.load('hi1.npy')
    #     sound.phases.append(y)
    #     sound.impress()


if __name__ == "__main__":
    unittest.main()
