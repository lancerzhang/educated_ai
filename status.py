import time, numpy, cv2, memory
import numpy as np

WORKLOAD_DATA = 'duration_data'
BUSY = 'busy'
SHORT_DURATION = 'S'
MEDIUM_DURATION = 'M'
LONG_DURATION = 'L'
REWARD_DATA = 'reward_data'
REWARD = 'reward'
SATISFIED_REWARD = 0.5


def init_status(status, PPS):
    if len(status) == 0:
        # if free in short time, find more detail, explore the world
        short_duration = [0] * 2 * PPS
        # if free in middle time, try different flow, see which one is better (with higher reward)
        middle_duration = [0] * 15 * PPS
        # if free in long time, clean up memories
        long_duration = [0] * 60 * PPS
        rewards = [0] * 30 * PPS
        status.update({WORKLOAD_DATA: {SHORT_DURATION: short_duration}})
        status.update({WORKLOAD_DATA: {MEDIUM_DURATION: middle_duration}})
        status.update({WORKLOAD_DATA: {LONG_DURATION: long_duration}})
        status.update({BUSY: {SHORT_DURATION: False}})
        status.update({BUSY: {MEDIUM_DURATION: False}})
        status.update({BUSY: {LONG_DURATION: False}})
        status.update({REWARD_DATA: rewards})
        status.update({REWARD: False})


def calculate_workload(status, DPS, frames, flag):
    if frames > len(status[WORKLOAD_DATA][flag]) and avg(status[WORKLOAD_DATA][flag]) > DPS * 0.8:
        status.update({BUSY: {flag: True}})
    else:
        status.update({BUSY: {flag: False}})


def calculate_reward(status, frames):
    if frames > len(status[REWARD_DATA]):
        max_reward = np.max(np.array(status[REWARD_DATA]))
        if max_reward > SATISFIED_REWARD:
            status[REWARD] = True


def calculate_status(status, DPS, frames):
    if len(init_status) == 0:
        init_status(status, DPS)
    calculate_workload(status, DPS, frames, SHORT_DURATION)
    calculate_workload(status, DPS, frames, MEDIUM_DURATION)
    calculate_workload(status, DPS, frames, LONG_DURATION)


def find_max_reward(working_memories):
    rewards = [x[memory.REWARD] for x in working_memories]
    max_reward = np.max(np.array(rewards))
    return max_reward


def update_status(status, processing_time, working_memories):
    status[WORKLOAD_DATA][SHORT_DURATION].pop(0)
    status[WORKLOAD_DATA][SHORT_DURATION].append(processing_time)
    status[WORKLOAD_DATA][MEDIUM_DURATION].pop(0)
    status[WORKLOAD_DATA][MEDIUM_DURATION].append(processing_time)
    status[WORKLOAD_DATA][LONG_DURATION].pop(0)
    status[WORKLOAD_DATA][LONG_DURATION].append(processing_time)
    max_reward = find_max_reward(working_memories)
    status[REWARD_DATA].pop(0)
    status[REWARD_DATA].append(max_reward)
