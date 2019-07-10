from . import constants
import logging
from . import util
import numpy as np
import time

logger = logging.getLogger('status')
logger.setLevel(logging.INFO)


class Status(object):
    WORKLOAD_DATA = 'duration_data'
    REWARD_DATA = 'reward_data'
    AVG = 'average'
    SATISFIED_REWARD = 45

    @util.timeit
    def __init__(self, bm):
        self.bio_memory = bm
        self.video_frame = 0
        self.video_fps = 0
        pps = constants.process_per_second
        all_status = {}
        # if free in short time, find more detail, explore the world
        short_duration = [0] * 2 * pps
        # if free in middle time, try different flow, see which one is better (with higher reward)
        middle_duration = [0] * 15 * pps
        # if free in long time, clean up memories
        long_duration = [0] * 60 * pps
        # satisfied reward in 5 seconds
        rewards = [0] * 2 * pps
        all_status.update(
            {self.WORKLOAD_DATA: {constants.SHORT_DURATION: short_duration, constants.MEDIUM_DURATION: middle_duration,
                                  constants.LONG_DURATION: long_duration}})
        all_status.update({constants.BUSY: {constants.SHORT_DURATION: False, constants.MEDIUM_DURATION: False,
                                            constants.LONG_DURATION: False}})
        all_status.update(
            {self.AVG: {constants.SHORT_DURATION: 0.1, constants.MEDIUM_DURATION: 0.1, constants.LONG_DURATION: 0.1}})
        all_status.update({self.REWARD_DATA: rewards})
        all_status.update({constants.REWARD: False})
        self.status = all_status

    @util.timeit
    def calculate_workload(self, dps, frames, flag):
        avg_workload = util.list_avg(self.status[self.WORKLOAD_DATA][flag])
        self.status[self.AVG][flag] = avg_workload
        # logger.debug(' {0} status list is {1}'.format(flag, status[self.WORKLOAD_DATA][flag]))
        # logger.debug('{0} avg_workload is {1}'.format(flag, avg_workload))
        if frames > len(self.status[self.WORKLOAD_DATA][flag]) and avg_workload > dps:
            self.status[constants.BUSY].update({flag: True})
            # logger.debug('{0} status is busy.'.format(flag))
        else:
            self.status[constants.BUSY].update({flag: False})

    @util.timeit
    def calculate_reward(self, frames):
        if frames > len(self.status[self.REWARD_DATA]):
            max_reward = np.max(np.array(self.status[self.REWARD_DATA]))
            # logger.debug('max reward is {0} '.format(max_reward))
            if max_reward > self.SATISFIED_REWARD:
                self.status[constants.REWARD] = True
                # logging.debug('reward is true.')
            else:
                self.status[constants.REWARD] = False

    @util.timeit
    def calculate_status(self, dps, frames):
        # logger.debug('status is {0} '.format(status))
        self.calculate_workload(dps, frames, constants.SHORT_DURATION)
        self.calculate_workload(dps, frames, constants.MEDIUM_DURATION)
        self.calculate_workload(dps, frames, constants.LONG_DURATION)
        self.calculate_reward(frames)

    @util.timeit
    def find_max_reward(self):
        max_reward = 0
        rewards = [x[constants.REWARD] for x in self.bio_memory.working_memories]
        if len(rewards) > 0:
            max_reward = np.max(np.array(rewards))
        return max_reward

    @util.timeit
    def update_status(self, processing_time):
        self.status[self.WORKLOAD_DATA][constants.SHORT_DURATION].pop(0)
        self.status[self.WORKLOAD_DATA][constants.SHORT_DURATION].append(processing_time)
        self.status[self.WORKLOAD_DATA][constants.MEDIUM_DURATION].pop(0)
        self.status[self.WORKLOAD_DATA][constants.MEDIUM_DURATION].append(processing_time)
        self.status[self.WORKLOAD_DATA][constants.LONG_DURATION].pop(0)
        self.status[self.WORKLOAD_DATA][constants.LONG_DURATION].append(processing_time)
        max_reward = self.find_max_reward()
        self.status[self.REWARD_DATA].pop(0)
        self.status[self.REWARD_DATA].append(max_reward)
        self.working_memories_statistics()

    @util.timeit
    def working_memories_statistics(self):
        if logger.getEffectiveLevel() is logging.DEBUG:
            # memory_survive_detail(working_memoriess)
            self.memory_survive_statistics()
            self.memory_duration_statistics()
            self.memory_recall_statistics()
            self.memory_reward_statistics()
            self.memory_status_statistics()

    @util.timeit
    def memory_status_statistics(self):
        status_data = [mem[constants.STATUS] for mem in self.bio_memory.working_memories]
        status_dict = util.np_array_group_by_count(status_data)

    @util.timeit
    def memory_reward_statistics(self):
        reward_data = [mem[constants.REWARD] for mem in self.bio_memory.working_memories]
        reward_dict = util.np_array_group_by_count(reward_data)

    @util.timeit
    def memory_recall_statistics(self):
        recall_data = [mem[constants.RECALL_COUNT] for mem in self.bio_memory.working_memories]
        recall_dict = util.np_array_group_by_count(recall_data)

    @util.timeit
    def memory_duration_statistics(self):
        memory_duration_data = [mem[constants.VIRTUAL_MEMORY_TYPE] for mem in self.bio_memory.working_memories if
                                constants.VIRTUAL_MEMORY_TYPE in mem]
        memory_duration_dict = util.np_array_group_by_count(memory_duration_data)

    @util.timeit
    def memory_survive_statistics(self):
        memory_survive_data = [int(mem[constants.LAST_ACTIVE_TIME] - mem[constants.HAPPEN_TIME]) for mem in
                               self.bio_memory.working_memories if constants.HAPPEN_TIME in mem]
        memory_survive_dict = util.np_array_group_by_count(memory_survive_data)

    @util.timeit
    def memory_survive_detail(self):
        for mem in self.bio_memory.working_memories:
            # exclude expectation, which don't have happen time
            if constants.HAPPEN_TIME in mem:
                survive_time = mem[constants.LAST_ACTIVE_TIME] - mem[constants.HAPPEN_TIME]
                # if survive_time > 10:
                #     logger.debug('{0} survive_time is {1}'.format(mem[constants.MID], survive_time))
                    # logger.debug('survive working memory is {0}'.format(mem))
