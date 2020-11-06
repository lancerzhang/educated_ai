import logging
import math
import time
from collections import deque

from components import constants
from components import util
from components.memory import Memory
from components.recognizers import ImageRecognizer
from components.recognizers import VoiceRecognizer

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
FEATURE_TYPES = [constants.voice, constants.image]
RECOGNIZERS = {constants.voice: VoiceRecognizer, constants.image: ImageRecognizer}


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
    all_memories = {}  # contains both cache and vp tree
    memory_cache = {}  # cache before put to vp tree
    memory_vp_tree = {}  # speed up searching memories
    work_memories = {}

    def __init__(self):
        for ft in FEATURE_TYPES:
            self.all_memories.update({ft: set()})
            self.memory_cache.update({ft: set()})
            self.memory_vp_tree.update({ft: None})
            self.work_memories.update({ft: deque(maxlen=constants.n_memory_children)})
        for mt in constants.memory_types:
            self.all_memories.update({mt: set()})
            self.memory_cache.update({mt: set()})
            self.memory_vp_tree.update({mt: None})
            self.work_memories.update({mt: deque(maxlen=constants.n_memory_children)})

    def input_real(self, features):
        for feature in features:
            existed = self.find_memory(feature)
            if existed is None:
                self.add_real_memory(feature)

    def add_real_memory(self, feature):
        m = Memory(constants.real, feature, feature.type)
        self.all_memories[feature.type].add(m)

    def find_cache(self, feature):
        recognizer = RECOGNIZERS[feature.type]
        cache = self.memory_cache[feature.type]
        for m in cache:
            if recognizer.is_similar(feature, m.data):
                return m

    def find_memory(self, feature):
        recognizer = RECOGNIZERS[feature.type]
        tree = self.memory_vp_tree[feature.type]
        if tree is not None:
            nearest1 = tree.get_nearest_neighbor()
            if recognizer.is_similar(nearest1, feature):
                return nearest1
        nearest2 = self.find_cache(feature)
        return nearest2

    # Use a separate thread to cleanup memories regularly.
    @util.timeit
    def cleanup_memories(self):
        interval_s = INTERVAL_MS / 1000
        all_types = FEATURE_TYPES + constants.memory_types
        for ft in all_types:
            memories = self.all_memories[ft]
            new_memories = slow_loop('c', memories, 'cleanup_refresh', None)
            # TODO, some update may lost during this process
            self.all_memories.update({ft: new_memories})
            time.sleep(interval_s)

    @util.timeit
    def reindex(self, memories_list=None):
        # refresh indexes of all memories
        memories_index = {}
        if memories_list is None:
            memories_list = list(self.all_memories)
        slow_loop(SELF_FUNC, memories_list, 'create_indexes', memories_index)
        self.memory_indexes = memories_index
        # refresh context and data indexes
        slow_loop(SELF_FUNC, memories_list, 'update_index', memories_index)
        slow_loop(SELF_FUNC, memories_list, 'update_weight', memories_index)

    def persist(self):
        return
