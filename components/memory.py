import time

from components import constants


class Memory:

    def __init__(self, memory_type, memory_data, real_type=None):
        self.MID = int(time.time() * 1000 * 1000)
        self.MEMORY_TYPE = memory_type
        self.REAL_TYPE = real_type
        self.created_time = time.time()
        self.activated_time = time.time()
        self.stability = 0
        self.context = {}
        self.context_indexes = set()  # memories use this memory as context
        self.context_weight = 0  # weight when this memory is a context
        # data of context should be [source_memory_id, target_memory_id]
        self.data = memory_data
        self.data_indexes = set()  # memories use this memory as data
        self.data_weight = 0  # weight when this memory is a data
        self.data_order = 'o'  # ordered
        if constants.memory_types.index(memory_type) <= constants.memory_types.index(constants.pack):
            self.data_order = 'u'  # unordered
