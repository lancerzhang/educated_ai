import memory, util, constants
import numpy as np

WORKLOAD_DATA = 'duration_data'

REWARD_DATA = 'reward_data'
SATISFIED_REWARD = 0.5


def init_status():
    pps = constants.process_per_second
    status = {}
    # if free in short time, find more detail, explore the world
    short_duration = [0] * 2 * pps
    # if free in middle time, try different flow, see which one is better (with higher reward)
    middle_duration = [0] * 15 * pps
    # if free in long time, clean up memories
    long_duration = [0] * 60 * pps
    rewards = [0] * 30 * pps
    status.update({WORKLOAD_DATA: {constants.SHORT_DURATION: short_duration, constants.MEDIUM_DURATION: middle_duration,
                                   constants.LONG_DURATION: long_duration}})
    status.update({constants.BUSY: {constants.SHORT_DURATION: False, constants.MEDIUM_DURATION: False,
                                    constants.LONG_DURATION: False}})
    status.update({REWARD_DATA: rewards})
    status.update({constants.REWARD: False})
    return status


def calculate_workload(status, dps, frames, flag):
    avg_workload = util.list_avg(status[WORKLOAD_DATA][flag])
    if frames > len(status[WORKLOAD_DATA][flag]) and avg_workload > dps * 0.8:
        status[constants.BUSY].update({flag: True})
    else:
        status[constants.BUSY].update({flag: False})


def calculate_reward(status, frames):
    if frames > len(status[REWARD_DATA]):
        max_reward = np.max(np.array(status[REWARD_DATA]))
        if max_reward > SATISFIED_REWARD:
            status[constants.REWARD] = True
        else:
            status[constants.REWARD] = False


def calculate_status(status, dps, frames):
#    print status[constants.REWARD]
    calculate_workload(status, dps, frames, constants.SHORT_DURATION)
    calculate_workload(status, dps, frames, constants.MEDIUM_DURATION)
    calculate_workload(status, dps, frames, constants.LONG_DURATION)
    calculate_reward(status, frames)


def find_max_reward(working_memories):
    max_reward = 0
    rewards = [x[constants.REWARD] for x in working_memories]
    if len(rewards) > 0:
        max_reward = np.max(np.array(rewards))
    return max_reward


def update_status(working_memories, status, processing_time):
    status[WORKLOAD_DATA][constants.SHORT_DURATION].pop(0)
    status[WORKLOAD_DATA][constants.SHORT_DURATION].append(processing_time)
    status[WORKLOAD_DATA][constants.MEDIUM_DURATION].pop(0)
    status[WORKLOAD_DATA][constants.MEDIUM_DURATION].append(processing_time)
    status[WORKLOAD_DATA][constants.LONG_DURATION].pop(0)
    status[WORKLOAD_DATA][constants.LONG_DURATION].append(processing_time)
    max_reward = find_max_reward(working_memories)
    status[REWARD_DATA].pop(0)
    status[REWARD_DATA].append(max_reward)
