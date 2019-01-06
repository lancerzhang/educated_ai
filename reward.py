import constants
import logging
import memory
from pynput.mouse import Button, Controller

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')


class Reward(object):

    def __init__(self):
        return

    def add_reward_memory(self, sequential_time_memories, reward):
        action = {constants.PHYSICAL_MEMORY_TYPE: constants.ACTION_REWARD, constants.REWARD: reward}
        logging.debug('added reward memory {0}'.format(action))
        action_memory = memory.add_physical_memory(action)
        slice_memory = memory.add_collection_memory(constants.SLICE_MEMORY, [action_memory], reward)
        sequential_time_memories[constants.SLICE_MEMORY].append(slice_memory)

    def process(self, sequential_time_memories, key):
        reward = 0
        if key is constants.KEY_ALT:
            reward = 50
        elif key is constants.KEY_CTRL:
            reward = 100
        if reward > 0:
            self.add_reward_memory(sequential_time_memories, reward)
