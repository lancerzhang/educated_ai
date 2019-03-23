from components.bio_memory import BioMemory
from components.data_adaptor import DataAdaptor
from tinydb import TinyDB
from tinydb.storages import MemoryStorage
from components.data_tinydb import DataTinyDB
from components.sound import Sound
from components import constants
import numpy as np
import unittest


class TestSound(unittest.TestCase):
    database = None

    def setUp(self):
        database = DataTinyDB(TinyDB(storage=MemoryStorage))
        da = DataAdaptor(database)
        bm = BioMemory(da)
        bm.forget_memory = False
        self.bio_memory = bm
        self.sound = Sound(bm)

    def test_filter_feature(self):
        kernel1 = '-1,-1,1,-1,-1,0,1,0,1'
        # kernel1 = '0,0,0,0,1,0,0,0,0'
        # kernel1 = '-1,-1,-1,-1,8,-1,-1,-1,-1'
        # kernel1 = '1,0,-1,0,0,0,-1,0,1'
        data1_1 = np.load('sound1_1.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data1_1)
        frequency_map1_1 = self.sound.get_frequency_map(None)
        feature_data1_1 = self.sound.filter_feature(frequency_map1_1, kernel1)
        self.assertIsNotNone(feature_data1_1)
        data1_2 = np.load('sound1_2.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data1_2)
        frequency_map1_2 = self.sound.get_frequency_map(None)
        feature_data1_2 = self.sound.filter_feature(frequency_map1_2, kernel1, feature_data1_1[constants.FEATURE])
        self.assertTrue(feature_data1_2[constants.SIMILAR])

        data2_1 = np.load('sound2_1.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data2_1)
        frequency_map2_1 = self.sound.get_frequency_map(None)
        feature_data2_1 = self.sound.filter_feature(frequency_map2_1, kernel1)
        self.assertIsNotNone(feature_data2_1)
        data2_2 = np.load('sound2_2.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data2_2)
        frequency_map2_2 = self.sound.get_frequency_map(None)
        feature_data2_2 = self.sound.filter_feature(frequency_map2_2, kernel1, feature_data2_1[constants.FEATURE])
        self.assertTrue(feature_data2_2[constants.SIMILAR])

        data3_1 = np.load('sound3_1.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data3_1)
        frequency_map3_1 = self.sound.get_frequency_map()
        feature_data3_1 = self.sound.filter_feature(frequency_map3_1, kernel1)
        self.assertIsNotNone(feature_data3_1)
        data3_2 = np.load('sound3_2.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data3_2)
        frequency_map3_2 = self.sound.get_frequency_map()
        feature_data3_2 = self.sound.filter_feature(frequency_map3_2, kernel1, feature_data3_1[constants.FEATURE])
        self.assertTrue(feature_data3_2[constants.SIMILAR])

        data1_2 = np.load('sound1_2.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data1_2)
        frequency_map1_2 = self.sound.get_frequency_map()
        feature_data1_2 = self.sound.filter_feature(frequency_map1_2, kernel1)
        data2_2 = np.load('sound2_2.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data2_2)
        frequency_map2_2 = self.sound.get_frequency_map()
        feature_data2_2 = self.sound.filter_feature(frequency_map2_2, kernel1, feature_data1_2[constants.FEATURE])
        self.assertFalse(feature_data2_2[constants.SIMILAR])

        data1_2 = np.load('sound1_2.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data1_2)
        frequency_map1_2 = self.sound.get_frequency_map()
        feature_data1_2 = self.sound.filter_feature(frequency_map1_2, kernel1)
        data3_2 = np.load('sound3_2.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data3_2)
        frequency_map3_2 = self.sound.get_frequency_map()
        feature_data3_2 = self.sound.filter_feature(frequency_map3_2, kernel1, feature_data1_2[constants.FEATURE])
        self.assertFalse(feature_data3_2[constants.SIMILAR])

    def test_filter_feature2(self):
        kernel1 = '-1,-1,1,-1,-1,0,1,0,1'
        data1_2 = np.load('sound1_2.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data1_2)
        frequency_map1_2 = self.sound.get_frequency_map(None)
        feature_data1_2 = self.sound.filter_feature(frequency_map1_2, kernel1)
        data2_2 = np.load('sound2_2.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data2_2)
        frequency_map2_2 = self.sound.get_frequency_map(None)
        feature_data2_2 = self.sound.filter_feature(frequency_map2_2, kernel1)
        data3_2 = np.load('sound3_2.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data3_2)
        frequency_map3_2 = self.sound.get_frequency_map(None)
        feature_data3_2 = self.sound.filter_feature(frequency_map3_2, kernel1, feature_data1_2[constants.FEATURE])


if __name__ == "__main__":
    unittest.main()
