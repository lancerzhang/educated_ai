import copy
import hashlib
import logging
import random
import time

import numpy as np

from components import util

logger = logging.getLogger('Memory')
logger.setLevel(logging.INFO)


class MemoryType:
    REAL = 0  # one real memory
    SLICE = 1  # collection of one type of real memories
    INSTANT = 2  # collection of slice memories in a short time
    SHORT = 3
    LONG = 4


class RealType:
    SOUND_FEATURE = 0
    VISION_FEATURE = 1
    VISION_FOCUS_MOVE = 2
    VISION_FOCUS_ZOOM = 3
    ACTION_MOUSE_CLICK = 4
    ACTION_REWARD = 5


class MemoryStatus:
    # dormant memories will be clean up in high priority
    # dormant memories can't be activated
    # dormant memories can be retrieved if it's yet clean up, recall count will be kept
    DORMANT = 0
    SLEEP = 1
    LIVING = 2
    MATCHED = 3
    MATCHING = 4


MEMORY_DURATIONS = [0.15, 0.15, 0.5, 5, 20]
MEMORY_TYPES_LENGTH = 5
MEMORY_FEATURES_LENGTH = 6
COMPOSE_NUMBER = 4
GREEDY_RATIO = 0.8
NOT_FORGET_STEP = 10
BASE_DESIRE = 0.1
BASE_STRENGTH = 0.1

TIME_SEC = [5, 6, 8, 11, 15, 20, 26, 33, 41, 50, 60, 71, 83, 96, 110, 125, 141, 158, 176, 196, 218, 242, 268, 296,
            326, 358, 392, 428, 466, 506, 548, 593, 641, 692, 746, 803, 863, 926, 992, 1061, 1133, 1208, 1286, 1367,
            1451, 1538, 1628, 1721, 1920, 2100, 2280, 2460, 2640, 2880, 3120, 3360, 3600, 4680, 6120, 7920, 10440,
            14040, 18720, 24840, 32400, 41760, 52920, 66240, 81720, 99720, 120240, 143640, 169920, 222480, 327600,
            537840, 853200, 1326240, 2035800, 3100140, 3609835, 4203316, 4894372, 5699043, 6636009, 7727020,
            8997403, 10476649, 12199095, 14204727, 16540102, 19259434, 22425848, 26112847, 30406022, 35405033,
            41225925, 48003823, 55896067, 65085866]


def construct_loop(mset, mdict):
    changed_set = set()
    for m in mset:
        # is_parent_changed = False
        # new_parent = set()
        # for x in m.parent:
        #     if util.is_int(x):
        #         is_parent_changed = True
        #         npr = mdict.get(x)
        #         if npr:
        #             new_parent.add(npr)
        #     else:
        #         new_parent.add(x)
        # if is_parent_changed:
        #     m.parent = new_parent
        is_children_changed = False
        new_children = []
        for x in m.children:
            if util.is_int(x):
                is_children_changed = True
                ncd = mdict.get(x)
                if ncd:
                    new_children.append(ncd)
            else:
                new_children.append(x)
        if is_children_changed:
            m.children = new_children
            # if is_parent_changed or is_children_changed:
            changed_set.add(m)
    if len(changed_set) > 0:
        construct_loop(changed_set, mdict)


def construct(memories):
    new_memories = copy.copy(memories)
    mdict = dict((x.mid, x) for x in memories)
    construct_loop(new_memories, mdict)
    return new_memories


def create_children_hash(children, memory_type):
    if memory_type is MemoryType.SLICE:
        return util.create_list_hash(children, False)
    else:
        return util.create_list_hash(children, True)


class Memory:
    # live = True
    protect_time = 0
    reward = 0
    desire = 0
    strength = 0

    # for active period
    status = None
    matched_time = None
    active_end_time = None

    def __init__(self, memory_type, real_type=None, children=None, kernel=None, feature=None, channel=None,
                 click_type=None, degrees=None, speed=None, duration=None, zoom_type=None, zoom_direction=None):
        self.created_time = time.time()
        self.status = MemoryStatus.MATCHED
        self.matched_time = time.time()
        self.recall_count = 0
        self.last_recall_time = time.time()
        # self.parent = set()
        # below variable should not be change after init
        self.memory_type = memory_type
        self.real_type = real_type
        self.kernel = kernel
        self.feature = feature
        self.channel = channel
        self.click_type = click_type
        self.degrees = degrees
        self.speed = speed
        self.duration = duration
        self.zoom_type = zoom_type
        self.zoom_direction = zoom_direction
        if children:
            self.children = children
        else:
            self.children = []
        self.mid = self.create_hash()
        self.kernel_index = self.create_kernel_hash()

    def __hash__(self):
        return self.mid

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return other == self.mid

    # add protect time to prevent frequent calculation of deletion
    @util.timeit
    def calculate_protect_time(self, recall_count):
        time_seq = np.array(TIME_SEC)
        end_number = recall_count + NOT_FORGET_STEP
        if end_number > len(time_seq):
            end_number = len(time_seq)
        sub_arr = time_seq[recall_count:end_number]
        return time.time() + np.sum(sub_arr)

    def cleanup_refresh(self, arg=None):
        self.refresh_self(recall=False, is_forget=True)

    # longer time elapsed, easier to forget
    # more times recall, harder to forget
    # can not recall frequently in short time
    @util.timeit
    def refresh_self(self, recall=False, is_forget=False):
        now_time = time.time()
        time_elapse = now_time - self.last_recall_time
        if time_elapse < TIME_SEC[0]:
            return
        count = 0
        for num in range(self.recall_count, len(TIME_SEC)):
            if TIME_SEC[num] <= time_elapse:
                count = count + 1
            else:
                # if go to next section
                if count > 0:
                    # random forget memory base on strength
                    if is_forget and time.time() > self.protect_time:
                        self.protect_time = self.calculate_protect_time(self.recall_count)
                        ran = random.randint(1, 100)
                        strength = 100 - count
                        if ran > strength:
                            self.hibernate()
                            break
                    # if this is recall, will update recall count and last recall time
                    if recall:
                        self.recall_count += 1
                        self.last_recall_time = time.time()
                break

    @util.timeit
    def recall(self):
        self.refresh_self(True, False)

    @util.timeit
    def calculate_desire(self):
        elapse = time.time() - self.matched_time
        # linear func, weight is 0 at beginning, it's 1 after 400 seconds
        f = 0.0025 * elapse
        desire = BASE_DESIRE + self.reward * f
        desire = desire if desire < 1 else 1
        self.desire = desire

    def get_desire(self):
        self.calculate_desire()
        return self.desire

    def get_active_time(self):
        active_start = self.active_end_time - self.get_duration()
        return time.time() - active_start

    @util.timeit
    def calculate_strength(self):
        elapse = self.get_active_time()
        f = 1 - elapse / MEMORY_DURATIONS[-1]
        if f < 0:
            f = 0
        raw = self.recall_count / 100
        strength = BASE_STRENGTH + raw * f
        strength = strength if strength < 1 else 1
        self.strength = strength

    def get_strength(self):
        self.calculate_strength()
        return self.strength

    @util.timeit
    def match_children(self):
        if self.status is not MemoryStatus.MATCHING:
            return
        logger.debug(f'match_children:{self.mid}')
        count = 0
        rest_not_matched = set()
        for m in self.children:
            # ignore dormant memory as it's forgot
            if m.status is MemoryStatus.DORMANT:
                continue
            if (time.time() - m.matched_time) < self.get_duration():
                count += 1
            else:
                rest_not_matched.add(m)
        if util.greater_than_half(count, len(self.children)):
            logger.debug(f'matched_children:{self.mid}')
            # self.render_tree(set())
            self.matched()
            for m in rest_not_matched:
                m.matched()

    # @util.timeit
    # Sleep > Matching
    def activate(self):
        # logger.debug(f'activate_memory:{self.mid}')
        self.status = MemoryStatus.MATCHING
        # keep it in active memories for matching
        self.active_end_time = time.time() + self.get_duration()

    @util.timeit
    # call this right after the memory is matched. Matching > Matched
    def matched(self, recall=True):
        logger.debug(f'matched_memory:{self.mid}')
        # normally change memory status from Matching to Matched
        # but there also maybe form dormant to Matched
        if self.status is MemoryStatus.DORMANT:
            logger.debug(f'activated dormant memory:{self.mid}')
        self.status = MemoryStatus.MATCHED
        self.matched_time = time.time()
        # extend active end time when it's matched, keeping it in active memories for composing
        self.active_end_time = time.time() + self.get_duration()
        if self.recall_count > 50:
            print(f'match: t.{self.memory_type} r.{self.real_type} {self.mid}')
        if recall:
            self.recall()

    # call this after the memory is confirmed matched by brain. Matched > Living
    def post_matched(self):
        self.status = MemoryStatus.LIVING

    # Living > SLEEP
    def deactivate(self):
        self.status = MemoryStatus.SLEEP
        self.active_end_time = 0

    # Sleep > Dormant, this memory won't be used, waiting to be clean up
    def hibernate(self):
        self.status = MemoryStatus.DORMANT

    def create_hash(self):
        raw = f'{self.memory_type}|{self.real_type}|{self.kernel}|{self.feature}|{self.channel}|{self.click_type}|' \
              f'{self.degrees}|{self.speed}|{self.duration}|{self.zoom_type}|{self.zoom_direction}|'
        children = [x.mid for x in self.children]
        if self.memory_type is MemoryType.SLICE:
            children = sorted(children)
        raw += f'{children}'
        return int(hashlib.md5(raw.encode('utf-8')).hexdigest(), 16)

    def create_kernel_hash(self):
        raw = f'{self.memory_type}|{self.real_type}|{self.kernel}|{self.channel}'
        return hashlib.md5(raw.encode('utf-8')).hexdigest()

    @util.timeit
    def create_kernel_index(self, indexes: dict):
        util.dict_set_add(indexes, self.kernel_index, self)

    @util.timeit
    def create_common_index(self, indexes: dict):
        indexes.update({self.mid: self})

    @util.timeit
    def create_children_index(self, indexes: dict):
        children_id_list = [x.mid for x in self.children]
        if self.memory_type is MemoryType.SLICE:
            sub_sets = util.list_combinations(children_id_list, False)
        else:
            sub_sets = util.list_combinations(children_id_list, True)
        for sub_set in sub_sets:
            k = create_children_hash(sub_set, self.memory_type)
            util.dict_set_add(indexes, k, self)

    @util.timeit
    def create_index(self, indexes):
        self.create_common_index(indexes)
        if self.real_type in [RealType.SOUND_FEATURE, RealType.VISION_FEATURE]:
            self.create_kernel_index(indexes)
        if len(self.children) > 0:
            self.create_children_index(indexes)

    def get_duration(self):
        return MEMORY_DURATIONS[self.memory_type]

    def simple_str(self):
        # parent = {x.mid for x in self.parent}
        children = [x.mid for x in self.children]
        return f'[id:{self.mid},type:{self.memory_type},feature:{self.real_type},recall:{self.recall_count},' \
               f'reward:{self.reward},status:{self.status},matched_time:{time.ctime(self.matched_time)}' \
               f',created_time:{time.ctime(self.created_time)}' \
               f',children:{children}]'

    # @util.timeit
    def render_tree(self, temp_set, level=1, max_level=30):
        if level >= max_level:
            # print('hit max level, return')
            return
        level_line = ''
        for i in range(0, level):
            level_line = '---{0}'.format(level_line)
        # if self.status is MemoryStatus.DORMANT:
        #     print('dead')
        # else:
        if self.memory_type < 4:
            if self.mid not in temp_set:
                # leaf = f'L{level}:{level_line} id:{self.mid},type:{self.memory_type},count:{self.recall_count}'
                leaf = f'T{self.memory_type}:{level_line} {self.simple_str()}'
                print(leaf)
                logger.debug(leaf)
                temp_set.add(self.mid)
        sub_level = level + 1
        for child in self.children:
            child.render_tree(temp_set, sub_level, max_level)
