import logging
import math
import random
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

FEATURE_SIMILARITY_THRESHOLD = 0.2
ACTIVE_LONG_MEMORY_LIMIT = 100
ASSOCIATE_MEMORY_LIMIT = 10
MEMORIES_NUM = 100 * 100 * 5
MEMORIES_CLEANUP_NUM = 100 * 100 * 6
INTERVAL_MS = 5
MEMORY_FILE = 'data/memory.npy'
SELF_FUNC = 's'
ITEM_FUNC = 'v'
RECOGNIZERS = {constants.voice: VoiceRecognizer, constants.image: ImageRecognizer}
TIME_SEC = [5, 6, 8, 11, 15, 20, 26, 33, 41, 50, 60, 71, 83, 96, 110, 125, 141, 158, 176, 196, 218, 242, 268, 296,
            326, 358, 392, 428, 466, 506, 548, 593, 641, 692, 746, 803, 863, 926, 992, 1061, 1133, 1208, 1286, 1367,
            1451, 1538, 1628, 1721, 1920, 2100, 2280, 2460, 2640, 2880, 3120, 3360, 3600, 4680, 6120, 7920, 10440,
            14040, 18720, 24840, 32400, 41760, 52920, 66240, 81720, 99720, 120240, 143640, 169920, 222480, 327600,
            537840, 853200, 1326240, 2035800, 3100140, 3609835, 4203316, 4894372, 5699043, 6636009, 7727020,
            8997403, 10476649, 12199095, 14204727, 16540102, 19259434, 22425848, 26112847, 30406022, 35405033,
            41225925, 48003823, 55896067, 65085866]


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


def recall_memory(memory):
    # TODO
    return


def refresh_memory(memory, recall=False, is_forget=False):
    now_time = time.time()
    time_elapse = now_time - memory.last_recall_time
    if time_elapse < TIME_SEC[0]:
        return
    count = 0
    for num in range(memory.recall_count, len(TIME_SEC)):
        if TIME_SEC[num] <= time_elapse:
            count = count + 1
        else:
            # if go to next section
            if count > 0:
                # random forget memory base on strength
                if is_forget and time.time() > memory.protect_time:
                    memory.protect_time = memory.calculate_protect_time(memory.recall_count)
                    ran = random.randint(1, 100)
                    strength = 100 - count
                    if ran > strength:
                        memory.hibernate()
                        break
                # if this is recall, will update recall count and last recall time
                if recall:
                    memory.recall_count += 1
                    memory.last_recall_time = time.time()
            break


class Brain:
    all_memories = {}  # contains both cache and vp tree
    memory_cache = {}  # cache before put to vp tree
    memory_vp_tree = {}  # speed up searching memories
    work_memories = {}

    def __init__(self):
        for mt in constants.feature_types + constants.memory_types:
            self.all_memories.update({mt: set()})
            self.memory_cache.update({mt: set()})
            self.memory_vp_tree.update({mt: None})
            self.work_memories.update({mt: deque(maxlen=constants.n_memory_children)})

    def input_real(self, features):
        for feature in features:
            existed = self.find_memory(feature)
            if existed is None:
                self.add_real_memory(feature)
            else:
                recall_memory(existed)

    def add_real_memory(self, feature):
        m = Memory(constants.real, feature, feature.type)
        self.all_memories[feature.type].add(m)
        self.memory_cache[feature.type].add(m)

    def find_cache(self, feature):
        recognizer = RECOGNIZERS[feature.type]
        cache = self.memory_cache[feature.type]
        # print(f'len cache {len(cache)}')
        for m in cache:
            if recognizer.is_feature_similar(feature, m.data):
                return m

    def find_tree(self, feature):
        recognizer = RECOGNIZERS[feature.type]
        tree = self.memory_vp_tree[feature.type]
        if tree is not None:
            query = Memory(constants.real, feature, feature.type)
            distance, nearest_memory = tree.get_nearest_neighbor(query)
            if recognizer.is_similar(distance):
                return nearest_memory

    def find_memory(self, feature):
        nearest = self.find_tree(feature)
        if nearest is None:
            nearest = self.find_cache(feature)
        return nearest

    # Use a separate thread to cleanup memories regularly.
    @util.timeit
    def cleanup_memories(self):
        interval_s = INTERVAL_MS / 1000
        for ft in constants.feature_types + constants.memory_types:
            memories = self.all_memories[ft].copy()
            new_memories = {x for x in memories if refresh_memory(x)}
            # TODO, some update may lost during this process
            self.all_memories.update({ft: new_memories})
            time.sleep(interval_s)

    @util.timeit
    def reindex(self):
        interval_s = INTERVAL_MS / 1000
        for ft in constants.feature_types:
            recognizer = RECOGNIZERS[ft]
            memories = self.all_memories[ft].copy()
            tree = vptree.VPTree(list(memories), recognizer.compare_memory)
            # TODO, some update may lost during this process
            self.memory_vp_tree.update({ft: tree})
            self.memory_cache[ft].clear()
            time.sleep(interval_s)

    def persist(self):
        return
