from . import constants
from components import util
import copy
import logging
import numpy as np
import random
import time

logger = logging.getLogger('Memory')
logger.setLevel(logging.INFO)
MEMORY_DURATIONS = [0.15, 0.15, 0.5, 3, 360]
MEMORY_TYPES = [constants.FEATURE_MEMORY, constants.SLICE_MEMORY, constants.INSTANT_MEMORY, constants.SHORT_MEMORY,
                constants.LONG_MEMORY]
MEMORY_FEATURES = [constants.SOUND_FEATURE, constants.VISION_FEATURE, constants.VISION_FOCUS_MOVE,
                   constants.VISION_FOCUS_ZOOM, constants.ACTION_MOUSE_CLICK, constants.ACTION_REWARD]
COMPOSE_NUMBER = 4
GREEDY_RATIO = 0.8
NOT_FORGET_STEP = 10
BASE_DESIRE = 0.1
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
    for m in list(memories):
        nm = copy.copy(m)
        nm.parent = set([x.mid for x in m.parent])
        nm.children = [x.mid for x in m.children]
        new_memories.add(nm)
    return new_memories


def construct(memories):
    new_memories = set()
    md = dict((x.mid, x) for x in memories)
    for m in memories:
        nm = copy.copy(m)
        new_parent = set()
        for x in m.parent:
            npr = md.get(x)
            if npr:
                new_parent.add(npr)
        nm.parent = new_parent
        new_children = []
        for x in m.children:
            ncr = md.get(x)
            if ncr:
                new_children.append(ncr)
        nm.children = new_children
        new_memories.add(nm)
    return new_memories


class Memory:
    mid = 0
    live = True
    memory_type = None
    feature_type = None
    recall_count = 1
    last_recall_time = 0
    protect_time = 0
    reward = 0
    parent = None
    children = None

    # for active period
    status = None
    matched_time = None
    active_start_time = None
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
        self.status = constants.MATCHED
        self.matched_time = time.time()
        self.active_start_time = time.time()
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
    def refresh(self, recall=False, is_forget=False):
        if not self.validate():
            self.live = False
            return
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
                            self.live = False
                            break
                    # if this is recall, will update recall count and last recall time
                    if recall:
                        self.recall_count += 1
                        self.last_recall_time = time.time()
                break

    @util.timeit
    def get_desire(self):
        elapse = time.time() - self.matched_time
        # linear func, weight is 0 at beginning, it's 1 after 4000 seconds
        f = 0.00025 * elapse
        desire = BASE_DESIRE + self.reward * f
        desire = desire if desire < 1 else 1
        return desire

    @util.timeit
    def activate(self):
        if not self.live:
            return
        if self.status != constants.DORMANT:
            return

        self.status = constants.MATCHING
        self.active_start_time = time.time()
        self.active_end_time = time.time() + MEMORY_DURATIONS[self.memory_type]

    @util.timeit
    def activate_tree(self):
        self.activate()
        for m in self.children:
            if m.memory_type in [MEMORY_TYPES.index(constants.LONG_MEMORY),
                                 MEMORY_TYPES.index(constants.SHORT_MEMORY),
                                 MEMORY_TYPES.index(constants.INSTANT_MEMORY),
                                 MEMORY_TYPES.index(constants.SLICE_MEMORY)]:
                if m.status in [constants.MATCHING, constants.DORMANT]:
                    m.activate_tree()
                    break
            else:
                m.activate_tree()

    @util.timeit
    def match(self):
        if self.status != constants.MATCHING:
            return False

        for m in self.children:
            if m.status != constants.MATCHED:
                return False

        self.matched()
        return True

    @util.timeit
    def matched(self):
        self.status = constants.MATCHED
        # extend active end time when it's matched
        self.active_end_time = time.time() + MEMORY_DURATIONS[self.memory_type]
        self.recall()

    @util.timeit
    def recall(self):
        self.refresh(True, False)

    # @util.timeit
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

    def deactivate(self):
        self.status = constants.DORMANT

    def set_memory_type(self, memory_type_str):
        self.memory_type = get_memory_type(memory_type_str)

    def set_feature_type(self, feature_type_str):
        self.feature_type = get_feature_type(feature_type_str)

    def validate(self):
        live = True
        if self.memory_type > 0:
            if len(self.children) == 0:
                live = False
            elif len(self.children) == 1:
                child = self.children[0]
                if not child.live:
                    live = False
                else:
                    if len(child.children) == 1:
                        self.children = child.children
                        child.children = []
            else:
                has_child = False
                for m in self.children:
                    if m.live:
                        has_child = True
                        break
                if not has_child:
                    live = False
        return live
