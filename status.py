import constants
import logging
import util
import numpy as np

logger = logging.getLogger('status')
logger.setLevel(logging.DEBUG)

WORKLOAD_DATA = 'duration_data'
REWARD_DATA = 'reward_data'
SATISFIED_REWARD = 45


def init_status():
    pps = constants.process_per_second
    status = {}
    # if free in short time, find more detail, explore the world
    short_duration = [0] * 2 * pps
    # if free in middle time, try different flow, see which one is better (with higher reward)
    middle_duration = [0] * 15 * pps
    # if free in long time, clean up memories
    long_duration = [0] * 60 * pps
    # satisfied reward in 5 seconds
    rewards = [0] * 2 * pps
    status.update({WORKLOAD_DATA: {constants.SHORT_DURATION: short_duration, constants.MEDIUM_DURATION: middle_duration,
                                   constants.LONG_DURATION: long_duration}})
    status.update({constants.BUSY: {constants.SHORT_DURATION: False, constants.MEDIUM_DURATION: False,
                                    constants.LONG_DURATION: False}})
    status.update({REWARD_DATA: rewards})
    status.update({constants.REWARD: False})
    return status


def calculate_workload(status, dps, frames, flag):
    avg_workload = util.list_avg(status[WORKLOAD_DATA][flag])
    # logger.debug(' {0} status list is {1}'.format(flag, status[WORKLOAD_DATA][flag]))
    # logger.debug('{0} avg_workload is {1}'.format(flag, avg_workload))
    if frames > len(status[WORKLOAD_DATA][flag]) and avg_workload > dps:
        status[constants.BUSY].update({flag: True})
        # logger.debug('{0} status is busy.'.format(flag))
    else:
        status[constants.BUSY].update({flag: False})


def calculate_reward(status, frames):
    if frames > len(status[REWARD_DATA]):
        max_reward = np.max(np.array(status[REWARD_DATA]))
        logger.debug('max reward is {0} '.format(max_reward))
        if max_reward > SATISFIED_REWARD:
            status[constants.REWARD] = True
            logging.debug('reward is true.')
        else:
            status[constants.REWARD] = False


def calculate_status(status, dps, frames):
    # logger.debug('status is {0} '.format(status))
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
    working_memories_statistics(working_memories)


def working_memories_statistics(working_memories):
    if logger.getEffectiveLevel() is logging.DEBUG:
        # memory_survive_detail(working_memories)
        memory_survive_statistics(working_memories)
        memory_duration_statistics(working_memories)
        memory_recall_statistics(working_memories)
        memory_reward_statistics(working_memories)
        memory_status_statistics(working_memories)


def memory_status_statistics(working_memories):
    status_data = [mem[constants.STATUS] for mem in working_memories]
    status_dict = util.np_array_group_by_count(status_data)
    logger.debug('memory_status_statistics is {0}'.format(status_dict))


def memory_reward_statistics(working_memories):
    reward_data = [mem[constants.REWARD] for mem in working_memories]
    reward_dict = util.np_array_group_by_count(reward_data)
    logger.debug('memory_reward_statistics is {0}'.format(reward_dict))


def memory_recall_statistics(working_memories):
    recall_data = [mem[constants.RECALL] for mem in working_memories]
    recall_dict = util.np_array_group_by_count(recall_data)
    logger.debug('memory_recall_statistics is {0}'.format(recall_dict))


def memory_duration_statistics(working_memories):
    memory_duration_data = [mem[constants.MEMORY_DURATION] for mem in working_memories if
                            constants.MEMORY_DURATION in mem]
    memory_duration_dict = util.np_array_group_by_count(memory_duration_data)
    logger.debug('memory_duration_statistics is {0}'.format(memory_duration_dict))


def memory_survive_statistics(working_memories):
    memory_survive_data = [int(mem[constants.LAST_ACTIVE_TIME] - mem[constants.HAPPEN_TIME]) for mem in
                           working_memories if constants.HAPPEN_TIME in mem]
    memory_survive_dict = util.np_array_group_by_count(memory_survive_data)
    logger.debug('memory_survive_statistics is {0}'.format(memory_survive_dict))


def memory_survive_detail(working_memories):
    for mem in working_memories:
        # exclude expectation, which don't have happen time
        if constants.HAPPEN_TIME in mem:
            survive_time = mem[constants.LAST_ACTIVE_TIME] - mem[constants.HAPPEN_TIME]
            if survive_time > 10:
                logger.debug('{0} survive_time is {1}'.format(mem[constants.MID], survive_time))
                # logger.debug('survive working memory is {0}'.format(mem))
