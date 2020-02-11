from . import constants
from . import util
from .brain import Brain
from .memory import Memory
import logging

logger = logging.getLogger('Reward')
logger.setLevel(logging.INFO)


class Reward(object):

    @util.timeit
    def __init__(self, brain: Brain):
        self.brain = brain

    @util.timeit
    def add_reward_memory(self, reward):
        q = Memory()
        q.set_feature_type(constants.ACTION_REWARD)
        q.reward = reward
        m = self.brain.put_physical_memory(q)
        self.brain.put_slice_memory([m], constants.SLICE_MEMORY, constants.ACTION_REWARD, reward=reward)

    @util.timeit
    def process(self, key):
        reward = 0
        if key == constants.KEY_ALT:
            reward = 0.5
        elif key == constants.KEY_CTRL:
            reward = 1
        if reward > 0:
            self.add_reward_memory(reward)
