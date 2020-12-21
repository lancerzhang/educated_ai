import logging
import math
import random
import threading
import time
import traceback

import numpy as np
import vptree

from src import constants
from src import util
from src.features import Feature
from src.memory import Memory
from src.recognizers import ImageRecognizer
from src.recognizers import VoiceRecognizer

logger = logging.getLogger('Brain')
logger.setLevel(logging.INFO)


class Brain:
    interval_s = 5 / 1000
    MEMORY_FILE = 'memories.npy'
    SELF_FUNC = 's'
    ITEM_FUNC = 'v'
    RECOGNIZERS = {constants.voice: VoiceRecognizer, constants.image: ImageRecognizer}

    memory_cycles = [15, 30, 60, 120, 60 * 5, 60 * 30, 60 * 60 * 12, 60 * 60 * 24, 60 * 60 * 24 * 2, 60 * 60 * 24 * 4,
                     60 * 60 * 24 * 7, 60 * 60 * 24 * 15, 60 * 60 * 24 * 30]

    def __init__(self):
        self.running = True
        self.all_memories = {}  # contains both cache and vp tree, for searching abstract memory
        self.categorized_memory = {}  # memories by category, for cleanup memory
        self.n_memories = {}  # length of all_memories, for compare and cleanup memory
        self.memory_cache = {}  # cache before put to vp tree, for searching real memory
        self.memory_vp_tree = {}  # speed up searching memories, for searching real memory
        # wide connection for high level memory, each 2 strong context memories have a link
        self.strong_context_memories = set()
        # memories link to strong context memory, which can use to determine next memory
        self.weak_context_memories = set()
        self.work_temporal_memories = {}
        for t in constants.feature_types + constants.memory_types:
            self.categorized_memory.update({t: {}})
            self.n_memories.update({t: 0})  # length of categorized_memories
            self.memory_cache.update({t: set()})  # cache before put to vp tree
            self.memory_vp_tree.update({t: None})  # speed up searching memories
        for f in constants.feature_types:
            for m in constants.memory_types:
                t = m + f
                self.work_temporal_memories.update({t: []})

    def start(self):
        brain_thread = threading.Thread(target=self.persist)
        brain_thread.daemon = True
        brain_thread.start()

    def stop(self):
        self.running = False

    @util.timeit
    def input_voice(self, voice_features_serial: list):
        if len(voice_features_serial) == 0:
            return
        packs = []
        for features in voice_features_serial:
            data = self.add_real_memories(features)
            pack = self.add_memory(constants.pack, data)
            packs = self.add_working(pack, packs)
        instant = self.add_memory(constants.instant, packs)
        # input short memory
        mt = constants.instant + constants.voice
        instants = self.add_working(instant, self.work_temporal_memories[mt],
                                    n_limit=constants.n_memory_children,
                                    time_limit=self.get_memory_duration(constants.short))
        self.work_temporal_memories[mt] = instants
        short = self.add_memory(constants.short, instants)
        return short

    def process(self, memories: set):
        if len(memories) == 0:
            return
        # input long memory
        shorts = []
        for short in memories:
            shorts = self.add_working(short, self.work_temporal_memories[constants.short],
                                      n_limit=constants.n_memory_children,
                                      time_limit=self.get_memory_duration(constants.long))
            self.work_temporal_memories[constants.short] = shorts
        long = self.add_memory(constants.long, shorts)
        # update contexts and synapses
        self.add_strong_contexts([long])
        self.add_strong_contexts(memories)
        self.update_weak_contexts()

    @util.timeit
    def add_real_memories(self, features: list):
        data = set()
        for feature in features:
            m = self.find_real(feature)
            if m is None:
                m = self.create_memory(constants.real, feature, feature.type)
            else:
                self.activate_memory(m)
            data.add(m)
        return data

    @util.timeit
    def add_memory(self, memory_type: str, sub_memories: list):
        if self.get_memory_type_index(memory_type) <= self.get_memory_type_index(constants.instant):
            # for instant and below memory, require more at least one child
            if len(sub_memories) == 0:
                return None
        else:
            # for short and above memory, require more than one child
            if len(sub_memories) <= 1:
                return None
        matched_parent, activated_parents, activated_children = self.find_memory(memory_type, sub_memories)
        # if memory_type == constants.instant and memory is not None:
        #     print(f'found existing memory:{memory}')
        # if memory_type == constants.short and memory is None:
        #     print(f'adding')
        #     for x in data:
        #         print(x)
        #     print(f'all memory')
        #     for x in self.all_memories.copy().values():
        #         print(x)
        if matched_parent is None:
            matched_parent = self.create_memory(memory_type, [x.MID for x in sub_memories])
            for m in sub_memories:
                m.data_indexes.add(matched_parent.MID)
        # for x in activated_parents:
        #     t = x.MEMORY_TYPE
        #     self.work_memories[t] = util.list_remove(self.work_memories[t], x)
        # for x in activated_children:
        #     x = self.all_memories.get(x)
        #     if x is not None:
        #         t = x.MEMORY_TYPE
        #         self.work_memories[t] = util.list_remove(self.work_memories[t], x)
        return matched_parent

    @util.timeit
    def add_working(self, mm: Memory, old: list, n_limit=-1, time_limit=-1):
        ls = self.get_valid_memories(old, output_type='Memory')
        if mm is None:
            return ls
        if len(ls) == 0:
            ls.append(mm)
        elif ls[-1].data != mm.data:
            ls.append(mm)
        if n_limit > 0:
            while n_limit < len(ls):
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

    @util.timeit
    def create_memory(self, memory_type: str, memory_data, real_type: str = None):
        m = Memory(memory_type, memory_data, real_type)
        if real_type:
            t = real_type
            self.memory_cache[t].add(m)
        else:
            t = memory_type
        self.categorized_memory[t].update({m.MID: m})
        self.all_memories.update({m.MID: m})
        return m

    def add_strong_contexts(self, memories):
        new_memories = set()
        for m in memories:
            if m is None or m.stability < constants.stable:
                continue
            if m not in self.strong_context_memories:
                self.strong_context_memories.add(m)
                new_memories.add(m)
        self.update_strong_contexts()
        for x in new_memories:
            self.add_links(x)

    def add_links(self, m: Memory):
        for x in self.strong_context_memories:
            if x != m:
                sub_memories = [x, m]
                matched_parent = self.find_link(sub_memories)
                if matched_parent is None:
                    matched_parent = self.create_memory(constants.link, sub_memories)
                    for y in sub_memories:
                        y.link_indexes.add(matched_parent.MID)

    def update_strong_contexts(self, n_context=constants.n_memory_context):
        live_memories = self.get_valid_memories(self.strong_context_memories.copy(), output_type='Memory')
        memories = []
        for m in live_memories:
            if time.time() - m.activated_time < self.get_memory_duration(m.MEMORY_TYPE):
                memories.append(m)
        if len(memories) > n_context:
            s_list = sorted(memories, key=lambda x: (x.stability, x.context_weight, x.activated_time), reverse=True)
            n_list = s_list[0:n_context]
            memories = set(n_list)
        self.strong_context_memories = memories

    def update_weak_contexts(self):
        link_ids = set()
        for m in self.strong_context_memories:
            link_ids = link_ids.union(m.link_indexes)
        valid_links = self.get_valid_memories(link_ids, output_type='Memory')
        week_memories = set()
        for link in valid_links:
            week_memories = week_memories.union(link.data)
        self.weak_context_memories = self.get_valid_memories(week_memories, output_type='Memory')

    @util.timeit
    def find_real_cache(self, feature: Feature):
        recognizer = self.RECOGNIZERS[feature.type]
        cache = self.memory_cache[feature.type].copy()
        # print(f'len cache {len(cache)}')
        for m in cache:
            if recognizer.is_feature_similar(feature, m.data):
                return m

    @util.timeit
    def find_real_tree(self, feature: Feature):
        recognizer = self.RECOGNIZERS[feature.type]
        tree = self.memory_vp_tree[feature.type]
        if tree is not None:
            query = Memory(constants.real, feature, feature.type)
            distance, nearest_memory = tree.get_nearest_neighbor(query)
            if recognizer.is_similar(distance):
                return nearest_memory

    @util.timeit
    def find_real(self, feature: Feature):
        nearest = self.find_real_tree(feature)
        if nearest is None:
            nearest = self.find_real_cache(feature)
        return nearest

    @util.timeit
    def find_memory(self, memory_type: str, child_memories: list):
        if len(child_memories) == 0:
            return
        child_ids = util.create_data(memory_type, [x.MID for x in child_memories])
        # if memory_type == constants.instant:
        #     print(f'finding:{child_ids}')
        #     print('packs')
        #     for x in self.categorized_memory[constants.pack].copy().values():
        #         print(x)
        #     print('instant')
        #     for x in self.categorized_memory[constants.instant].copy().values():
        #         print(x)
        match_parent = None
        parent_ids = set()
        for m in child_memories:
            # print(f'm:{m}')
            parent_ids = parent_ids.union(m.data_indexes)
        # print(parent_ids)
        parents = self.get_valid_memories(parent_ids, output_type='Memory')
        activated_parents = set()
        activated_children = set()
        for parent in parents:
            if constants.ordered == util.get_order(memory_type):
                is_sub = util.is_sublist(child_memories, parent.data)
            else:
                is_sub = util.is_subset(parent.data, set(child_memories))
            if is_sub:
                # if self.get_order(parent.MEMORY_TYPE) == constants.ordered:
                #     print(f'activating {parent}')
                # if parent.MEMORY_TYPE == constants.instant:
                #     print(f'activating instant: {parent}')
                self.activate_memory(parent)
                activated_parents.add(parent)
                activated_children = activated_children.union(set(parent.data))
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
                match_parent = parent
        return match_parent, activated_parents, activated_children

    def find_link(self, child_memories: list):
        if len(child_memories) != 2:
            return
        index1 = child_memories[0].link_indexes
        index2 = child_memories[1].link_indexes
        found = index1.intersection(index2)
        if len(found) == 0:
            return
        elif len(found) == 1:
            result = found.pop()
            if result in self.all_memories:
                return result
            else:
                return
        else:
            print(f'this wont happen')

    # @util.timeit
    # def find_context(self, child_memories: list):
    #     context_ids = set.intersection(*[x.context_indexes for x in child_memories])
    #     contexts = self.get_valid_memories(context_ids, output_type='Memory')
    #     return contexts

    @classmethod
    def get_retrievability(cls, t, stability=0):
        # stability 0 is very easy to forget
        if stability == 0:
            if t <= cls.memory_cycles[0]:
                return 1
        #     else:
        #         return 0
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
    def is_steady(cls, m: Memory):
        now_time = time.time()
        # print(f'now {now_time}, at {m.activated_time}, stb {m.stability}')
        if now_time < m.activated_time + cls.memory_cycles[m.stability]:
            return True
        else:
            return False

    @util.timeit
    def get_valid_memories(self, src, output_type='mid'):
        memories = []
        for x in src.copy():
            if type(x) == Memory:
                x = x.MID
            existed = self.all_memories.get(x)
            if existed is not None:
                if output_type == 'mid':
                    memories.append(existed.MID)
                else:
                    memories.append(existed)
        if type(src) == set:
            memories = set(memories)
        return memories

    @staticmethod
    def get_memory_type_index(memory_type: str):
        return constants.memory_types.index(memory_type)

    @classmethod
    def get_memory_duration(cls, memory_type: str):
        return constants.memory_duration[cls.get_memory_type_index(memory_type)]

    @classmethod
    def activate_memory(cls, m: Memory):
        # if constants.short == m.MEMORY_TYPE:
        #     print(f'activated {m.MID}')
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
    def validate_memory(cls, m: Memory):
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
    def update_weight(item, memory_indexes):
        item.context_weight = math.log(len(memory_indexes) / len(item.link_indexes))
        item.data_weight = math.log(len(memory_indexes) / len(item.data_indexes))

    def cleanup_memories(self):
        new_all_memories = {}
        for t in constants.feature_types + constants.memory_types:
            memories = self.categorized_memory[t].copy()
            new_memories = {}
            for mid, m in memories.items():
                if self.validate_memory(m):
                    new_memories.update({mid: m})
                    new_all_memories.update({mid: m})
                # refresh data index
                m.data_indexes = self.get_valid_memories(m.data_indexes)
                # refresh data
                if isinstance(m.data, list) or isinstance(m.data, set):
                    m.data = self.get_valid_memories(m.data)
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
            self.categorized_memory.update({t: new_memories})
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
                logger.debug(f'start to reindex')
                recognizer = self.RECOGNIZERS[ft]
                memory_list = list(memories.values())
                if len(memory_list) > 0:
                    tree = vptree.VPTree(memory_list, recognizer.compare_memory)
                else:
                    tree = None
                logger.debug(f'vptree points:{len(memories)}')
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
                self.save()
                time.sleep(self.interval_s)
            except:
                logger.error(traceback.format_exc())

    # Use a separate thread to persist memories to storage regularly.
    @util.timeit
    def save(self):
        try:
            np.save(self.MEMORY_FILE, self.all_memories)
        except:
            logging.error(traceback.format_exc())

    @util.timeit
    def load(self):
        try:
            memories = np.load(self.MEMORY_FILE, allow_pickle=True).item()
            self.all_memories = memories
            for m in memories.values():
                t = m.MEMORY_TYPE
                if m.REAL_TYPE is not None:
                    t = m.REAL_TYPE
                    self.memory_cache[t].add(m)
                self.categorized_memory[t].update({m.MID: m})
            self.reindex()
        except:
            logging.error(traceback.format_exc())
