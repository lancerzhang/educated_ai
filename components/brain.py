from components.memory import Memory
from components.memory import MemoryType
from components.memory import MemoryStatus
from components import dashboard
from components import memory
from components import util
from collections import deque
from itertools import combinations
from multiprocessing import Pool
import logging
import numpy as np
import traceback
import time

logger = logging.getLogger('Brain')
logger.setLevel(logging.DEBUG)

FEATURE_SIMILARITY_THRESHOLD = 0.2
ACTIVE_LONG_MEMORY_LIMIT = 100
ASSOCIATE_MEMORY_LIMIT = 10
MEMORIES_NUM = 100 * 100 * 10
MEMORIES_CLEANUP_NUM = 100 * 100 * 11

MEMORY_FILE = 'data/memory.npy'


def children_combinations(memories, width):
    if len(memories) < width or len(memories) == 0:
        return []
    memory_type = memories[0].memory_type
    memory_id_list = [x.mid for x in memories]
    if memory_type is MemoryType.REAL:
        return combinations(memory_id_list, width)
    else:
        return util.list_continuous_combination(memory_id_list, width)


class Brain:

    def __init__(self):
        self.counter = 0
        self.memories = set()
        self.memory_indexes = {}  # speed up searching memories
        self.work_memories = []
        self.active_memories = set()
        self.temp_set1 = set()  # speed up searching active memories
        self.temp_set2 = set()
        work_feature_memories = []
        for i in range(0, memory.MEMORY_FEATURES_LENGTH):
            work_feature_memories.append(deque(maxlen=memory.COMPOSE_NUMBER))
        self.work_memories.append(work_feature_memories)
        for i in range(1, memory.MEMORY_TYPES_LENGTH):
            self.work_memories.append(deque(maxlen=memory.COMPOSE_NUMBER))
        self.pool = Pool()

    @util.timeit
    def associate(self):
        for memory_type in reversed(range(memory.MEMORY_TYPES_LENGTH - 1)):
            memories = [x for x in self.active_memories if
                        x.memory_type == memory_type and x.status is MemoryStatus.LIVING]
            logger.debug(f'memory_type:{memory_type}')
            logger.debug(f'len memories:{len(memories)}')
            sorted_memories = sorted(memories, key=lambda x: x.matched_time, reverse=False)
            logger.debug(f'len sorted_memories:{len(sorted_memories)}')
            # print(f'{memory_type},sorted_memories:{sorted_memories}')
            activated_count = 0
            for width in reversed(range(1, memory.COMPOSE_NUMBER - 1)):
                logger.debug(f'width:{width}')
                sub_sets = children_combinations(sorted_memories, width)
                logger.debug(f'len sub_sets:{len(sub_sets)}')
                # print(f'sub_sets:{sub_sets}')
                for sub_set in sub_sets:
                    # print(f'sub_set:{sub_set}')
                    parents = self.memory_indexes.get(memory.create_children_hash(sub_set, memory_type + 1))
                    # print(f'parents:{parents}')
                    if parents is not None:
                        logger.debug(f'len parents:{len(parents)}')
                        for m in parents:
                            if activated_count > ASSOCIATE_MEMORY_LIMIT:
                                return
                                # print(f'{m.simple_str()}')
                            if m.status is MemoryStatus.DORMANT:
                                continue
                            activated_count += 1
                            if m in self.active_memories:
                                continue
                            if time.time() - m.matched_time > m.get_duration():
                                self.activate_memory(m)
                if activated_count > 0:
                    return

    def activate_memory(self, m: Memory):
        m.activate()
        self.active_memories.add(m)

    @util.timeit
    def activate_children(self):
        self.temp_set1.clear()
        for m in self.active_memories.copy():
            if m.status is MemoryStatus.MATCHING:
                self.activate_children_tree(m)

    # @util.timeit
    def activate_children_tree(self, m: Memory):
        if m.status is MemoryStatus.DORMANT:
            return
        if m in self.temp_set1:
            return
        self.temp_set1.add(m)
        if m not in self.active_memories:
            self.activate_memory(m)
        # self.counter += 1
        for x in m.children:
            if x.memory_type in [MemoryType.REAL, MemoryType.SLICE]:
                if x.status is MemoryStatus.SLEEP:
                    self.activate_children_tree(x)
            else:
                if x.status in [MemoryStatus.MATCHING, MemoryStatus.SLEEP]:
                    self.activate_children_tree(x)
                    # just active 1st non-matched memory
                    return

    @util.timeit
    def match_memories(self):
        # logger.debug(f'match_memories start')
        # self.temp_set1.clear()
        for i in range(0, memory.MEMORY_TYPES_LENGTH):
            for m in {x for x in self.active_memories if
                      x.memory_type == i and x.status in [MemoryStatus.MATCHING, MemoryStatus.MATCHED]}:
                m.match_children()
                # self.counter += 1
                if m.status is MemoryStatus.MATCHED:
                    self.add_matched_memory(m)
                    # match bottom up
                    # for x in m.parent:
                    #     if x.status in [MemoryStatus.DORMANT, MemoryStatus.SLEEP]:
                    #         x.match_children()
                    #         # self.counter += 1
                    #         if x.status is MemoryStatus.MATCHED:
                    #             self.add_matched_memory(m)

    def post_matched_memories(self):
        for m in {x for x in self.active_memories if x.status is MemoryStatus.MATCHED}:
            m.post_matched()

    @util.timeit
    def add_matched_memory(self, m):
        if m.memory_type == memory.MemoryType.REAL:
            work_list = self.work_memories[m.memory_type][m.real_type]
        else:
            work_list = self.work_memories[m.memory_type]
        if m not in work_list:
            work_list.append(m)
            self.active_memories.add(m)

    # @util.timeit
    # extend active time of parent memory which are in active and matching status
    # def extend_matching_parent(self, m: Memory):
    #     for x in m.parent:
    #         self.extend_matching_parent_tree(x)

    # def extend_matching_parent_tree(self, m: Memory):
    #     if m in self.temp_set1:
    #         return
    #     self.temp_set1.add(m)  # record that x have been processed, will skip it in the same frame
    #     if m in self.active_memories and m.status is MemoryStatus.MATCHING:
    #         m.active_end_time = time.time() + memory.MEMORY_DURATIONS[m.memory_type]
    #     # self.counter += 1
    #     for x in m.parent:
    #         self.extend_matching_parent_tree(x)

    @util.timeit
    def put_memory(self, m: Memory):
        # logger.debug(f'put_memory:{m.mid}')
        em = self.memory_indexes.get(m.mid)
        if em:
            m = em
            m.matched(recall=True)
        else:
            self.memories.add(m)
            m.create_index(self.memory_indexes)
            m.matched(recall=False)
        self.add_matched_memory(m)
        return m

    def find_similar_feature_memories(self, query: Memory):
        feature_memories = self.memory_indexes.get(query.kernel_index)
        if feature_memories is None:
            return
        for m in feature_memories:
            difference = util.np_array_diff(query.feature, m.feature)
            if difference < FEATURE_SIMILARITY_THRESHOLD:
                return m

    @util.timeit
    def put_feature_memory(self, real_type, kernel, feature, channel=None):
        q = Memory(MemoryType.REAL, real_type=real_type, kernel=kernel, feature=feature, channel=channel)
        m = self.find_similar_feature_memories(q)
        if m:
            self.put_memory(m)
        else:
            self.put_memory(q)

    @util.timeit
    def compose_memory(self, children, memory_type, real_type=-1, reward=0):
        if len(children) == 0:
            return
        q = Memory(memory_type, real_type=real_type, children=children)
        m = self.put_memory(q)
        # for c in children:
        #     c.parent.add(m)
        if reward > 0:
            m.reward = reward
        else:
            max_reward = np.max(np.array([x.reward for x in children]))
            m.reward = max_reward * 0.9
        return m

    @util.timeit
    def compose_memories(self):
        for i in range(0, memory.MEMORY_FEATURES_LENGTH):
            nm = self.compose_memory(self.get_valid_work_memories(MemoryType.REAL, i), MemoryType.SLICE,
                                     real_type=i)
            if nm:
                self.add_matched_memory(nm)

        for j in range(MemoryType.REAL + 1, memory.MEMORY_TYPES_LENGTH - 1):
            memory_type = j + 1
            # if memory_type >= len(memory.MEMORY_TYPES):
            #     memory_type = j
            nm = self.compose_memory(self.get_valid_work_memories(j, -1), memory_type)
            if nm:
                self.add_matched_memory(nm)

    @util.timeit
    def get_valid_work_memories(self, memory_type, real_type):
        now = time.time()
        if memory_type == memory.MemoryType.REAL:
            memories = list(self.work_memories[memory_type][real_type])
        else:
            memories = list(self.work_memories[memory_type])
        valid_memories = []
        for m in list(memories):
            if (now - m.matched_time) < memory.MEMORY_DURATIONS[memory_type]:
                valid_memories.append(m)
        return valid_memories

    @util.timeit
    def cleanup_active_memories(self):
        # self.log_dashboard()
        new_active_memories = set()
        active_memory_list = list(self.active_memories)
        strength_list = [x.get_strength() for x in active_memory_list if x.memory_type == MemoryType.LONG]
        threshold = 0
        if len(strength_list) > ACTIVE_LONG_MEMORY_LIMIT:
            desc_list = sorted(strength_list, reverse=True)
            threshold = desc_list[ACTIVE_LONG_MEMORY_LIMIT]
        for m in self.active_memories:
            if m.status in [MemoryStatus.LIVING, MemoryStatus.MATCHING] and m.active_end_time > time.time():
                # use strength instead of get_strength() to avoid different strength value
                if m.memory_type == MemoryType.LONG and m.strength <= threshold:
                    m.deactivate()
                else:
                    new_active_memories.add(m)
            else:
                m.deactivate()
        self.active_memories = new_active_memories

    def log_dashboard(self):
        try:
            dashboard.log(self.memories, 'all_memory')
            dashboard.log(self.active_memories, 'active_memory', with_status=True, need_active=False)
            # for i in range(0, 5):
            #     logger.debug(
            #         f'all active memories type {i} [{[x.mid for x in self.active_memories if x.memory_type == i]}]')
        except:
            logging.error(traceback.format_exc())

    # Use a separate thread to cleanup memories regularly.
    @util.timeit
    def cleanup_memories(self):
        # TODO, is there performance issue? Seems multi thread don't help
        for m in self.memories.copy():
            m.refresh_self(recall=False, is_forget=True)

        if len(self.memories) < MEMORIES_CLEANUP_NUM:
            return
        new_memories = sorted(list(self.memories.copy()), key=lambda x: (x.status, x.recall_count, x.matched_time),
                              reverse=True)
        trim_memories = new_memories[0:MEMORIES_NUM]
        self.memories = set(trim_memories)
        # for m in self.memories.copy():
        #     m.parent = {x for x in m.parent if x in new_memories}
        self.reindex()

    # Use a separate thread to persist memories to storage regularly.
    @util.timeit
    def save(self):
        try:
            self.cleanup_memories()
            np.save(MEMORY_FILE, list(memory.flatten(self.memories.copy())))
        except:
            logging.error(traceback.format_exc())

    @util.timeit
    def reindex(self):
        memory_indexes = {}
        for m in self.memories:
            m.create_index(memory_indexes)
        self.memory_indexes = memory_indexes

    @util.timeit
    def load(self):
        try:
            raw_data = np.load(MEMORY_FILE, allow_pickle=True)
            memories = memory.construct(set(raw_data))
            # reset status from unexpected exit
            for m in memories:
                if m.status is not MemoryStatus.DORMANT:
                    m.status = MemoryStatus.SLEEP
            self.memories = memories
            self.reindex()
        except:
            pass

    @util.timeit
    def get_matching_real_memories(self, real_type):
        real_memories = {x for x in self.active_memories if
                         x.memory_type == MemoryType.REAL and
                         x.real_type == real_type and x.status == MemoryStatus.MATCHING}
        return real_memories

    @util.timeit
    def get_matched_slice_memories(self, real_type):
        slice_memories = {x for x in self.active_memories if
                          x.memory_type == MemoryType.SLICE and
                          x.real_type == real_type and x.status == MemoryStatus.MATCHED}
        return slice_memories
