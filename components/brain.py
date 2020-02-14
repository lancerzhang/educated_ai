from components.memory import Memory
from components.memory import MemoryType
from components.memory import FeatureType
from components import constants
from components import dashboard
from components import memory
from components import util
from collections import deque
import logging
import numpy as np
import traceback
import time

logger = logging.getLogger('Brain')
logger.setLevel(logging.INFO)


class Brain:
    MEMORY_FILE = 'data/memory.npy'
    FEATURE_SIMILARITY_THRESHOLD = 0.2
    ACTIVE_LONG_MEMORY_LIMIT = 100

    def __init__(self):
        self.memories = set()
        self.memory_indexes = {}  # speed up searching memories
        self.work_memories = []
        self.active_memories = set()
        self.temp_set = set()  # speed up searching active memories
        work_feature_memories = []
        for i in range(0, memory.MEMORY_FEATURES_LENGTH):
            work_feature_memories.append(deque(maxlen=memory.COMPOSE_NUMBER))
        self.work_memories.append(work_feature_memories)
        for i in range(1, memory.MEMORY_TYPES_LENGTH):
            self.work_memories.append(deque(maxlen=memory.COMPOSE_NUMBER))

    @util.timeit
    # find top parents
    def associate(self):
        self.temp_set.clear()
        for m in self.active_memories:
            if m.status is constants.LIVING:
                self.search_top_parent(m)
        top_parents = self.temp_set.copy()
        self.temp_set.clear()
        for m in top_parents:
            # TODO, need to check desire?
            self.activate_memory(m)

    # @util.timeit
    def search_top_parent(self, m: Memory):
        for p in m.parent:
            if len(p.parent) == 0:
                self.temp_set.add(p)
            else:
                self.search_top_parent(p)

    @util.timeit
    def activate_memory(self, m: Memory):
        if m in self.temp_set:
            return
        self.temp_set.add(m)  # record that m have been processed, will skip it in the same frame
        m.activate()
        self.active_memories.add(m)

    @util.timeit
    def activate_children(self):
        self.temp_set.clear()
        for m in self.active_memories.copy():
            if m.status is constants.MATCHING:
                self.activate_children_tree(m)

    # @util.timeit
    def activate_children_tree(self, m: Memory):
        if m in self.temp_set:
            return
        self.activate_memory(m)
        # logger.debug(f'activate_children_tree {m.simple_str()}')
        for x in m.children:
            if x.memory_type in [MemoryType.FEATURE, MemoryType.SLICE]:
                self.activate_children_tree(x)
            else:
                if x.status is constants.MATCHING:
                    self.activate_children_tree(x)
                    # just active 1st non-matched memory
                    return

    @util.timeit
    def match_memories(self):
        self.temp_set.clear()
        for i in range(0, memory.MEMORY_TYPES_LENGTH):
            for m in {x for x in self.active_memories if x.memory_type == i}:
                m.match_children()
                if m.status is constants.MATCHED:
                    self.post_matched_memory(m)
                    for x in m.parent:
                        x.match_children()
                        if x.status is constants.MATCHED:
                            self.post_matched_memory(x)
        self.temp_set.clear()
        for m in [x for x in self.active_memories if x.status is constants.MATCHING]:
            self.extend_matched_children(m)

    def post_matched_memory(self, m: Memory):
        m.post_matched()
        self.add_matched_memory(m)
        self.extend_matching_parent(m)

    @util.timeit
    def add_matched_memory(self, m):
        if m.memory_type == memory.MemoryType.FEATURE:
            work_list = self.work_memories[m.memory_type][m.feature_type]
        else:
            work_list = self.work_memories[m.memory_type]
        if m not in work_list:
            work_list.append(m)
            self.active_memories.add(m)

    # @util.timeit
    # extend active time of parent memory which are in active and matching status
    def extend_matching_parent(self, m: Memory):
        if m in self.temp_set:
            return
        for x in m.parent:
            if x in self.active_memories and x.status is constants.MATCHING:
                x.active_end_time = time.time() + memory.MEMORY_DURATIONS[x.memory_type]
            self.temp_set.add(x)  # record that x have been processed, will skip it in the same frame
            self.extend_matching_parent(x)

    def extend_matched_children(self, m: Memory):
        if m in self.temp_set:
            return
        for x in m.children:
            if x.status is constants.LIVING:
                x.active_end_time = m.active_end_time

    @util.timeit
    def put_memory(self, m: Memory):
        if not self.find_memory(m):
            self.add_memory(m)

    @util.timeit
    def add_memory(self, m: Memory):
        self.memories.add(m)
        m.create_index(self.memory_indexes)
        m.matched()
        self.add_matched_memory(m)

    @util.timeit
    def put_feature_memory(self, feature_type, kernel, feature, channel=None):
        m = Memory(MemoryType.FEATURE, feature_type=feature_type, kernel=kernel, feature=feature, channel=channel)
        if not self.find_similar_feature_memories(m):
            self.add_memory(m)

    @util.timeit
    def put_slice_memory(self, child_memories, feature_type, reward=0):
        self.compose_memory(child_memories, MemoryType.SLICE, feature_type=feature_type, reward=reward)

    @util.timeit
    def compose_memory(self, children, memory_type, feature_type=-1, reward=0):
        if len(children) == 0:
            return
        m = Memory(memory_type, feature_type=feature_type, channel=children)
        self.put_memory(m)
        for c in children:
            c.parent.add(m)
        if reward > 0:
            m.reward = reward
        else:
            max_reward = np.max(np.array([x.reward for x in children]))
            m.reward = max_reward * 0.9
        return m

    @util.timeit
    def get_valid_work_memories(self, memory_type, feature_type):
        now = time.time()
        if memory_type == memory.MemoryType.FEATURE:
            memories = list(self.work_memories[memory_type][feature_type])
        else:
            memories = list(self.work_memories[memory_type])
        valid_memories = []
        for m in list(memories):
            if (now - m.matched_time) < memory.MEMORY_DURATIONS[memory_type]:
                valid_memories.append(m)
        return valid_memories

    @util.timeit
    def compose_memories(self):
        for i in range(0, memory.MEMORY_FEATURES_LENGTH):
            nm = self.compose_memory(self.get_valid_work_memories(MemoryType.FEATURE, i), MemoryType.SLICE,
                                     feature_type=i)
            if nm:
                self.work_memories[MemoryType.FEATURE + 1].append(nm)

        for j in range(MemoryType.FEATURE + 1, memory.MEMORY_TYPES_LENGTH - 1):
            memory_type = j + 1
            # if memory_type >= len(memory.MEMORY_TYPES):
            #     memory_type = j
            nm = self.compose_memory(self.get_valid_work_memories(j, -1), memory_type)
            if nm:
                self.work_memories[memory_type].append(nm)

    @util.timeit
    def cleanup_active_memories(self):
        # self.log_dashboard()
        new_active_memories = set()
        active_memory_list = list(self.active_memories)
        strength_list = [x.get_strength() for x in active_memory_list if x.memory_type == MemoryType.LONG]
        threshold = 0
        if len(strength_list) > self.ACTIVE_LONG_MEMORY_LIMIT:
            desc_list = sorted(strength_list, reverse=True)
            threshold = desc_list[self.ACTIVE_LONG_MEMORY_LIMIT]
        for m in self.active_memories:
            if m.status in [constants.LIVING, constants.MATCHING] and m.active_end_time > time.time():
                # use strength instead of get_strength() to avoid different strength value
                if m.memory_type == MemoryType.LONG and m.strength <= threshold:
                    m.deactivate()
                else:
                    new_active_memories.add(m)
            else:
                m.deactivate()
        self.active_memories = new_active_memories

    @util.timeit
    def find_memory(self, query: Memory):
        return self.memory_indexes.get(query.mid)

    @util.timeit
    def get_memories(self, query: Memory):
        records = self.memory_indexes.get(query.kernel_index)
        if records:
            return records
        else:
            return []

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
        new_memories = set()
        for m in self.memories.copy():
            m.refresh_self(recall=False, is_forget=True)
            # m.refresh_relative()
            if m.live:
                new_memories.add(m)
        self.memories = new_memories
        self.reindex()

    # Use a separate thread to persist memories to storage regularly.
    @util.timeit
    def save(self):
        try:
            self.cleanup_memories()
            np.save(self.MEMORY_FILE, list(memory.flatten(self.memories)))
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
            raw_data = np.load(self.MEMORY_FILE, allow_pickle=True)
            self.memories = memory.construct(set(raw_data))
            self.reindex()
        except:
            pass

    @util.timeit
    def find_similar_feature_memories(self, query: Memory, feature):
        feature_memories = self.get_memories(query)
        for m in feature_memories:
            difference = util.np_array_diff(feature, m.feature)
            if difference < self.FEATURE_SIMILARITY_THRESHOLD:
                return m

    @util.timeit
    def get_matching_feature_memories(self, feature_type):
        feature_memories = {x for x in self.active_memories if
                            x.memory_type == constants.FEATURE_MEMORY and
                            x.feature_type == feature_type and x.status == constants.MATCHING}
        return feature_memories
