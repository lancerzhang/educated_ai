import memory, util, constants
import numpy as np

WORKLOAD_DATA = 'duration_data'

REWARD_DATA = 'reward_data'
SATISFIED_REWARD = 0.5


def init_status(status, dps):
    # if free in short time, find more detail, explore the world
    short_duration = [0] * 2 * dps
    # if free in middle time, try different flow, see which one is better (with higher reward)
    middle_duration = [0] * 15 * dps
    # if free in long time, clean up memories
    long_duration = [0] * 60 * dps
    rewards = [0] * 30 * dps
    status.update({WORKLOAD_DATA: {constants.SHORT_DURATION: short_duration}})
    status.update({WORKLOAD_DATA: {constants.MEDIUM_DURATION: middle_duration}})
    status.update({WORKLOAD_DATA: {constants.LONG_DURATION: long_duration}})
    status.update({constants.BUSY: {constants.SHORT_DURATION: False}})
    status.update({constants.BUSY: {constants.MEDIUM_DURATION: False}})
    status.update({constants.BUSY: {constants.LONG_DURATION: False}})
    status.update({REWARD_DATA: rewards})
    status.update({constants.REWARD: False})


def calculate_workload(status, dps, frames, flag):
    if frames > len(status[WORKLOAD_DATA][flag]) and util.list_avg(status[WORKLOAD_DATA][flag]) > dps * 0.8:
        status.update({constants.BUSY: {flag: True}})
    else:
        status.update({constants.BUSY: {flag: False}})


def calculate_reward(status, frames):
    if frames > len(status[REWARD_DATA]):
        max_reward = np.max(np.array(status[REWARD_DATA]))
        if max_reward > SATISFIED_REWARD:
            status[constants.REWARD] = True


def calculate_status(status, dps, frames):
    if len(status) == 0:
        init_status(status, dps)
    calculate_workload(status, dps, frames, constants.SHORT_DURATION)
    calculate_workload(status, dps, frames, constants.MEDIUM_DURATION)
    calculate_workload(status, dps, frames, constants.LONG_DURATION)


def find_max_reward(working_memories):
    rewards = [x[constants.REWARD] for x in working_memories]
    max_reward = np.max(np.array(rewards))
    return max_reward


def update_status(status, processing_time, working_memories):
    status[WORKLOAD_DATA][constants.SHORT_DURATION].pop(0)
    status[WORKLOAD_DATA][constants.SHORT_DURATION].append(processing_time)
    status[WORKLOAD_DATA][constants.MEDIUM_DURATION].pop(0)
    status[WORKLOAD_DATA][constants.MEDIUM_DURATION].append(processing_time)
    status[WORKLOAD_DATA][constants.LONG_DURATION].pop(0)
    status[WORKLOAD_DATA][constants.LONG_DURATION].append(processing_time)
    max_reward = find_max_reward(working_memories)
    status[REWARD_DATA].pop(0)
    status[REWARD_DATA].append(max_reward)
