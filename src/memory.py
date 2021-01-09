import hashlib
import time
import uuid

from src import util


class Memory:

    def __init__(self, memory_type, memory_data, real_type=None):
        self.MID = self.create_id()
        self.MEMORY_TYPE = memory_type
        self.REAL_TYPE = real_type
        self.CREATED_TIME = time.time()
        self.activated_time = time.time()
        self.strengthen_time = time.time()
        self.stability = 0
        self.context = set()
        self.context_indexes = set()  # ID of memories use this memory as index
        self.context_weight = 0  # weight when this memory is a context
        # data of context should be [source_memory_id, target_memory_id]
        self.data = util.create_data(memory_type, memory_data)
        self.data_indexes = set()  # ID of memories use this memory as data
        self.action = None

    def __hash__(self):
        return self.MID

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return other == self.MID

    @staticmethod
    def create_id():
        return int(hashlib.md5(str(uuid.uuid4()).encode('utf-8')).hexdigest(), 16)
