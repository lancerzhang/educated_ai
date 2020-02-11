from . import constants
from components import util
import copy
import hashlib
import logging
import numpy as np
import random
import time

logger = logging.getLogger('Memory')
logger.setLevel(logging.INFO)
MEMORY_DURATIONS = [0.15, 0.15, 0.5, 3, 60]
MEMORY_TYPES = [constants.FEATURE_MEMORY, constants.SLICE_MEMORY, constants.INSTANT_MEMORY, constants.SHORT_MEMORY,
                constants.LONG_MEMORY]
MEMORY_FEATURES = [constants.SOUND_FEATURE, constants.VISION_FEATURE, constants.VISION_FOCUS_MOVE,
                   constants.VISION_FOCUS_ZOOM, constants.ACTION_MOUSE_CLICK, constants.ACTION_REWARD]
COMPOSE_NUMBER = 4
GREEDY_RATIO = 0.8
NOT_FORGET_STEP = 10
BASE_DESIRE = 0.1
BASE_STRENGTH = 0.1
id_sequence = 0

TIME_SEC = [5, 6, 8, 11, 15, 20, 26, 33, 41, 50, 60, 71, 83, 96, 110, 125, 141, 158, 176, 196, 218, 242, 268, 296,
            326, 358, 392, 428, 466, 506, 548, 593, 641, 692, 746, 803, 863, 926, 992, 1061, 1133, 1208, 1286, 1367,
            1451, 1538, 1628, 1721, 1920, 2100, 2280, 2460, 2640, 2880, 3120, 3360, 3600, 4680, 6120, 7920, 10440,
            14040, 18720, 24840, 32400, 41760, 52920, 66240, 81720, 99720, 120240, 143640, 169920, 222480, 327600,
            537840, 853200, 1326240, 2035800, 3100140, 3609835, 4203316, 4894372, 5699043, 6636009, 7727020,
            8997403, 10476649, 12199095, 14204727, 16540102, 19259434, 22425848, 26112847, 30406022, 35405033,
            41225925, 48003823, 55896067, 65085866]


def create():
    m = Memory()
    m.assign_id()
    return m


def get_memory_type(memory_type_str):
    return MEMORY_TYPES.index(memory_type_str)


def get_feature_type(feature_type_str):
    return MEMORY_FEATURES.index(feature_type_str)


@util.timeit
def flatten(memories):
    new_memories = set()
    for m in memories.copy():
        nm = copy.copy(m)
        nm.parent = set([x.mid for x in m.parent])
        nm.children = [x.mid for x in m.children]
        new_memories.add(nm)
    return new_memories


def construct_loop(mset, mdict):
    changed_set = set()
    for m in mset:
        is_parent_changed = False
        new_parent = set()
        for x in m.parent:
            if util.is_int(x):
                is_parent_changed = True
                npr = mdict.get(x)
                if npr:
                    new_parent.add(npr)
            else:
                new_parent.add(x)
        if is_parent_changed:
            m.parent = new_parent
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
        if is_parent_changed or is_children_changed:
            changed_set.add(m)
    if len(changed_set) > 0:
        construct_loop(changed_set, mdict)


def construct(memories):
    new_memories = copy.copy(memories)
    mdict = dict((x.mid, x) for x in memories)
    construct_loop(new_memories, mdict)
    return new_memories


class Memory:
    mid = 0
    live = True
    memory_type = None
    feature_type = None
    recall_count = 1
    created_time = 0
    last_recall_time = 0
    protect_time = 0
    reward = 0
    desire = 0
    strength = 0
    parent = None
    children = None

    # for active period
    status = None  # constants.MATCHED, constants.MATCHING, constants.DORMANT
    matched_time = None
    active_end_time = None

    kernel = None
    feature = None
    channel = None
    click_type = None
    degrees = None
    speed = None
    duration = None
    zoom_type = None
    zoom_direction = None

    def __init__(self):
        self.created_time = time.time()
        self.status = constants.MATCHED
        self.matched_time = time.time()
        self.recall_count = 1
        self.last_recall_time = time.time()
        self.parent = set()
        self.children = []

    def __hash__(self):
        return int(self.mid)

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return other == self.mid

    def assign_id(self):
        global id_sequence
        id_sequence += 1
        self.mid = id_sequence

    # add protect time to prevent frequent calculation of deletion
    @util.timeit
    def calculate_protect_time(self, recall_count):
        time_seq = np.array(TIME_SEC)
        end_number = recall_count + NOT_FORGET_STEP
        if end_number > len(time_seq):
            end_number = len(time_seq)
        sub_arr = time_seq[recall_count:end_number]
        return time.time() + np.sum(sub_arr)

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
                            self.kill()
                            break
                    # if this is recall, will update recall count and last recall time
                    if recall:
                        self.recall_count += 1
                        self.last_recall_time = time.time()
                break

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
        active_start = self.active_end_time - MEMORY_DURATIONS[self.memory_type]
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
    def activate(self):
        logger.debug(f'activating {self.simple_str()}')
        if not self.live:
            return False
        if self.status is not constants.DORMANT:
            return False
        self.status = constants.MATCHING
        logger.debug(f'activated {self.simple_str()}')
        # keep it in active memories for matching
        self.active_end_time = time.time() + MEMORY_DURATIONS[self.memory_type]
        return True

    @util.timeit
    def match_children(self):
        # if self.memory_type > 0:
        #     logger.debug(f'matching_memory {self.simple_str()}')
        if self.status != constants.MATCHING:
            return False

        for m in self.children:
            # if self.memory_type > 0:
            #     logger.debug(f'child_memory {m.simple_str()}')
            if m.status != constants.MATCHED:
                return False

        self.matched()
        if self.memory_type > 1:
            logger.debug(f'matched_memory {self.simple_str()}')
        return True

    @util.timeit
    def matched(self):
        self.status = constants.MATCHED
        # extend active end time when it's matched, keeping it in active memories for composing
        self.active_end_time = time.time() + MEMORY_DURATIONS[self.memory_type]
        self.recall()

    @util.timeit
    def recall(self):
        self.refresh_self(True, False)

    # disable for performance issue @util.timeit
    def equal(self, query):
        equal_fields = ['memory_type', 'feature_type', 'channel', 'kernel', 'feature', 'click_type', 'degrees', 'speed',
                        'duration', 'zoom_type', 'zoom_direction']
        for field in equal_fields:
            if getattr(query, field) is not None:
                if getattr(query, field) != getattr(self, field):
                    return False
        if len(query.children) > 0:
            if self.memory_type <= 1:
                return util.list_equal_no_order(self.children, query.children)
            else:
                return util.list_equal_order(self.children, query.children)
        return True

    @util.timeit
    def deactivate(self):
        self.status = constants.DORMANT
        self.active_end_time = 0

    @util.timeit
    def set_memory_type(self, memory_type_str):
        self.memory_type = get_memory_type(memory_type_str)

    @util.timeit
    def set_feature_type(self, feature_type_str):
        self.feature_type = get_feature_type(feature_type_str)

    @util.timeit
    def refresh_relative(self):
        self.children = [x for x in self.children if x.live is True]
        self.parent = {x for x in self.parent if x.live is True}
        if self.memory_type > 0 and len(self.children) == 0:
            self.kill()

    @util.timeit
    def create_index_common(self, indexes: dict):
        raw = f'{self.memory_type}|{self.feature_type}|{self.click_type}|{self.degrees}|{self.speed}|{self.duration}|' \
              f'{self.zoom_type}|{self.zoom_direction}|'
        if len(self.children) > 0:
            mids = [x.mid for x in self.children]
            if self.memory_type <= 2:
                # without order
                raw += f'{sorted(mids)}'
            else:
                raw += f'{mids}'
        index = hashlib.md5(raw.encode('utf-8')).hexdigest()
        if indexes is not None:
            indexes.update({index: self})
        return index

    @util.timeit
    def create_index_kernel(self, indexes: dict):
        raw = f'{self.memory_type}|{self.feature_type}|{self.channel}|{self.kernel}'
        index = hashlib.md5(raw.encode('utf-8')).hexdigest()
        if indexes is not None:
            index_objects = indexes.get(index)
            if index_objects:
                index_objects.append(self)
                indexes.update({index: index_objects})
            else:
                indexes.update({index: [self]})
        return index

    @util.timeit
    def get_index(self):
        return self.create_index(None)

    @util.timeit
    def create_index(self, indexes):
        if self.memory_type == MEMORY_TYPES.index(constants.FEATURE_MEMORY) and self.feature_type < 2:
            return self.create_index_kernel(indexes)
        else:
            return self.create_index_common(indexes)

    def kill(self):
        self.deactivate()
        self.live = False

    def simple_str(self):
        parent = {x.mid for x in self.parent}
        children = [x.mid for x in self.children]
        return f'[id:{self.mid},type:{self.memory_type},feature:{self.feature_type},recall:{self.recall_count},' \
               f'reward:{self.reward},live:{self.live},status:{self.status},parent:{parent},children:{children}]'

    # @util.timeit
    def render_tree(self, temp_set, level=0, max_level=30):
        if level >= max_level:
            # print('hit max level, return')
            return
        level_line = ''
        for i in range(0, level):
            level_line = '---{0}'.format(level_line)
        if not self.live:
            print('dead')
        else:
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
