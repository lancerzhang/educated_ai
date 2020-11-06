import logging
import math
import time
from collections import deque
from multiprocessing import Pool

from components import memory
from components import util
from components.memory import Memory

logger = logging.getLogger('Brain')
logger.setLevel(logging.DEBUG)

FEATURE_SIMILARITY_THRESHOLD = 0.2
ACTIVE_LONG_MEMORY_LIMIT = 100
ASSOCIATE_MEMORY_LIMIT = 10
MEMORIES_NUM = 100 * 100 * 5
MEMORIES_CLEANUP_NUM = 100 * 100 * 6
INTERVAL_MS = 5
MEMORY_FILE = 'data/memory.npy'
SELF_FUNC = 's'
ITEM_FUNC = 'v'


def slow_loop(mode, items, map_func, args, chunk=10, interval=INTERVAL_MS):
    interval_s = interval / 1000
    time.sleep(interval_s)
    start = time.time()
    chunk_size = chunk
    result = []
    for i in range(0, len(items), chunk_size):
        chunk_items = items[i:i + chunk_size]
        for item in chunk_items:
            if mode == SELF_FUNC:
                new_item = globals()[map_func](item, args)
            else:
                new_item = getattr(item, map_func)(item, args)
            result.append(new_item)
        if time.time() - start > interval_s:
            start = time.time()
            time.sleep(interval_s)
    return result


def create_indexes(item, memory_indexes):
    memory_indexes.update({item.MID: item})


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


def update_weight(item, memory_indexes):
    item.context_weight = math.log(len(memory_indexes) / len(item.context_indexes))
    item.data_weight = math.log(len(memory_indexes) / len(item.data_indexes))


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
        # self.pool = Pool()

    @util.timeit
    def associate(self):
        return

    def activate_memory(self, m: Memory):
        return

    @util.timeit
    def match_memories(self):
        return

    def post_matched_memories(self):
        return

    @util.timeit
    def compose_memories(self):
        return

    @util.timeit
    def cleanup_active_memories(self):
        return

    # Use a separate thread to cleanup memories regularly.
    @util.timeit
    def cleanup_memories(self):
        interval_s = INTERVAL_MS / 1000
        memories = list(self.memories)
        time.sleep(interval_s)
        new_memories = slow_loop('c', memories, 'cleanup_refresh', None)
        time.sleep(interval_s)
        if len(self.memories) < MEMORIES_CLEANUP_NUM:
            return new_memories
        sorted_memories = sorted(new_memories, key=lambda x: (x.status, x.recall_count, x.matched_time),
                                 reverse=True)
        time.sleep(interval_s)
        trim_memories = sorted_memories[0:MEMORIES_NUM]
        time.sleep(interval_s)
        self.reindex(fast_mode=False, memories_list=trim_memories)
        time.sleep(interval_s)
        self.memories = set(trim_memories)
        return trim_memories

    @util.timeit
    def reindex(self, memories_list=None):
        # refresh indexes of all memories
        memories_index = {}
        if memories_list is None:
            memories_list = list(self.memories)
        slow_loop(SELF_FUNC, memories_list, 'create_indexes', memories_index)
        self.memory_indexes = memories_index
        # refresh context and data indexes
        slow_loop(SELF_FUNC, memories_list, 'update_index', memories_index)
        slow_loop(SELF_FUNC, memories_list, 'update_weight', memories_index)

    def persist(self):
        return
