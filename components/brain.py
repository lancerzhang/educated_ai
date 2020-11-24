import logging
import math
import random
import threading
import time
import traceback

import vptree

from components import constants
from components import util
from components.memory import Memory
from components.recognizers import ImageRecognizer
from components.recognizers import VoiceRecognizer

logger = logging.getLogger('Brain')
logger.setLevel(logging.DEBUG)


class Brain:
    interval_s = 5 / 1000
    MEMORY_FILE = 'data/memory.npy'
    SELF_FUNC = 's'
    ITEM_FUNC = 'v'
    RECOGNIZERS = {constants.voice: VoiceRecognizer, constants.image: ImageRecognizer}

    memory_cycles = [15, 30, 60, 120, 60 * 5, 60 * 30, 60 * 60 * 12, 60 * 60 * 24, 60 * 60 * 24 * 2, 60 * 60 * 24 * 4,
                     60 * 60 * 24 * 7, 60 * 60 * 24 * 15, 60 * 60 * 24 * 30]

    def __init__(self):
        self.running = True
        self.instant_set = set()
        self.instant_list = []
        self.all_memories = {}  # contains both cache and vp tree
        self.categorized_memory = {}  # contains both cache and vp tree
        self.n_memories = {}  # length of all_memories
        self.memory_cache = {}  # cache before put to vp tree
        self.memory_vp_tree = {}  # speed up searching memories
        self.work_memories = {}
        for mt in constants.feature_types + constants.memory_types:
            self.categorized_memory.update({mt: {}})
            self.n_memories.update({mt: 0})  # length of categorized_memories
            self.memory_cache.update({mt: set()})  # cache before put to vp tree
            self.memory_vp_tree.update({mt: None})  # speed up searching memories
            self.work_memories.update({mt: []})

    def start(self):
        brain_thread = threading.Thread(target=self.persist)
        brain_thread.daemon = True
        brain_thread.start()

    def stop(self):
        self.running = False

    def process_voice(self, voice_features_serial):
        packs = []
        for features in voice_features_serial:
            data = self.input_real(features)
            pack = self.input_memory(constants.pack, data)
            packs = self.add_seq(pack, packs)
        instant = self.input_memory(constants.instant, packs)
        instants = self.add_seq(instant, self.work_memories[constants.instant], constants.n_memory_children,
                                constants.memory_duration[constants.memory_types.index(constants.short)])
        self.work_memories[constants.instant] = instants
        short = self.input_memory(constants.short, instants)

    @util.timeit
    def input_real(self, features):
        data = set()
        for feature in features:
            m = self.find_real(feature)
            if m is None:
                m = self.add_memory(constants.real, feature, feature.type)
            else:
                self.activate_memory(m)
            data.add(m)
        return data

    @util.timeit
    def input_memory(self, memory_type, data):
        if constants.memory_types.index(memory_type) <= constants.memory_types.index(constants.instant):
            # for instant and below memory, require more at least one child
            if len(data) == 0:
                return None
        else:
            # for short and above memory, require more than one child
            if len(data) <= 1:
                return None
        memory = self.find_memory(memory_type, data)
        # if memory_type == constants.instant and memory is not None:
        #     print(f'found existing memory:{memory}')
        # if memory_type == constants.short and memory is None:
        #     print(f'adding')
        #     for x in data:
        #         print(x)
        #     print(f'all memory')
        #     for x in self.all_memories.copy().values():
        #         print(x)
        if memory is None:
            if constants.ordered == self.get_order(memory_type):
                data_ids = [x.MID for x in data]
            else:
                data_ids = {x.MID for x in data}
            memory = self.add_memory(memory_type, data_ids)
            # if memory_type == constants.instant:
            #     self.instant_set.add(util.list_to_str(data_ids))
            #     self.instant_list.append(util.list_to_str(data_ids))
            #     print(f'new instants set {len(self.instant_set)} list {len(self.instant_list)}')
            # print(f'new {memory_type} memory:{memory}')
            # print(f'all memories')
            # for x in self.all_memories[memory_type].copy().values():
            #     print(x)
            for m in data:
                m.data_indexes.add(memory.MID)
        return memory

    def add_seq(self, mm, old, n_limit=-1, time_limit=-1):
        ls = []
        if len(old) > 0:
            for x in old:
                existed = self.all_memories.get(x.MID)
                if existed is not None:
                    ls.append(x)
        if mm is None:
            return ls
        if len(ls) == 0:
            ls.append(mm)
            return ls
        if mm.data == ls[-1].data:
            return ls
        ls.append(mm)
        if 0 < n_limit < len(ls):
            ls.pop(0)
        if time_limit > 0:
            now_time = time.time()
            new_ls = []
            for x in ls:
                if now_time - x.activated_time < time_limit:
                    new_ls.append(x)
            return new_ls
        else:
            return ls

    def add_memory(self, memory_type, memory_data, real_type=None):
        m = Memory(memory_type, memory_data, real_type)
        if real_type:
            memory_type = real_type
        self.categorized_memory[memory_type].update({m.MID: m})
        self.all_memories.update({m.MID: m})
        self.memory_cache[memory_type].add(m)
        return m

    def find_real_cache(self, feature):
        recognizer = self.RECOGNIZERS[feature.type]
        cache = self.memory_cache[feature.type].copy()
        # print(f'len cache {len(cache)}')
        for m in cache:
            if recognizer.is_feature_similar(feature, m.data):
                return m

    def find_real_tree(self, feature):
        recognizer = self.RECOGNIZERS[feature.type]
        tree = self.memory_vp_tree[feature.type]
        if tree is not None:
            query = Memory(constants.real, feature, feature.type)
            distance, nearest_memory = tree.get_nearest_neighbor(query)
            if recognizer.is_similar(distance):
                return nearest_memory

    @util.timeit
    def find_real(self, feature):
        nearest = self.find_real_tree(feature)
        if nearest is None:
            nearest = self.find_real_cache(feature)
        return nearest

    @util.timeit
    def find_memory(self, memory_type, child_memories):
        if len(child_memories) == 0:
            return
        if constants.ordered == self.get_order(memory_type):
            child_ids = [x.MID for x in child_memories]
        else:
            child_ids = {x.MID for x in child_memories}
        # if memory_type == constants.instant:
        #     print(f'finding:{child_ids}')
        #     print('packs')
        #     for x in self.categorized_memory[constants.pack].copy().values():
        #         print(x)
        #     print('instant')
        #     for x in self.categorized_memory[constants.instant].copy().values():
        #         print(x)
        found_memory = None
        parent_ids = set()
        for m in child_memories:
            # print(f'm:{m}')
            parent_ids = parent_ids.union(m.data_indexes)
        # print(parent_ids)
        for pid in parent_ids:
            parent = self.all_memories.get(pid)
            if parent is None:
                # memory was deleted
                continue
            # print(p)
            if constants.ordered == self.get_order(memory_type):
                is_sub = util.is_sublist(child_memories, parent.data)
            else:
                is_sub = parent.data.issubset(child_memories)
            if is_sub:
                # if self.get_order(parent.MEMORY_TYPE) == constants.ordered:
                #     print(f'activating {parent}')
                # if parent.MEMORY_TYPE == constants.instant:
                #     print(f'activating instant: {parent}')
                self.activate_memory(parent)
            if parent.data == child_ids:
                # print(f'exist')
                # if self.get_order(parent.MEMORY_TYPE) == constants.ordered:
                #     print(f'found {parent}')
                # if parent.MEMORY_TYPE == constants.instant:
                #     print(f'found instant: {parent}')
                #     print(is_sub)
                #     print(self.get_order(memory_type))
                #     print(parent.data)
                #     print(child_ids)
                found_memory = parent
        return found_memory

    @staticmethod
    def get_order(memory_type):
        order = constants.ordered  # ordered
        if constants.memory_types.index(memory_type) <= constants.memory_types.index(constants.pack):
            order = constants.unordered  # unordered
        return order

    @classmethod
    def get_retrievability(cls, t, stability=0):
        # stability 0 is very easy to forget
        if stability == 0:
            if t <= cls.memory_cycles[0]:
                return 1
            else:
                return 0
        # for stability larger than 0
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
        bias = (len(cls.memory_cycles) - stability + 1) / len(cls.memory_cycles)
        if stability == len(cls.memory_cycles):
            # ensure it never forget
            bias = 0
        r = 1 - forget_possibility * bias
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
        if m.stability == len(cls.memory_cycles):
            return
        # strengthen if time is larger then current cycle
        # but can't continuously strengthen
        if now_time - m.CREATED_TIME > cls.memory_cycles[m.stability] and \
                now_time - m.strengthen_time > cls.memory_cycles[m.stability]:
            m.stability += 1
            m.strengthen_time = now_time
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

    # Use a separate thread to cleanup memories regularly.
    @util.timeit
    def cleanup_memories2(self):
        new_all_memories = {}
        debuged = False
        for ft in constants.feature_types + constants.memory_types:
            memories = self.categorized_memory[ft].copy()
            new_memories = {}
            for mid, m in memories.items():
                if self.validate_memory(m):
                    new_memories.update({mid: m})
                    new_all_memories.update({mid: m})
                else:
                    # print(f'{m.MEMORY_TYPE} {mid} is to be deleted')
                    # the memory need to be deleted
                    # break the downward connection
                    if isinstance(m.data, list) or isinstance(m.data, set):
                        for x in m.data:
                            child = self.all_memories.get(x)
                            # print(f'updating {x}')
                            # if not debuged:
                            #     debuged = True
                            #     for k in self.all_memories.copy():
                            #         print(k)
                            child.data_indexes.remove(mid)
                    # delete the memory, remove index
                    # break the upward connection
                    for x in m.data_indexes:
                        # if not debuged:
                        #     debuged = True
                        #     for k in self.all_memories.copy():
                        #         print(k)
                        # print(f'remove {mid} from {x} data')
                        parent = self.all_memories.get(x)
                        parent.data.remove(mid)
                        if len(parent.data) == 1:
                            equal_from = parent.MID
                            equal_to = parent.data.pop()
                            # print(f'{equal_from} ony has one child, equals to {equal_to}')
                            for y in parent.data_indexes:
                                grand_parent = self.all_memories.get(y)
                                # print(f'type of grand_parent.data {type(grand_parent.data)}')
                                if isinstance(grand_parent.data, set):
                                    # print(f'replace grand parent set data')
                                    grand_parent.data.remove(equal_from)
                                    grand_parent.data.add(equal_to)
                                elif isinstance(grand_parent.data, list):
                                    # print(f'replace grand parent list data')
                                    new_data = [equal_to if x == equal_from else x for x in grand_parent.data]
                                    grand_parent.data = new_data
            # TODO, some update may lost during this process
            self.categorized_memory.update({ft: new_memories})
            time.sleep(self.interval_s)
        self.all_memories = new_all_memories

    def cleanup_memories(self):
        new_all_memories = {}
        debuged = False
        for ft in constants.feature_types + constants.memory_types:
            memories = self.categorized_memory[ft].copy()
            new_memories = {}
            for mid, m in memories.items():
                if self.validate_memory(m):
                    new_memories.update({mid: m})
                    new_all_memories.update({mid: m})
                # refresh data index
                new_data_indexes = set()
                for di in m.data_indexes:
                    existed = self.all_memories.get(di)
                    if existed is not None:
                        new_data_indexes.add(existed.MID)
                m.data_indexes = new_data_indexes
                # refresh data
                if isinstance(m.data, list) or isinstance(m.data, set):
                    new_data = []
                    for d in m.data:
                        existed = self.all_memories.get(d)
                        if existed is not None:
                            new_data.append(existed.MID)
                    if isinstance(m.data, set):
                        new_data = set(new_data)
                    m.data = new_data
                    # re-link one child memory
                    # if len(m.data) == 1:
                    #     equal_from = m.MID
                    #     equal_to = m.data.pop()
                    #     # print(f'{equal_from} ony has one child, equals to {equal_to}')
                    #     for y in m.data_indexes:
                    #         parent = self.all_memories.get(y)
                    #         if parent is not None:
                    #             # print(f'type of parent.data {type(parent.data)}')
                    #             if isinstance(parent.data, set):
                    #                 # print(f'replace parent set data')
                    #                 parent.data.remove(equal_from)
                    #                 parent.data.add(equal_to)
                    #             elif isinstance(parent.data, list):
                    #                 # print(f'replace parent list data')
                    #                 new_data = [equal_to if x == equal_from else x for x in parent.data]
                    #                 parent.data = new_data
            # TODO, some update may lost during this process
            self.categorized_memory.update({ft: new_memories})
            time.sleep(self.interval_s)
        self.all_memories = new_all_memories

    @util.timeit
    def reindex(self):
        for ft in constants.feature_types:
            memories = self.categorized_memory[ft].copy()
            caches = self.memory_cache[ft]
            has_creation = len(caches) > 0
            has_deletion = self.n_memories[ft] != len(memories)
            if has_creation or has_deletion:
                print(f'start to reindex')
                recognizer = self.RECOGNIZERS[ft]
                memory_list = list(memories.values())
                if len(memory_list) > 0:
                    tree = vptree.VPTree(memory_list, recognizer.compare_memory)
                else:
                    tree = None
                print(f'vptree points:{len(memories)}')
                # TODO, some update may lost during this process
                self.memory_vp_tree.update({ft: tree})
                caches.clear()
                time.sleep(self.interval_s)
            self.n_memories.update({ft: len(memories)})

    def persist(self):
        while self.running:
            try:
                self.cleanup_memories()
                self.reindex()
                time.sleep(self.interval_s)
            except:
                logger.error(traceback.format_exc())
