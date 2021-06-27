import time

from src import constants
from src.memory import Memory


class MemoryList:

    def __init__(self):
        self.data = []
        self.temporal_duration = constants.temporal_duration
        self.context_duration = constants.context_duration
        self.total_duration = self.temporal_duration + self.context_duration
        self.processing = []
        self.processed = []
        self.temporal = []
        self.context = []
        self.expired = []

    def __len__(self):
        return len(self.data)

    def __getitem__(self, x):
        return self.data[x]

    def append(self, m: Memory):
        m.activated_time = time.time()
        self.data.append(m)

    def prepare(self):
        new_processing = []
        new_processed = []
        new_expired = []
        new_temporal = []
        new_context = []
        now_time = time.time()
        for m in self.data:
            elapsed = now_time - m.created_time
            if elapsed > self.total_duration:
                new_expired.append(m)
            elif elapsed > self.temporal_duration:
                new_processed.append(m)
                if m.stability >= constants.stable:
                    # only stable memory will be used, to reduce calculation
                    new_context.append(m)
            else:
                new_processing.append(m)
                if m.stability >= constants.stable:
                    # only stable memory will be used
                    new_temporal.append(m)
        self.processed = new_processed
        self.processing = new_processing
        self.expired = new_expired
        self.temporal = new_temporal
        self.context = new_context

    def rebuild(self, new_processing):
        self.data = self.processed + new_processing
