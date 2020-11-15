import logging
import math
import random
import threading
import time
from collections import deque

import vptree

from components import constants
from components import util
from components.memory import Memory
from components.recognizers import ImageRecognizer
from components.recognizers import VoiceRecognizer

logger = logging.getLogger('Brain')
logger.setLevel(logging.DEBUG)


class Brain:
    all_memories = {}  # contains both cache and vp tree
    n_memories = {}  # length of all_memories
    memory_cache = {}  # cache before put to vp tree
    memory_vp_tree = {}  # speed up searching memories
    work_memories = {}

    interval_s = 5 / 1000
    MEMORY_FILE = 'data/memory.npy'
    SELF_FUNC = 's'
    ITEM_FUNC = 'v'
    RECOGNIZERS = {constants.voice: VoiceRecognizer, constants.image: ImageRecognizer}

    memory_cycles = [15, 30, 60, 120, 60 * 5, 60 * 30, 60 * 60 * 12, 60 * 60 * 24, 60 * 60 * 24 * 2, 60 * 60 * 24 * 4,
                     60 * 60 * 24 * 7, 60 * 60 * 24 * 15, 60 * 60 * 24 * 30]

    def __init__(self):
        self.running = True
        for mt in constants.feature_types + constants.memory_types:
            self.all_memories.update({mt: set()})
            self.n_memories.update({mt: 0})
            self.memory_cache.update({mt: set()})
            self.memory_vp_tree.update({mt: None})
            self.work_memories.update({mt: deque(maxlen=constants.n_memory_children)})

    @classmethod
    def get_retrievability(cls, t, stability=0):
        if t <= 1200:
            forget_possibility = 0.00035 * t
        elif t <= 3600:
            forget_possibility = 0.000155555 * t
        elif t <= 86400:
            forget_possibility = 0.000008564 * t
        elif t <= 604800:
            forget_possibility = 0.000001273 * t
        elif t <= 2592000:
            forget_possibility = 0.000000304 * t
        else:
            forget_possibility = 0.8
        r = 1 - forget_possibility * (len(cls.memory_cycles) - stability) / len(cls.memory_cycles)
        return round(r, 2)

    @classmethod
    def is_steady(cls, m):
        now_time = time.time()
        # print(f'now {now_time}, at {m.activated_time}, stb {m.stability}')
        if now_time < m.activated_time + cls.memory_cycles[m.stability]:
            return True
        else:
            return False

    @classmethod
    def activate_memory(cls, m):
        now_time = time.time()
        if m.stability == len(cls.memory_cycles) or cls.is_steady(m):
            pass
        elif now_time - m.CREATED_TIME > cls.memory_cycles[m.stability]:
            m.stability += 1
        m.activated_time = now_time

    @classmethod
    def validate_memory(cls, m):
        now_time = time.time()
        if cls.is_steady(m):
            # print(f'is steady')
            # avoid frequent refresh
            return True
        else:
            retrievability = cls.get_retrievability(now_time - m.CREATED_TIME, m.stability)
            ran = random.randint(1, 100)
            if ran > retrievability * 100:
                return False
            else:
                # print(f'here')
                # avoid frequent cleanup
                m.activated_time = now_time
                return True

    @classmethod
    def slow_loop(cls, mode, items, map_func, args, chunk=10, interval=interval_s):
        time.sleep(cls.interval_s)
        start = time.time()
        chunk_size = chunk
        result = []
        for i in range(0, len(items), chunk_size):
            chunk_items = items[i:i + chunk_size]
            for item in chunk_items:
                if mode == cls.SELF_FUNC:
                    new_item = globals()[map_func](item, args)
                else:
                    new_item = getattr(item, map_func)(item, args)
                result.append(new_item)
            if time.time() - start > cls.interval_s:
                start = time.time()
                time.sleep(cls.interval_s)
        return result

    @staticmethod
    def create_indexes(item, memory_indexes):
        memory_indexes.update({item.MID: item})

    @staticmethod
    def update_index(mid, memory_indexes):
        mem = memory_indexes[mid]
        for context_mid in mem.context.copy():
            # if the context memory still exists
            if context_mid in memory_indexes:
                # add item to context_index of each memory in context
                memory_indexes[context_mid].context_index.add(mem.MID)
            else:
                # the context memory was forgot
                del mem.context[context_mid]
        for data_mid in mem.DATA:
            if data_mid in memory_indexes:
                # add item to data_index of each memory in DATA
                memory_indexes[data_mid].data_index.add(mem.MID)
        # check if the memory was forgot in context index
        for context_index in mem.context_indexes.copy():
            if context_index not in memory_indexes:
                mem.context_indexes.remove(context_index)
        # check if the memory was forgot in data index
        for data_index in mem.data_indexes.copy():
            if data_index not in memory_indexes:
                mem.data_indexes.remove(data_index)

    @staticmethod
    def update_weight(item, memory_indexes):
        item.context_weight = math.log(len(memory_indexes) / len(item.context_indexes))
        item.data_weight = math.log(len(memory_indexes) / len(item.data_indexes))

    def start(self):
        brain_thread = threading.Thread(target=self.persist)
        brain_thread.daemon = True
        brain_thread.start()

    def stop(self):
        self.running = False

    def input_features(self, features):
        self.input_real(features)

    @util.timeit
    def input_real(self, features):
        pack = set()
        for feature in features:
            m = self.find_memory(feature)
            if m is None:
                m = self.add_real_memory(feature)
            else:
                self.activate_memory(m)
            pack.add(m)

    def add_real_memory(self, feature):
        m = Memory(constants.real, feature, feature.type)
        self.all_memories[feature.type].add(m)
        self.memory_cache[feature.type].add(m)
        return m

    def find_cache(self, feature):
        recognizer = self.RECOGNIZERS[feature.type]
        cache = self.memory_cache[feature.type]
        # print(f'len cache {len(cache)}')
        for m in cache:
            if recognizer.is_feature_similar(feature, m.data):
                return m

    def find_tree(self, feature):
        recognizer = self.RECOGNIZERS[feature.type]
        tree = self.memory_vp_tree[feature.type]
        if tree is not None:
            query = Memory(constants.real, feature, feature.type)
            distance, nearest_memory = tree.get_nearest_neighbor(query)
            if recognizer.is_similar(distance):
                return nearest_memory

    @util.timeit
    def find_memory(self, feature):
        nearest = self.find_tree(feature)
        if nearest is None:
            nearest = self.find_cache(feature)
        return nearest

    # Use a separate thread to cleanup memories regularly.
    @util.timeit
    def cleanup_memories(self):
        for ft in constants.feature_types + constants.memory_types:
            memories = self.all_memories[ft].copy()
            new_memories = {x for x in memories if self.validate_memory(x)}
            # TODO, some update may lost during this process
            self.all_memories.update({ft: new_memories})
            time.sleep(self.interval_s)

    @util.timeit
    def reindex(self):
        for ft in constants.feature_types:
            memories = self.all_memories[ft].copy()
            caches = self.memory_cache[ft]
            has_creation = len(caches) > 0
            has_deletion = self.n_memories[ft] != len(memories)
            if has_creation or has_deletion:
                print(f'start to reindex')
                recognizer = self.RECOGNIZERS[ft]
                tree = vptree.VPTree(list(memories), recognizer.compare_memory)
                print(f'vptree points:{len(memories)}')
                # TODO, some update may lost during this process
                self.memory_vp_tree.update({ft: tree})
                caches.clear()
                time.sleep(self.interval_s)
            self.n_memories.update({ft: len(memories)})

    def persist(self):
        while self.running:
            self.cleanup_memories()
            self.reindex()
            time.sleep(self.interval_s)
