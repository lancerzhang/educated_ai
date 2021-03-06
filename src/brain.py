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
from src.recognizers import SpeechRecognizer
from src.recognizers import VisionRecognizer
from src.memory_list import MemoryList

logger = logging.getLogger('Brain')
logger.setLevel(logging.INFO)


class Brain:
    interval_s = 5 / 1000
    MEMORY_FILE = 'memories.npy'
    SELF_FUNC = 's'
    ITEM_FUNC = 'v'
    DURATION = 5
    RECOGNIZERS = {constants.speech: SpeechRecognizer, constants.vision: VisionRecognizer}

    memory_cycles = [15, 30, 60, 120, 60 * 5, 60 * 30, 60 * 60 * 12, 60 * 60 * 24, 60 * 60 * 24 * 2, 60 * 60 * 24 * 4,
                     60 * 60 * 24 * 7, 60 * 60 * 24 * 15, 60 * 60 * 24 * 30]

    def __init__(self):
        self.running = True
        self.all_memories = {}  # contains both cache and vp tree, for searching abstract memory
        # self.categorized_memory = {}  # memories by category, for cleanup memory
        # self.n_memories = {}  # length of all_memories, for compare and cleanup memory
        self.feature_memory_cache = {}  # cache before put to vp tree, for searching feature memory
        self.feature_memories = {}  # speed up searching memories, for searching feature memory
        self.context_memories = set()  # acknowledged context memories
        self.context_task = set()  # partial acknowledged context memories
        self.working_memory_lists = MemoryList(self.DURATION)  # use single time line for all memories
        self.last_processed = {}
        # self.origin_temporal_memories = []
        # for t in constants.feature_types + constants.memory_types:
        #     self.categorized_memory.update({t: {}})
        #     self.n_memories.update({t: 0})  # length of categorized_memories
        for sense_type in constants.sense_types:
            self.feature_memory_cache.update({sense_type: set()})  # cache before put to vp tree
            self.feature_memories.update(
                {sense_type: vptree.VPTree([], lambda a, b: False)})  # speed up searching memories
            # self.working_memory_lists.update({sense_type: TimedList(self.DURATION)})

    def start(self):
        brain_thread = threading.Thread(target=self.persist)
        brain_thread.daemon = True
        brain_thread.start()

    def stop(self):
        self.running = False

    @util.timeit
    def receive_vision(self, features):
        if len(features) == 0:
            return
        feature_type = constants.vision
        self.add_sense(feature_type, features)

    @util.timeit
    def receive_speech(self, features_list: list):
        if len(features_list) == 0:
            return
        sense_type = constants.speech
        for features in features_list:
            self.add_sense(sense_type, features)

    def add_sense(self, sense_type, features):
        feature_memories = self.add_feature_memories(features)
        sense_memory = self.add_memory(feature_memories)
        self.working_memory_lists[sense_type].append(sense_memory)

    def rebuild_context(self):
        new_context = set()
        # remove outdated context
        for m in self.context_memories:
            if time.time() - m.activated_time < self.DURATION:
                new_context.add(m)
        # put processed memory to context
        for sense_type in constants.sense_types:
            processed = self.working_memory_lists[sense_type].processed
            for m in processed:
                new_context.add(m)
        self.context_memories = new_context

    def recognize(self):
        for sense_type in constants.sense_types:
            self.working_memory_lists[sense_type].prepare()
        self.rebuild_context()
        for sense_type in constants.sense_types:
            new_working = self.coalesce_memory(sense_type)
            self.working_memory_lists[sense_type].rebuild(new_working)

    def coalesce_memory(self, sense_type):
        working = self.working_memory_lists[sense_type].processing
        return working

    def segment_memories(self, memory_list, position_list, reverse=False):
        if reverse:
            end = position_list[-1]
            while end > 0:
                for width in reversed(range(constants.n_memory_children)):
                    start = end - width - 1
                    if width == 1:
                        position_list.append(start)
                        end = start
                        break
                    if end > len(memory_list):
                        break
                    child_memories = memory_list[start:end]
                    parent_memories, _ = self.find_parents(child_memories)
                    if len(parent_memories) > 0:
                        position_list.append(start)
                        end = start
                        break
        else:
            start = position_list[-1]
            while start < len(memory_list):
                for width in reversed(range(constants.n_memory_children)):
                    end = start + width + 1
                    if width == 1:
                        position_list.append(end)
                        start = end
                        break
                    if end > len(memory_list):
                        break
                    child_memories = memory_list[start:end]
                    parent_memories, _ = self.find_parents(child_memories)
                    if len(parent_memories) > 0:
                        position_list.append(end)
                        start = end
                        break
        return position_list

    # need to call before a frame
    def prepare_frame(self):
        for _, working_queue in self.working_memory_lists.items():
            working_queue.delete_expired()

    @util.timeit
    def control(self, m: Memory, actions):
        if m.action is not None:
            m.action.control()
        else:
            for ac in actions:
                pass

    @util.timeit
    def add_feature_memories(self, features: list):
        data = set()  # use set to prevent duplicated memory
        for feature in features:
            m = self.find_feature(feature)
            if m is None:
                m = self.create_memory(constants.feature, feature, feature.type)
            else:
                self.activate_memory(m)
            data.add(m)
        return data

    def get_parent_type(self, m: Memory):
        idx = self.get_memory_type_index(m.MEMORY_TYPE)
        if idx < len(constants.memory_types) - 1:
            idx += 1
        return constants.memory_types[idx]

    # @util.timeit
    def add_memory(self, sub_memories: list):
        if len(sub_memories) == 0:
            return None
        memory_type = self.get_parent_type(sub_memories[0])
        if memory_type == constants.temporal and len(sub_memories) <= 1:
            # for temporal memory, require more than one child
            return None
        full_matches, partial_matches = self.find_parents(sub_memories)
        for m in partial_matches:
            self.activate_memory(m)
        if len(full_matches) == 0:
            result = self.create_memory(memory_type, sub_memories)
        else:
            if memory_type == constants.temporal:
                sorted_memories = self.sort_context(full_matches)
                best_match = sorted_memories[0]
                context_ids = {x.MID for x in self.context_memories}
                if context_ids == best_match.link:
                    # contexts of best match equal current contexts
                    result = best_match
                else:
                    common_contexts = self.get_common_contexts(best_match)
                    if len(common_contexts) == 0:
                        # if no common context, then create a new memory with current context
                        result = self.create_memory(memory_type, sub_memories, context=self.context_memories)
                    else:
                        # search if there is memory with common context
                        existing = self.match_contexts(full_matches, common_contexts)
                        if existing is None:
                            result = self.create_memory(memory_type, sub_memories, context=common_contexts)
                        else:
                            result = existing
            else:
                result = full_matches.pop()
        return result

    def sort_context(self, memories):
        return sorted(memories, key=lambda x: (self.get_context_weight(x), x.stability), reverse=True)

    def get_common_contexts(self, m: Memory):
        ctx_ids = {x.MID for x in self.context_memories}
        common_ids = ctx_ids.intersection(m.context)
        return self.get_valid_memories(common_ids, output_type='Memory')

    def get_context_weight(self, m: Memory):
        return sum(x.context_weight for x in self.get_common_contexts(m))

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
    def create_memory(self, memory_type: str, memory_data, real_type: str = None, context=None):
        m = Memory(memory_type, memory_data, real_type)
        if real_type:
            t = real_type
            self.feature_memory_cache[t].add(m)
        else:
            t = memory_type
        self.all_memories.update({m.MID: m})
        # for non real memory, update data indexes
        if self.get_memory_type_index(memory_type) > 0:
            for d in memory_data:
                d.data_indexes.add(m.MID)
        memory_context = set()
        if context is None:
            if memory_type == constants.temporal:
                memory_context = self.context_memories
        else:
            memory_context = context
        if len(memory_context) > 0:
            m.context = {x.MID for x in memory_context}
            for c in memory_context:
                c.context_indexes.add(m.MID)
        return m

    @util.timeit
    def find_feature_cache(self, feature: Feature):
        recognizer = self.RECOGNIZERS[feature.type]
        cache = self.feature_memory_cache[feature.type].copy()
        # print(f'len cache {len(cache)}')
        for m in cache:
            if recognizer.is_feature_similar(feature, m.data):
                return m

    @util.timeit
    def find_feature_tree(self, feature: Feature):
        recognizer = self.RECOGNIZERS[feature.type]
        tree = self.feature_memories[feature.type]
        if tree is not None:
            query = Memory(constants.instant, feature, feature.type)
            distance, nearest_memory = tree.get_nearest_neighbor(query)
            if recognizer.is_similar(distance):
                return nearest_memory

    @util.timeit
    def find_feature(self, feature: Feature):
        nearest = self.find_feature_tree(feature)
        if nearest is None:
            nearest = self.find_feature_cache(feature)
        return nearest

    # @util.timeit
    def find_parents(self, child_memories: list):
        if len(child_memories) == 0:
            return
        memory_type = self.get_parent_type(child_memories[0])
        child_ids = util.create_data(memory_type, [x.MID for x in child_memories])
        full_matches = set()
        partial_matches = set()
        parent_ids = set()
        for m in child_memories:
            parent_ids = parent_ids.union(m.data_indexes)
        parents = self.get_valid_memories(parent_ids, output_type='Memory')
        for parent in parents:
            if constants.temporal == memory_type:
                is_sub = util.is_sublist(child_memories, parent.data)
            else:
                is_sub = util.is_subset(parent.data, set(child_memories))
            if is_sub:
                partial_matches.add(parent)
            if parent.data == child_ids:
                full_matches.add(parent)
        return full_matches, partial_matches

    @staticmethod
    def is_stable(m: Memory):
        if m.stability < constants.stable:
            return False
        else:
            return True

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
    def match_contexts(memories, context):
        context_ids = {x.MID for x in context}
        for m in memories:
            if m.link == context_ids:
                return m

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

    def update_context_weight(self, m: Memory):
        if len(m.context_indexes) == 0:
            m.context_weight = 0
        else:
            m.context_weight = math.log(len(self.all_memories) / len(m.context_indexes))

    def update_data_weight(self, m: Memory):
        if len(m.data_indexes) == 0:
            m.data_weight = 0
        else:
            m.data_weight = math.log(len(self.all_memories) / len(m.data_indexes))

    def cleanup_memories(self):
        new_all_memories = {}
        for t in constants.sense_types + constants.memory_types:
            memories = self.categorized_memory[t].copy()
            new_memories = {}
            for mid, m in memories.items():
                if self.validate_memory(m):
                    new_memories.update({mid: m})
                    new_all_memories.update({mid: m})
                    # refresh data and index
                    m.data_indexes = self.get_valid_memories(m.data_indexes)
                    m.link = self.get_valid_memories(m.link)
                    m.context_indexes = self.get_valid_memories(m.context_indexes)
                    self.update_context_weight(m)
                    self.update_data_weight(m)
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
        for ft in constants.sense_types:
            memories = self.categorized_memory[ft].copy()
            caches = self.feature_memory_cache[ft]
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
                self.feature_memories.update({ft: tree})
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
                if m.FEATURE_TYPE is not None:
                    t = m.FEATURE_TYPE
                    self.feature_memory_cache[t].add(m)
                self.categorized_memory[t].update({m.MID: m})
            self.reindex()
        except:
            logging.error(traceback.format_exc())
