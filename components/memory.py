from . import constants
from components import util
import logging
import numpy as np
import random
import time

logger = logging.getLogger('Memory')
logger.setLevel(logging.INFO)
MEMORY_DURATIONS = [0.15, 0.15, 0.5, 3, 360]
MEMORY_TYPES = [constants.FEATURE_MEMORY, constants.SLICE_MEMORY, constants.INSTANT_MEMORY, constants.SHORT_MEMORY,
                constants.LONG_MEMORY]
MEMORY_FEATURES = ['vision', 'sound', 'focus_move', 'focus_zoom', 'mouse', 'reward']
COMPOSE_NUMBER = 4
GREEDY_RATIO = 0.8
NOT_FORGET_STEP = 10

TIME_SEC = [5, 6, 8, 11, 15, 20, 26, 33, 41, 50, 60, 71, 83, 96, 110, 125, 141, 158, 176, 196, 218, 242, 268, 296,
            326, 358, 392, 428, 466, 506, 548, 593, 641, 692, 746, 803, 863, 926, 992, 1061, 1133, 1208, 1286, 1367,
            1451, 1538, 1628, 1721, 1920, 2100, 2280, 2460, 2640, 2880, 3120, 3360, 3600, 4680, 6120, 7920, 10440,
            14040, 18720, 24840, 32400, 41760, 52920, 66240, 81720, 99720, 120240, 143640, 169920, 222480, 327600,
            537840, 853200, 1326240, 2035800, 3100140, 3609835, 4203316, 4894372, 5699043, 6636009, 7727020,
            8997403, 10476649, 12199095, 14204727, 16540102, 19259434, 22425848, 26112847, 30406022, 35405033,
            41225925, 48003823, 55896067, 65085866]


class Memory:
    live = True
    memory_type = -1
    feature_type = -1
    recall_count = 1
    last_recall_time = 0
    protect_time = 0
    reward = 0
    parent = set()
    children = []

    # for active period
    status = None
    matched_time = None
    active_start_time = None
    active_end_time = None

    def __init__(self, mid):
        self.mid = mid
        self.status = constants.MATCHED
        self.matched_time = time.time()
        self.active_start_time = time.time()
        self.recall_count = 1
        self.last_recall_time = time.time()

    def __hash__(self):
        return int(self.mid)

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

    # longer time elapsed, easier to forget
    # more times recall, harder to forget
    # can not recall frequently in short time
    @util.timeit
    def refresh(self, recall=False, is_forget=False):
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
    def activate(self):
        if self.status != constants.DORMANT:
            return

        self.status = constants.MATCHING
        self.active_start_time = time.time()
        self.active_end_time = time.time() + MEMORY_DURATIONS[self.memory_type]

    @util.timeit
    def activate_tree(self):
        self.activate()
        for memory in self.children:
            if memory.virtual_type in [constants.LONG_MEMORY, constants.SHORT_MEMORY, constants.INSTANT_MEMORY]:
                if memory.status == constants.MATCHING:
                    break
                elif memory.status == constants.DORMANT:
                    memory.activate_tree()
                    break
            else:
                memory.activate_tree()

    @util.timeit
    def match(self):
        if self.status != constants.MATCHING:
            return False

        for memory in self.children:
            if memory.status != constants.MATCHED:
                return False

        self.status = constants.MATCHED
        # extend active end time when it;s matched
        self.active_end_time = time.time() + MEMORY_DURATIONS[self.memory_type]
        self.recall()
        return True

    @util.timeit
    def recall(self):
        return

    @util.timeit
    def equals(self, memory):
        if memory.children:
            if self.children != memory.children:
                return False
        return True

    def deactivate(self):
        self.status = constants.DORMANT
