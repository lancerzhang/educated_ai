from components.memory import Memory
from components import constants
from components import memory
from components import util
import collections
import logging
import numpy as np
import traceback
import time

logger = logging.getLogger('Brain')
logger.setLevel(logging.DEBUG)

FEATURE_SIMILARITY_THRESHOLD = 0.2
NUMBER_OF_ACTIVE_MEMORIES = 50
USE_INDEX = True


class Brain:
    memory_file = 'data/memory.npy'

    def __init__(self):
        self.memories = set()
        self.memory_indexes = {}
        self.active_memories = []

    @util.timeit
    def associate(self):
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
    def activate(self):
        for m in self.active_memories:
            m.activate_tree()

    @util.timeit
    def match(self):
        for i in range(1, len(memory.MEMORY_TYPES) - 1):
            for m in self.active_memories:
                if m.memory_type == i:
                    m.match()

        match_any = True
        while match_any:
            match_any = False
            for m in self.active_memories:
                if m.memory_type == memory.get_memory_type(constants.LONG_MEMORY):
                    if m.match():
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
    def compose_memory(self, children, memory_type, feature_type=-1, reward=0):
        if len(children) == 0:
            return
        memories = util.list_remove_duplicates(children)
        if len(memories) > memory.COMPOSE_NUMBER:
            # only use last 4 memories
            memories = memories[-memory.COMPOSE_NUMBER:]
        query = Memory()
        query.memory_type = memory_type
        query.feature_type = feature_type
        query.children = memories
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
    def cleanup(self):
        logger.debug(f'active_memories original size is:{len(self.active_memories)} ')
        new_active_memories = []
        for m in self.active_memories:
            if m.live:
                if m.active_end_time < time.time():
                    m.deactivate()
                else:
                    new_active_memories.append(m)
        self.active_memories = new_active_memories[-NUMBER_OF_ACTIVE_MEMORIES:]
        logger.debug(f'active_memories new size is:{len(self.active_memories)} ')

    @util.timeit
    def find_memory(self, query: Memory):
        if USE_INDEX:
            return self.memory_indexes.get(query.get_index())

        for m in self.memories:
            if m.equal(query):
                return m
        return None

    @util.timeit
    def get_memories(self, query: Memory):
        if USE_INDEX:
            records = self.memory_indexes.get(query.get_index())
            if records:
                return records
            else:
                return []

        result = []
        for m in self.memories:
            if m.equal(query):
                result.append(m)
        return result

    # Use a separate thread to cleanup memories regularly.
    @util.timeit
    def cleanup_memories(self):
        logger.debug(f'memories original size is:{len(self.memories)}')
        new_memories = set()
        new_memory_indexes = {}
        for m in list(self.memories):
            m.refresh(recall=False, is_forget=True)
            if m.live:
                new_memories.add(m)
                m.create_index(new_memory_indexes)
        self.memories = new_memories
        self.memory_indexes = new_memory_indexes
        logger.debug(f'memories new size is:{len(self.memories)}')

    def stat(self):
        memories = [x for x in self.memories if x.recall_count > 1]
        memory_types = [x.memory_type for x in memories]
        memory_types_counter = collections.Counter(memory_types)
        logger.debug(f'memory_types_counter:{sorted(memory_types_counter.items())}')

        feature_type = [x.feature_type for x in memories]
        feature_type_counter = collections.Counter(feature_type)
        logger.debug(f'feature_type_counter:{sorted(feature_type_counter.items())}')

        recall_count = [x.recall_count for x in memories]
        recall_count_counter = collections.Counter(recall_count)
        logger.debug(f'recall_count_counter:{sorted(recall_count_counter.items())}')

        children = [len(x.children) for x in memories if x.memory_type > 0]
        children_counter = collections.Counter(children)
        logger.debug(f'children_counter:{sorted(children_counter.items())}')

    # Use a separate thread to persist memories to storage regularly.
    @util.timeit
    def save(self):
        try:
            self.cleanup_memories()
            config = [memory.id_sequence]
            np.save(self.memory_file, list(memory.flatten(self.memories)))
            np.save('data/config', config)
            self.stat()
        except:
            logging.error(traceback.format_exc())

    @util.timeit
    def load(self):
        try:
            self.memories = memory.construct(set(np.load(self.memory_file, allow_pickle=True)))
            for m in self.memories:
                m.create_index(self.memory_indexes)
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
            if difference < FEATURE_SIMILARITY_THRESHOLD:
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
