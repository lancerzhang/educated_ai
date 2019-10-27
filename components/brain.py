from components.memory import Memory
from components import constants
from components import memory
from components import util
import logging
import numpy as np
import time

logger = logging.getLogger('Brain')
logger.setLevel(logging.DEBUG)

FEATURE_SIMILARITY_THRESHOLD = 0.2


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

    def add_memory(self, m):
        if m.mid == 0:
            m.assign_id()
            self.memories.add(m)
        m.status = constants.MATCHED
        m.matched_time = time.time()
        m.recall()
        self.active_memories.append(m)
        return m

    def put_memory(self, query):
        m = self.find_memory(query)
        if m:
            self.add_memory(m)
        else:
            m = self.add_memory(query)
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
        if reward > 0:
            m.reward = reward
        else:
            max_reward = np.max(np.array([x.reward for x in children]))
            m.reward = max_reward * 0.9
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
    def find_memory(self, query):
        for m in self.memories:
            if m.equal(query):
                return m
        return None

    @util.timeit
    def get_memories(self, query):
        result = []
        for m in self.memories:
            if m.equal(query):
                result.append(m)
        return result

    # Use a separate thread to cleanup memories regularly.
    @util.timeit
    def cleanup_memories(self):
        for m in self.memories:
            m.refresh(recall=False, is_forget=True)
        self.memories = set(x for x in self.memories if x.live)

    # Use a separate thread to persist memories to storage regularly.
    @util.timeit
    def save(self):
        config = [memory.id_sequence]
        np.save('memory', list(self.memories))
        np.save('config', config)

    @util.timeit
    def clean(self):
        self.cleanup_memories()
        self.save()

    @util.timeit
    def load(self):
        try:
            self.memories = set(np.load('memory.npy', allow_pickle=True))
        except:
            pass
        try:
            config = np.load('config.npy')
            memory.id_sequence = config[0]
        except:
            pass

    @util.timeit
    def get_feature_memories(self, feature_type_str, kernel):
        query = Memory()
        query.feature_type = memory.get_feature_type(feature_type_str)
        query.kernel = kernel
        return self.get_memories(query)

    @util.timeit
    def find_similar_feature_memories(self, feature_type_str, kernel, feature):
        feature_memories = self.get_feature_memories(feature_type_str, kernel)
        for m in feature_memories:
            difference = util.np_array_diff(feature, m.feature)
            if difference < FEATURE_SIMILARITY_THRESHOLD:
                return m

    @util.timeit
    def put_feature_memory(self, feature_type_str, kernel, feature):
        m = self.find_similar_feature_memories(feature_type_str, kernel, feature)
        if m:
            m.recall()
        else:
            m = Memory()
            m.feature_type = memory.get_feature_type(feature_type_str)
            m.kernel = kernel
            m.feature = feature
            self.add_memory(m)

    @util.timeit
    def put_virtual_memory(self, memory_type_str, child_memories, reward=0):
        memory_type = memory.MEMORY_TYPES.index(memory_type_str)
        self.compose_memory(child_memories, memory_type, reward)

    @util.timeit
    def enrich_feature_memories(self, feature_type_str, fm):
        feature_type = memory.get_feature_type(feature_type_str)
        matched_memories = [x for x in self.active_memories if
                            x.feature_type == feature_type and x.status == constants.MATCHED]
        if fm not in matched_memories:
            matched_memories.append(fm)
        self.put_virtual_memory(constants.SLICE_MEMORY, matched_memories)

    @util.timeit
    def get_matching_feature_memories(self, feature_type_str):
        feature_type = memory.get_feature_type(feature_type_str)
        feature_memories = [x for x in self.active_memories if
                            x.feature_type == feature_type and x.status == constants.MATCHING]
        return feature_memories

    @util.timeit
    def put_physical_memory(self, query):
        query.memory_type = memory.MEMORY_TYPES.index(constants.FEATURE_MEMORY)
        return self.put_memory(query)

    @util.timeit
    def put_vision_feature_memory(self, feature_type, channel, kernel, feature):
        query = Memory()
        query.feature_type = feature_type
        query.channel = channel
        query.kernel = kernel
        query.feature = feature
        return self.put_physical_memory(query)

    @util.timeit
    def put_mouse_click_memory(self, click_type):
        query = Memory()
        query.feature_type = memory.MEMORY_FEATURES.index(constants.ACTION_MOUSE_CLICK)
        query.click_type = click_type
        return self.put_physical_memory(query)

    @util.timeit
    def put_reward_memory(self, reward):
        query = Memory()
        query.feature_type = memory.MEMORY_FEATURES.index(constants.ACTION_REWARD)
        query.reward = reward
        return self.put_physical_memory(query)

    @util.timeit
    def put_vision_focus_move_memory(self, degrees, speed, duration):
        query = Memory()
        query.feature_type = memory.MEMORY_FEATURES.index(constants.VISION_FOCUS_MOVE)
        query.degrees = degrees
        query.speed = speed
        query.duration = duration
        return self.put_physical_memory(query)

    @util.timeit
    def put_vision_focus_zoom_memory(self, zoom_type, zoom_direction):
        query = Memory()
        query.feature_type = memory.MEMORY_FEATURES.index(constants.VISION_FOCUS_ZOOM)
        query.zoom_type = zoom_type
        query.zoom_direction = zoom_direction
        return self.put_physical_memory(query)
