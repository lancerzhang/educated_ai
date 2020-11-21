import unittest

import numpy as np

from components import favor
from components.brain import Brain
from components.favor import Favor
from components.featurepack import FeaturePack
from components.memory import Memory
from components.memory import MemoryStatus
from components.memory import MemoryType
from components.memory import FeatureTypes
from components.voice import Voice


class TestSound(unittest.TestCase):
    database = None

    def setUp(self):
        brain1 = Brain()
        favor.FAVOR_FILE = 'favor.npy'
        favor1 = Favor()
        self.sound = Voice(brain1, favor1)

    def test_filter_feature(self):
        kernel1 = '-1,-1,1,-1,-1,0,1,0,1'
        # kernel1 = '0,0,0,0,1,0,0,0,0'
        # kernel1 = '-1,-1,-1,-1,8,-1,-1,-1,-1'
        # kernel1 = '1,0,-1,0,0,0,-1,0,1'
        data1_1 = np.load('sound1_1.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data1_1)
        fp11 = self.sound.filter_feature(FeaturePack(kernel=kernel1))
        self.assertIsNotNone(fp11)
        data1_2 = np.load('sound1_2.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data1_2)
        fp12 = self.sound.filter_feature(FeaturePack(kernel=kernel1, contrast=fp11.feature))
        self.assertTrue(fp12.similar)
        data2_1 = np.load('sound2_1.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data2_1)
        fp21 = self.sound.filter_feature(FeaturePack(kernel=kernel1))
        self.assertIsNotNone(fp21)
        data2_2 = np.load('sound2_2.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data2_2)
        fp22 = self.sound.filter_feature(FeaturePack(kernel=kernel1, contrast=fp21.feature))
        # self.assertTrue(fp22.similar)
        data3_1 = np.load('sound3_1.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data3_1)
        fp31 = self.sound.filter_feature(FeaturePack(kernel=kernel1))
        self.assertIsNotNone(fp31)
        data3_2 = np.load('sound3_2.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data3_2)
        fp32 = self.sound.filter_feature(FeaturePack(kernel=kernel1, contrast=fp31.feature))
        # self.assertTrue(fp32.similar)
        data1_2 = np.load('sound1_2.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data1_2)
        fp12 = self.sound.filter_feature(FeaturePack(kernel=kernel1))
        data2_2 = np.load('sound2_2.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data2_2)
        fp22 = self.sound.filter_feature(FeaturePack(kernel=kernel1, contrast=fp12.feature))
        # self.assertFalse(fp22.similar)
        data1_2 = np.load('sound1_2.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data1_2)
        fp12 = self.sound.filter_feature(FeaturePack(kernel=kernel1))
        data3_2 = np.load('sound3_2.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data3_2)
        fp32 = self.sound.filter_feature(FeaturePack(kernel=kernel1, contrast=fp12.feature))
        # self.assertFalse(fp32.similar)

    def test_filter_feature2(self):
        kernel1 = '-1,-1,1,-1,-1,0,1,0,1'
        data1_2 = np.load('sound1_2.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data1_2)
        fp12 = self.sound.filter_feature(FeaturePack(kernel=kernel1))
        data2_2 = np.load('sound2_2.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data2_2)
        fp22 = self.sound.filter_feature(FeaturePack(kernel=kernel1))
        data3_2 = np.load('sound3_2.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data3_2)
        fp32 = self.sound.filter_feature(FeaturePack(kernel=kernel1, contrast=fp12.feature))

    def test_match_features(self):
        kernel1 = '-1,-1,1,-1,-1,0,1,0,1'
        data1_1 = np.load('sound1_1.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data1_1)
        fp11 = self.sound.filter_feature(FeaturePack(kernel=kernel1))
        m1 = Memory(MemoryType.REAL, real_type=FeatureTypes.voice, kernel=fp11.kernel, feature=fp11.feature)
        m1.status = MemoryStatus.MATCHING
        self.sound.brain.categorized_memory = {m1}
        self.sound.brain.active_memories = {m1}
        self.sound.brain.reindex()
        data1_2 = np.load('sound1_2.npy')
        self.sound.previous_phase = np.array([])
        self.sound.phases.append(data1_2)
        self.sound.match_features()
        self.assertEqual(MemoryStatus.MATCHED, m1.status)


if __name__ == "__main__":
    unittest.main()
