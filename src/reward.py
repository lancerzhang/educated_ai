import logging

from . import constants
from . import util
from .brain import Brain
from .memory import Memory
from .memory import MemoryType
from .memory import FeatureTypes

logger = logging.getLogger('Reward')
logger.setLevel(logging.INFO)


class Reward(object):

    @util.timeit
    def __init__(self, brain: Brain):
        self.brain = brain

    @util.timeit
    def add_reward_memory(self, reward):
        q = Memory(MemoryType.REAL, feature_type=FeatureTypes.ACTION_REWARD)
        m = self.brain.put_memory(q)
        m.reward = reward  # TODO, reward as search?
        self.brain.compose_memory([m], MemoryType.SLICE, real_type=FeatureTypes.ACTION_REWARD, reward=reward)

    @util.timeit
    def process(self, key):
        reward = 0
        if key == constants.KEY_ALT:
            reward = 0.5
        elif key == constants.KEY_CTRL:
            reward = 1
        if reward > 0:
            self.add_reward_memory(reward)
