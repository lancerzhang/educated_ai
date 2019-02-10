import constants
import logging


class Reward(object):

    def __init__(self, bm):
        self.bio_memory = bm

    def add_reward_memory(self, sequential_time_memories, new_reward):
        action = {constants.PHYSICAL_MEMORY_TYPE: constants.ACTION_REWARD, constants.REWARD: new_reward}
        logging.debug('added reward memory {0}'.format(action))
        action_memory = self.bio_memory.add_physical_memory(action)
        slice_memory = self.bio_memory.add_collection_memory(constants.SLICE_MEMORY, [action_memory], reward=new_reward)
        sequential_time_memories[constants.SLICE_MEMORY].append(slice_memory)

    def process(self, sequential_time_memories, key):
        reward = 0
        if key is constants.KEY_ALT:
            reward = 50
        elif key is constants.KEY_CTRL:
            reward = 100
        if reward > 0:
            self.add_reward_memory(sequential_time_memories, reward)
