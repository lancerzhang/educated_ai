from . import constants
from . import util
import logging

logger = logging.getLogger('Reward')
logger.setLevel(logging.INFO)


class Reward(object):

    @util.timeit
    def __init__(self, brain):
        self.brain = brain

    @util.timeit
    def add_reward_memory(self, new_reward):
        bm = self.brain.add_reward_memory(new_reward)
        self.brain.add_virtual_memory(constants.SLICE_MEMORY, [bm], reward=new_reward)

    @util.timeit
    def process(self, key):
        reward = 0
        if key == constants.KEY_ALT:
            reward = 50
        elif key == constants.KEY_CTRL:
            reward = 100
        if reward > 0:
            self.add_reward_memory(reward)
