import numpy as np
from scipy.spatial.distance import euclidean


class EnergyDescriptor:
    MIN_ENERGY = 50
    MIN_DISTANCE = 0.1

    def describe(self, mfcc):
        energy = mfcc[0]
        if energy < self.MIN_ENERGY:
            return None
        else:
            return energy

    def compare(self, mfcc1, mfcc2):
        feature1 = self.describe(mfcc1)
        feature2 = self.describe(mfcc2)
        features = [feature1, feature2]
        if feature1 is None or feature2 is None:
            return None
        else:
            distance = abs(feature1 - feature2) / np.max(features)
            return distance

    def is_similar(self, mfcc1, mfcc2):
        distance = self.compare(mfcc1, mfcc2)
        if distance is not None and distance < self.MIN_DISTANCE:
            return True
        else:
            return False


class MfccNormalDescriptor:
    BLOCK_WIDTH = 2
    BLOCK_HEIGHT = 2
    MIN_ENERGY_UNIT = 10
    MIN_DISTANCE_UNIT = 0.1

    def describe(self, mfcc_block):
        h, w = mfcc_block.shape
        if np.sum(np.abs(mfcc_block)) > self.MIN_ENERGY_UNIT * h * w:
            return mfcc_block / np.abs(mfcc_block).max()
        else:
            return None

    def compare(self, mfcc_block1, mfcc_block2):
        feature1 = self.describe(mfcc_block1)
        feature2 = self.describe(mfcc_block2)
        if feature1 is None or feature2 is None:
            return None
        distance = euclidean(feature1[0], feature2[0]) + euclidean(feature1[1], feature2[1])
        return distance

    def is_similar(self, mfcc_block1, mfcc_block2):
        h1, w1 = mfcc_block1.shape
        h2, w2 = mfcc_block2.shape
        if h1 != h2 or w1 != w2 or h1 != self.BLOCK_HEIGHT or w1 != self.BLOCK_WIDTH:
            return False
        distance = self.compare(mfcc_block1, mfcc_block2)
        if distance is not None and distance < self.MIN_DISTANCE_UNIT * h1 * w1:
            return True
        else:
            return False
