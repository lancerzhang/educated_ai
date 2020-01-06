from components.memory import Memory
from components import constants
from components import dashboard
from components import memory
from components import util
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
        self.memory_indexes = {}
        self.active_memories = []

    @util.timeit
    def get_active_parents(self):
        active_parent = []
        # collect parent memories from top to down
        for x in reversed(range(len(memory.MEMORY_TYPES))):
            if len(active_parent) > 0:
                return active_parent
            for m in self.active_memories:
                if m.memory_type == x and m.status == constants.MATCHED:
                    active_parent += [x for x in m.parent if x.live]
        return active_parent

    @util.timeit
    def associate(self):
        active_parent = self.get_active_parents()
        # count parent memories
        parent_counts = util.list_element_count(active_parent)
        parent_weight = {}
        # update memory desire
        for m, count in parent_counts.items():
            parent_weight.update({m: count * m.get_desire()})
        # select top desire
        active_memory_set = set(self.active_memories)
        for m in sorted(parent_weight, key=parent_weight.get, reverse=True):
            if m not in active_memory_set:
                m.activate()
                self.active_memories.append(m)
                return

    @util.timeit
    def activate_children(self):
        for m in self.active_memories:
            m.activate_children_tree()

    @util.timeit
    def activate_parent(self, m: Memory):
        for x in m.parent:
            if x in self.active_memories:
                x.active_end_time = time.time() + memory.MEMORY_DURATIONS[x.memory_type]
                self.activate_parent(x)

    @util.timeit
    def match_memories(self):
        for i in range(1, len(memory.MEMORY_TYPES) - 1):
            for m in self.active_memories:
                if m.memory_type == i:
                    if m.match():
                        self.activate_parent(m)

        match_any = True
        while match_any:
            match_any = False
            for m in self.active_memories:
                if m.memory_type == memory.get_memory_type(constants.LONG_MEMORY):
                    if m.match():
                        self.activate_parent(m)
                        match_any = True

    @util.timeit
    def add_memory(self, m: Memory):
        if m.mid == 0:
            m.assign_id()
            self.memories.add(m)
            m.create_index(self.memory_indexes)
        m.matched()
        self.active_memories.append(m)

    @util.timeit
    def put_memory(self, query: Memory):
        m = self.find_memory(query)
        if not m:
            m = query
        self.add_memory(m)
        return m

    @util.timeit
    def compose_memory(self, matched_active_memories, memory_type, feature_type=-1, reward=0):
        if len(matched_active_memories) == 0:
            return
        children = util.list_remove_duplicates(matched_active_memories)
        if len(children) > memory.COMPOSE_NUMBER:
            # only use last 4 memories
            children = children[-memory.COMPOSE_NUMBER:]
        query = Memory()
        query.memory_type = memory_type
        query.feature_type = feature_type
        query.children = children
        m = self.put_memory(query)
        for c in children:
            c.parent.add(m)
        if reward > 0:
            m.reward = reward
        else:
            max_reward = np.max(np.array([x.reward for x in children]))
            m.reward = max_reward * 0.9
        return m

    @util.timeit
    def compose_memories(self):
        matched_memories = [x for x in self.active_memories if x.status == constants.MATCHED]
        now = time.time()

        feature_memory_type_index = memory.get_memory_type(constants.FEATURE_MEMORY)
        for i in range(0, len(memory.MEMORY_FEATURES)):
            memories = [x for x in matched_memories if x.memory_type == feature_memory_type_index
                        and x.feature_type == i
                        and (now - x.matched_time) < memory.MEMORY_DURATIONS[feature_memory_type_index]]
            nm = self.compose_memory(memories, memory.get_memory_type(constants.SLICE_MEMORY), feature_type=i)
            if nm:
                matched_memories.append(nm)

        for j in range(feature_memory_type_index + 1, len(memory.MEMORY_TYPES)):
            memories = [x for x in matched_memories if
                        x.memory_type == j and (now - x.matched_time) < memory.MEMORY_DURATIONS[j]]
            memory_type = j + 1
            if memory_type >= len(memory.MEMORY_TYPES):
                memory_type = j
            nm = self.compose_memory(memories, memory_type)
            if nm:
                matched_memories.append(nm)

    @util.timeit
    def cleanup_active_memories(self):
        new_active_memories = []
        strength_list = [x.get_strength() for x in self.active_memories if
                         x.memory_type == memory.MEMORY_TYPES.index(constants.LONG_MEMORY)]
        threshold = 0
        if len(strength_list) > self.ACTIVE_LONG_MEMORY_LIMIT:
            desc_list = sorted(strength_list, reverse=True)
            threshold = desc_list[self.ACTIVE_LONG_MEMORY_LIMIT]
        for m in self.active_memories:
            if m.status in [constants.MATCHED, constants.MATCHING] and m.active_end_time > time.time():
                # use strength instead of get_strength() to avoid different strength value
                if m.memory_type == memory.MEMORY_TYPES.index(constants.LONG_MEMORY) and m.strength <= threshold:
                    m.deactivate()
                else:
                    new_active_memories.append(m)
            else:
                m.deactivate()
        self.active_memories = new_active_memories

    @util.timeit
    def find_memory(self, query: Memory):
        return self.memory_indexes.get(query.get_index())

    @util.timeit
    def get_memories(self, query: Memory):
        records = self.memory_indexes.get(query.get_index())
        if records:
            return records
        else:
            return []

    def log_dashboard(self):
        dashboard.log(self.memories, 'all_memory')
        dashboard.log(self.active_memories, 'active_memory')

    # Use a separate thread to cleanup memories regularly.
    @util.timeit
    def cleanup_memories(self):
        logger.debug(f'memories original size is:{len(self.memories)}')
        new_memories = set()
        for m in list(self.memories):
            m.refresh_self(recall=False, is_forget=True)
            m.refresh_relative()
            if m.live:
                new_memories.add(m)
        self.memories = new_memories
        self.reindex()
        logger.debug(f'memories new size is:{len(self.memories)}')

    # Use a separate thread to persist memories to storage regularly.
    @util.timeit
    def save(self):
        try:
            self.cleanup_memories()
            config = [memory.id_sequence]
            np.save(self.MEMORY_FILE, list(memory.flatten(self.memories)))
            np.save('data/config', config)
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
        try:
            config = np.load('data/config.npy')
            memory.id_sequence = config[0]
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
    def put_feature_memory(self, feature_type_str, kernel, feature, channel=None):
        query = Memory()
        query.set_memory_type(constants.FEATURE_MEMORY)
        query.set_feature_type(feature_type_str)
        if channel:
            query.channel = channel
        query.kernel = kernel
        m = self.find_similar_feature_memories(query, feature)
        if not m:
            m = query
            m.feature = feature
        self.add_memory(m)

    @util.timeit
    def put_physical_memory(self, query: Memory):
        query.set_memory_type(constants.FEATURE_MEMORY)
        return self.put_memory(query)

    @util.timeit
    def put_virtual_memory(self, child_memories, memory_type_str, reward=0):
        self.compose_memory(child_memories, memory.get_memory_type(memory_type_str), reward=reward)

    @util.timeit
    def enrich_feature_memories(self, feature_type_str, fm: Memory):
        feature_type = memory.get_feature_type(feature_type_str)
        matched_memories = [x for x in self.active_memories if
                            x.feature_type == feature_type and x.status == constants.MATCHED]
        if fm not in matched_memories:
            matched_memories.append(fm)
        self.put_virtual_memory(matched_memories, constants.SLICE_MEMORY)

    @util.timeit
    def get_matching_feature_memories(self, feature_type_str):
        feature_type = memory.get_feature_type(feature_type_str)
        feature_memories = [x for x in self.active_memories if
                            x.memory_type == constants.FEATURE_MEMORY and
                            x.feature_type == feature_type and x.status == constants.MATCHING]
        return feature_memories
