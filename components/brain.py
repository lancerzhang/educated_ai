from components.memory import Memory
from components import constants
from components import memory
from components import util
import logging
import numpy as np
import time

logger = logging.getLogger('Brain')
logger.setLevel(logging.DEBUG)


class Brain:
    def __init__(self):
        self.memories = set()
        self.active_memories = []

    @util.timeit
    def associate_active_memories(self):
        active_parent = []
        # collect parent memories
        for m in self.active_memories:
            active_parent += [x for x in m.parent if x.live]
        # count parent memories
        parent_counts = util.list_element_count(active_parent)
        parent_weight = {}
        # update memory desire
        for m, count in parent_counts.items():
            parent_weight.update({m: count * m.get_desire()})
        # select top desire
        for m in sorted(parent_weight, key=parent_weight.get, reverse=True):
            if m not in self.active_memories:
                m.activate()
                self.active_memories.append(m)
                break

    @util.timeit
    def activate_memories(self):
        for m in self.active_memories:
            m.activate_tree()

    @util.timeit
    def match_virtual_memories(self):
        for i in range(1, len(memory.MEMORY_TYPES) - 1):
            for m in self.active_memories:
                if m.memory_type == i:
                    m.match()

        match_any = True
        while match_any:
            match_any = False
            for m in self.active_memories:
                if m.memory_type == memory.MEMORY_TYPES.index(constants.LONG_MEMORY):
                    if m.match():
                        match_any = True

    @util.timeit
    def compose_memory(self, children, memory_type, feature_type=-1, reward=0):
        if len(children) == 0:
            return
        memories = util.list_remove_duplicates(children)
        if len(memories) > memory.COMPOSE_NUMBER:
            # only use last 4 memories
            memories = memories[-memory.COMPOSE_NUMBER:]
        query = Memory()
        query.memory_type = memory_type
        query.children = memories
        m = self.find_one_memory(query)
        if not m:
            m = query
            m.assign_id()
            m.feature_type = feature_type
            max_reward = np.max(np.array([x.reward for x in children]))
            m.reward = max_reward * 0.9
            self.memories.add(m)
        m.status = constants.MATCHED
        m.matched_time = time.time()
        # set reward directly if it's provided
        if reward > 0:
            m.reward = reward
        m.refresh()
        self.active_memories.append(m)
        return m

    @util.timeit
    def compose_active_memories(self):
        matched_memories = [x for x in self.active_memories if x.status == constants.MATCHED]
        now = time.time()

        feature_memory_type_index = memory.MEMORY_TYPES.index(constants.FEATURE_MEMORY)
        for i in range(0, len(memory.MEMORY_FEATURES)):
            memories = [x for x in matched_memories if x.memory_type == feature_memory_type_index
                        and x.feature_type == i
                        and (now - x.matched_time) < memory.MEMORY_DURATIONS[feature_memory_type_index]]
            nm = self.compose_memory(memories, memory.MEMORY_TYPES.index(constants.SLICE_MEMORY), i)
            if nm:
                matched_memories.append(nm)

        for j in range(feature_memory_type_index + 1, len(memory.MEMORY_TYPES)):
            memories = [x for x in matched_memories if
                        x.memory_type == j and (now - x.matched_time) < memory.MEMORY_DURATIONS[j]]
            nm = self.compose_memory(memories, j + 1)
            if nm:
                matched_memories.append(nm)

    @util.timeit
    def cleanup_active_memories(self):
        self.active_memories = [x for x in self.active_memories if x.live]
        new_active_memories = []
        for m in self.active_memories:
            if m.active_end_time < time.time():
                m.deactivate()
            else:
                new_active_memories.append(m)
        self.active_memories = new_active_memories

    @util.timeit
    def find_one_memory(self, query):
        for m in self.memories:
            if m.equal(query):
                return m
        return None

    # Use a separate thread to cleanup memories regularly.
    @util.timeit
    def cleanup_memories(self):
        for m in self.memories:
            m.refresh(recall=False, is_forget=True)
        self.memories = set(x for x in self.memories if x.live)

    # Use a separate thread to persist memories to storage regularly.
    @util.timeit
    def persist_memories(self):
        config = [memory.id_sequence]
        np.save('mm', list(self.memories))
        np.save('config', config)

    @util.timeit
    def house_keep(self):
        self.cleanup_memories()
        self.persist_memories()

    @util.timeit
    def load_memories(self):
        try:
            self.memories = set(np.load('mm.npy', allow_pickle=True))
        except:
            pass
        try:
            config = np.load('config.npy')
            memory.id_sequence = config[0]
        except:
            pass

    @util.timeit
    def add_reward_memory(self, reward):
        m = memory.create()
        m.memory_type = memory.MEMORY_TYPES.index(constants.FEATURE_MEMORY)
        m.feature_type = memory.MEMORY_TYPES.index(constants.ACTION_REWARD)
        m.reward = reward

    @util.timeit
    def add_virtual_memory(self, memory_type_str, child_memories, reward=0):
        memory_type = memory.MEMORY_TYPES.index(memory_type_str)
        self.compose_memory(child_memories, memory_type, reward)

    @util.timeit
    def enrich_feature_memories(self, feature_type_str, fm):
        feature_type = memory.MEMORY_FEATURES.index(feature_type_str)
        matched_memories = [x for x in self.active_memories if
                            x.feature_type == feature_type and x.status == constants.MATCHED]
        if fm not in matched_memories:
            matched_memories.append(fm)
        self.add_virtual_memory(constants.SLICE_MEMORY, matched_memories)

    @util.timeit
    def prepare_matching_physical_memories(self, feature_type_str):
        feature_type = memory.MEMORY_FEATURES.index(feature_type_str)
        physical_memories = [x for x in self.active_memories if
                             x.feature_type == feature_type and x.status == constants.MATCHING]
        return physical_memories

    @util.timeit
    def recall_feature_memory(self, fmm, feature):
        fmm.feature=feature
        fmm.recall()
