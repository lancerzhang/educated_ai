from components.memory import Memory
from components import constants
from components import memory
from components import util
import copy
import logging
import numpy as np
import time

logger = logging.getLogger('Brain')
logger.setLevel(logging.INFO)


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
        for i in range(1, len(memory.MEMORY_TYPES)-1):
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
    def compose_memory(self, children, memory_type, feature_type=-1):
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
            m.create()
            m.feature_type = feature_type
            max_reward = np.max(np.array([x.reward for x in children]))
            m.reward = max_reward * 0.9
            self.memories.add(m)
        m.status = constants.MATCHED
        m.matched_time = time.time()
        m.refresh()
        self.active_memories.append(m)

    @util.timeit
    def compose_active_memories(self):
        matched_memories = [x for x in self.active_memories if x.status == constants.MATCHED]
        now = time.time()

        feature_memory_type_index = memory.MEMORY_TYPES.index(constants.FEATURE_MEMORY)
        for i in range(0, len(memory.MEMORY_FEATURES)):
            memories = [x for x in matched_memories if x.memory_type == feature_memory_type_index
                        and x.feature_type == i
                        and (now - x.matched_time) < memory.MEMORY_DURATIONS[feature_memory_type_index]]
            self.compose_memory(memories, feature_memory_type_index, i)

        for j in range(feature_memory_type_index + 1, len(memory.MEMORY_TYPES)):
            memories = [x for x in matched_memories if
                        x.memory_type == j and (now - x.matched_time) < memory.MEMORY_DURATIONS[j]]
            self.compose_memory(memories, j)

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
            if m.equals(query):
                return m
        return None

    @util.timeit
    def create_memory(self, m):
        return

    # Use a separate thread to cleanup memories regularly.
    @util.timeit
    def cleanup_memories(self):
        for m in self.memories:
            m.refresh()
        self.memories = set(x for x in self.memories if x.live)

    # Use a separate thread to persist memories to storage regularly.
    @util.timeit
    def persist_memories(self):
        pass
