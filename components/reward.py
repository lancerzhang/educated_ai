from . import constants
import logging
import time

logger = logging.getLogger('Reward')
logger.setLevel(logging.INFO)


class Reward(object):

    def __init__(self, bm):
        self.bio_memory = bm

    def add_reward_memory(self, new_reward):
        start = time.time()
        bm = self.bio_memory.add_reward_memory(new_reward)
        self.bio_memory.add_virtual_memory(constants.SLICE_MEMORY, [bm], reward=new_reward)
        logger.info('add_reward_memory:{0}'.format(time.time() - start))

    def process(self, key):
        logging.debug('process')
        reward = 0
        if key == constants.KEY_ALT:
            reward = 50
        elif key == constants.KEY_CTRL:
            reward = 100
        if reward > 0:
            self.add_reward_memory(reward)
