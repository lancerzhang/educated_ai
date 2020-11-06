import logging
import time

logger = logging.getLogger('Memory')
logger.setLevel(logging.INFO)


class MemoryType:
    REAL = 0  # one real memory
    SET = 1  # collection of one type of real memories happened at the same time
    CONTEXT = 2  # indicate if a memory is context of another
    INSTANT = 3  # collection of slice memories happened in an instant, it's phone in voice
    SHORT = 4  # memories happened in a short time, it's word in voice
    LONG = 5  # memories happened in a long time, it's sentence in voice
    LONG2 = 6  # memories happened in a longer time, it's sentence in voice


class MemoryStatus:
    # dormant memories will be clean up in high priority
    # dormant memories can't be activated
    # dormant memories can be retrieved if it's yet clean up, recall count will be kept
    DORMANT = 0
    SLEEP = 1
    LIVING = 2
    MATCHED = 3
    MATCHING = 4


MEMORY_DURATIONS = [0, 0.15, 0.5, 5, 10, 20]  # mfcc, phone, char, word, sentence, concat sentence
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


class Memory:

    def __init__(self, memory_type, memory_data, real_type=None):
        self.MID = int(time.time() * 1000 * 1000)
        self.MEMORY_TYPE = memory_type
        self.REAL_TYPE = real_type
        self.created_time = time.time()
        self.status = MemoryStatus.MATCHED
        self.matched_time = time.time()
        self.recall_count = 0
        self.last_recall_time = time.time()
        self.context = {}
        self.context_indexes = set()  # memories use this memory as context
        self.context_weight = 0  # weight when this memory is a context
        # data of context should be [source_memory_id, target_memory_id]
        self.data = memory_data
        self.data_indexes = set()  # memories use this memory as data
        self.data_weight = 0  # weight when this memory is a data
        self.data_order = 'o'  # ordered
        if memory_type <= MemoryType.SET:
            self.data_order = 'u'  # unordered
