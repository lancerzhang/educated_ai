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

    def test_get_strongest_energy_segment1(self):
        data = np.array([1, 2, 3, 4])
        self.assertEqual(7, sound.get_max_energy(data))

    def test_get_strongest_energy_segment2(self):
        data = np.array([1, 2, 4, 3])
        self.assertEqual(9, sound.get_max_energy(data))

    def test_get_strongest_energy_segment3(self):
        data = np.array([3, 2, 1])
        self.assertEqual(5, sound.get_max_energy(data))

    def test_mix_energy(self):
        energy1 = 200
        mem = self.database.add_sound({sound.FEATURE: sound.FEATURE_MFCC, sound.INDEX: 1, sound.ENERGY: energy1})
        energy2 = 100
        sound.mix_energy(energy2, [mem])
        result = self.database.get_memory(mem[memory.ID], False)
        self.assertEqual(150, result[sound.ENERGY])

    def test_mix_energy2(self):
        mem1 = self.database.add_sound({sound.FEATURE: sound.FEATURE_MFCC, sound.INDEX: 1, sound.ENERGY: 200})
        mem2 = self.database.add_sound({sound.FEATURE: sound.FEATURE_MFCC, sound.INDEX: 1, sound.ENERGY: 300})
        energy2 = 100
        sound.mix_energy(energy2, [mem1, mem2])
        result1 = self.database.get_memory(mem1[memory.ID], False)
        self.assertEqual(150, result1[sound.ENERGY])
        result2 = self.database.get_memory(mem2[memory.ID], False)
        self.assertEqual(200, result2[sound.ENERGY])

    def test_process_frame_feature_new(self):
        frame_working_memories = []
        mem1 = self.database.add_sound({sound.FEATURE: sound.FEATURE_MFCC, sound.INDEX: 0, sound.ENERGY: 200})
        current_data = np.array([-300, 20, 10])
        last_data = np.array([-200, 20, 10])
        sound.process_frame_mfcc_feature(frame_working_memories, current_data, last_data)
        self.assertEqual(1, len(frame_working_memories))

    def test_process_frame_feature_found(self):
        frame_working_memories = []
        mem1 = self.database.add_sound({sound.FEATURE: sound.FEATURE_MFCC, sound.INDEX: 0, sound.ENERGY: -200})
        current_data = np.array([-210, 20, 10])
        last_data = np.array([-200, 15, 5])
        sound.process_frame_mfcc_feature(frame_working_memories, current_data, last_data)
        self.assertEqual(1, len(frame_working_memories))
        result2 = self.database.get_memory(mem1[memory.ID], False)
        self.assertEqual(-205, result2[sound.ENERGY])


if __name__ == "__main__":
    unittest.main()
