import constants
import memory
import time
from pynput.mouse import Button, Controller


class Reward(object):

    def __init__(self):
        return


def process(sequential_time_memories, key):
    reward = 0
    if key is constants.KEY_ALT:
        reward = 50
    elif key is constants.KEY_CTRL:
        reward = 100
    if reward > 0:
        add_reward_memory(sequential_time_memories, reward)


def add_reward_memory(sequential_time_memories, reward):
    action = {constants.PHYSICAL_MEMORY_TYPE: constants.ACTION_REWARD, constants.REWARD: reward}
    print 'added reward memory ', action
    action_memory = memory.add_physical_memory(action)
    slice_memory = memory.add_collection_memory(constants.SLICE_MEMORY, [action_memory], reward)
    sequential_time_memories[constants.SLICE_MEMORY].append(slice_memory)