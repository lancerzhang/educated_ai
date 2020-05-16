import time
import unittest

from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from components import constants
from components.bio_memory import BioMemory
from components.data_adaptor import DataAdaptor
from components.data_tinydb import DataTinyDB


class TestBioMemory(unittest.TestCase):
    data_adaptor = None

    def setUp(self):
        database = DataTinyDB(TinyDB(storage=MemoryStorage))
        da = DataAdaptor(database)
        bm = BioMemory(da)
        bm.forget_memory = False
        self.bio_memory = bm
        self.data_adaptor = da

    def test_split_seq_time_memories_empty(self):
        memories = []
        result = self.bio_memory.split_seq_time_memories(memories)
        self.assertEqual(0, len(result[self.bio_memory.NEW_MEMORIES]))
        self.assertEqual(0, len(result[self.bio_memory.REST_OF_MEMORIES]))

    def test_split_seq_time_memories_number_no_split(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        memories = [mem]
        result = self.bio_memory.split_seq_time_memories(memories)
        self.assertEqual(0, len(result[self.bio_memory.NEW_MEMORIES]))
        self.assertEqual(1, len(result[self.bio_memory.REST_OF_MEMORIES]))

    def test_split_seq_time_memories_number_split_1_1(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        memories = []
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + 1):
            memories.append(mem)
        result = self.bio_memory.split_seq_time_memories(memories)
        self.assertEqual(1, len(result[self.bio_memory.NEW_MEMORIES]))
        self.assertEqual(1, len(result[self.bio_memory.REST_OF_MEMORIES]))

    def test_split_seq_time_memories_number_split_1_0(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        memories = []
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + 0):
            memories.append(mem)
        result = self.bio_memory.split_seq_time_memories(memories)
        self.assertEqual(1, len(result[self.bio_memory.NEW_MEMORIES]))
        self.assertEqual(0, len(result[self.bio_memory.REST_OF_MEMORIES]))

    def test_split_seq_time_memories_number_split_1_2(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        memories = []
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + 2):
            memories.append(mem)
        result = self.bio_memory.split_seq_time_memories(memories)
        self.assertEqual(1, len(result[self.bio_memory.NEW_MEMORIES]))
        self.assertEqual(2, len(result[self.bio_memory.REST_OF_MEMORIES]))

    def test_split_seq_time_memories_number_split_2(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        memories = []
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + self.bio_memory.COMPOSE_NUMBER + 1):
            memories.append(mem)
        result = self.bio_memory.split_seq_time_memories(memories)
        self.assertEqual(2, len(result[self.bio_memory.NEW_MEMORIES]))
        self.assertEqual(1, len(result[self.bio_memory.REST_OF_MEMORIES]))

    def test_split_seq_time_memories_time_no_split(self):
        now = time.time()
        memories = []
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER - 1):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 1})
            memories.append(mem)
            now = now + 1
        result = self.bio_memory.split_seq_time_memories(memories, 6)
        self.assertEqual(0, len(result[self.bio_memory.NEW_MEMORIES]))
        self.assertEqual(self.bio_memory.COMPOSE_NUMBER - 1, len(result[self.bio_memory.REST_OF_MEMORIES]))

    def test_split_seq_time_memories_time_split_1_1(self):
        now = time.time()
        memories = []
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER - 1):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 3})
            memories.append(mem)
            now = now + 3
        result = self.bio_memory.split_seq_time_memories(memories, 5)
        self.assertEqual(1, len(result[self.bio_memory.NEW_MEMORIES]))
        self.assertEqual(1, len(result[self.bio_memory.REST_OF_MEMORIES]))
        self.assertEqual(1, len(result[self.bio_memory.CHILD_DAT1]))
        self.assertEqual(3, result[self.bio_memory.CHILD_DAT1][0][1])

    def test_split_seq_time_memories_time_split_0(self):
        now = time.time()
        memories = []
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER - 1):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 2})
            memories.append(mem)
            now = now + 2
        result = self.bio_memory.split_seq_time_memories(memories, 5)
        self.assertEqual(0, len(result[self.bio_memory.NEW_MEMORIES]))
        self.assertEqual(3, len(result[self.bio_memory.REST_OF_MEMORIES]))

    def test_split_seq_time_memories_time_split_1_2(self):
        now = time.time()
        memories = []
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 3})
            memories.append(mem)
            now = now + 3
        result = self.bio_memory.split_seq_time_memories(memories, 5)
        self.assertEqual(1, len(result[self.bio_memory.NEW_MEMORIES]))
        self.assertEqual(2, len(result[self.bio_memory.REST_OF_MEMORIES]))
        self.assertEqual(1, len(result[self.bio_memory.CHILD_DAT1]))
        self.assertEqual(3, result[self.bio_memory.CHILD_DAT1][0][1])

    def test_split_seq_time_memories_time_split_2(self):
        now = time.time()
        memories = []
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + 3):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 2})
            memories.append(mem)
            now = now + 2
        result = self.bio_memory.split_seq_time_memories(memories, 5)
        self.assertEqual(2, len(result[self.bio_memory.NEW_MEMORIES]))
        self.assertEqual(1, len(result[self.bio_memory.REST_OF_MEMORIES]))
        self.assertEqual(2, len(result[self.bio_memory.CHILD_DAT1]))
        self.assertEqual(3, len(result[self.bio_memory.CHILD_DAT1][0]))
        self.assertEqual(3, len(result[self.bio_memory.CHILD_DAT1][1]))
        self.assertEqual(2, result[self.bio_memory.CHILD_DAT1][0][1])
        self.assertEqual(2, result[self.bio_memory.CHILD_DAT1][0][2])
        self.assertEqual(2, result[self.bio_memory.CHILD_DAT1][1][1])
        self.assertEqual(2, result[self.bio_memory.CHILD_DAT1][1][2])

    def test_split_seq_time_memories_mix(self):
        now = time.time()
        memories = []
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + 1):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 1})
            memories.append(mem)
            now = now + 1
        result = self.bio_memory.split_seq_time_memories(memories, 10)
        self.assertEqual(1, len(result[self.bio_memory.NEW_MEMORIES]))
        self.assertEqual(1, len(result[self.bio_memory.REST_OF_MEMORIES]))

    def test_compose_slice_number_no_split(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        self.bio_memory.temp_memories[constants.SLICE_MEMORY].append(mem)
        self.bio_memory.compose()
        self.assertEqual(1, len(self.bio_memory.temp_memories[constants.SLICE_MEMORY]))

    def test_compose_slice_number_split_1_1(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + 1):
            self.bio_memory.temp_memories[constants.SLICE_MEMORY].append(mem)
        self.bio_memory.compose()
        self.assertEqual(1, len(self.bio_memory.temp_memories[constants.SLICE_MEMORY]))

    def test_compose_slice_number_split_1_0(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + 0):
            self.bio_memory.temp_memories[constants.SLICE_MEMORY].append(mem)
        self.bio_memory.compose()
        self.assertEqual(0, len(self.bio_memory.temp_memories[constants.SLICE_MEMORY]))

    def test_compose_slice_number_split_1_2(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + 2):
            self.bio_memory.temp_memories[constants.SLICE_MEMORY].append(mem)
        self.bio_memory.compose()
        self.assertEqual(2, len(self.bio_memory.temp_memories[constants.SLICE_MEMORY]))

    def test_compose_slice_number_split_2(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + self.bio_memory.COMPOSE_NUMBER + 1):
            self.bio_memory.temp_memories[constants.SLICE_MEMORY].append(mem)
        self.bio_memory.compose()
        self.assertEqual(1, len(self.bio_memory.temp_memories[constants.SLICE_MEMORY]))

    def test_compose_slice_time_no_split(self):
        now = time.time()
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER - 1):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 0.1})
            self.bio_memory.temp_memories[constants.SLICE_MEMORY].append(mem)
            now = now + 0.1
        self.bio_memory.compose()
        self.assertEqual(self.bio_memory.COMPOSE_NUMBER - 1, len(self.bio_memory.temp_memories[constants.SLICE_MEMORY]))

    def test_compose_slice_time_split_1_1(self):
        now = time.time()
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER - 1):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 0.3})
            self.bio_memory.temp_memories[constants.SLICE_MEMORY].append(mem)
            now = now + 0.3
        self.bio_memory.compose()
        self.assertEqual(1, len(self.bio_memory.temp_memories[constants.SLICE_MEMORY]))

    def test_compose_slice_time_split_1_0(self):
        now = time.time()
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER - 1):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 0.2})
            self.bio_memory.temp_memories[constants.SLICE_MEMORY].append(mem)
            now = now + 0.2
        self.bio_memory.compose()
        self.assertEqual(self.bio_memory.COMPOSE_NUMBER - 1, len(self.bio_memory.temp_memories[constants.SLICE_MEMORY]))

    def test_compose_slice_time_split_1_2(self):
        now = time.time()
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 0.3})
            self.bio_memory.temp_memories[constants.SLICE_MEMORY].append(mem)
            now = now + 0.3
        self.bio_memory.compose()
        self.assertEqual(2, len(self.bio_memory.temp_memories[constants.SLICE_MEMORY]))

    def test_compose_slice_time_split_2(self):
        now = time.time()
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + 3):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 0.2})
            self.bio_memory.temp_memories[constants.SLICE_MEMORY].append(mem)
            now = now + 0.2
        self.bio_memory.compose()
        self.assertEqual(1, len(self.bio_memory.temp_memories[constants.SLICE_MEMORY]))

    def test_compose_instant_number_no_split(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        self.bio_memory.temp_memories[constants.INSTANT_MEMORY].append(mem)
        self.bio_memory.compose()
        self.assertEqual(1, len(self.bio_memory.temp_memories[constants.INSTANT_MEMORY]))

    def test_compose_instant_number_split_1_1(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + 1):
            self.bio_memory.temp_memories[constants.INSTANT_MEMORY].append(mem)
        self.bio_memory.compose()
        self.assertEqual(1, len(self.bio_memory.temp_memories[constants.INSTANT_MEMORY]))

    def test_compose_instant_number_split_1_0(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + 0):
            self.bio_memory.temp_memories[constants.INSTANT_MEMORY].append(mem)
        self.bio_memory.compose()
        self.assertEqual(0, len(self.bio_memory.temp_memories[constants.INSTANT_MEMORY]))

    def test_compose_instant_number_split_1_2(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + 2):
            self.bio_memory.temp_memories[constants.INSTANT_MEMORY].append(mem)
        self.bio_memory.compose()
        self.assertEqual(2, len(self.bio_memory.temp_memories[constants.INSTANT_MEMORY]))

    def test_compose_instant_number_split_2(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + self.bio_memory.COMPOSE_NUMBER + 1):
            self.bio_memory.temp_memories[constants.INSTANT_MEMORY].append(mem)
        self.bio_memory.compose()
        self.assertEqual(1, len(self.bio_memory.temp_memories[constants.INSTANT_MEMORY]))

    def test_compose_instant_time_no_split(self):
        now = time.time()
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER - 1):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 1})
            self.bio_memory.temp_memories[constants.INSTANT_MEMORY].append(mem)
            now = now + 1
        self.bio_memory.compose()
        self.assertEqual(self.bio_memory.COMPOSE_NUMBER - 1,
                         len(self.bio_memory.temp_memories[constants.INSTANT_MEMORY]))

    def test_compose_instant_time_split_1_1(self):
        now = time.time()
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER - 1):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 3})
            self.bio_memory.temp_memories[constants.INSTANT_MEMORY].append(mem)
            now = now + 3
        self.bio_memory.compose()
        self.assertEqual(1, len(self.bio_memory.temp_memories[constants.INSTANT_MEMORY]))

    def test_compose_instant_time_split_1_0(self):
        now = time.time()
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER - 1):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 1})
            self.bio_memory.temp_memories[constants.INSTANT_MEMORY].append(mem)
            now = now + 1
        self.bio_memory.compose()
        self.assertEqual(self.bio_memory.COMPOSE_NUMBER - 1,
                         len(self.bio_memory.temp_memories[constants.INSTANT_MEMORY]))

    def test_compose_instant_time_split_1_2(self):
        now = time.time()
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 2})
            self.bio_memory.temp_memories[constants.INSTANT_MEMORY].append(mem)
            now = now + 2
        self.bio_memory.compose()
        self.assertEqual(2, len(self.bio_memory.temp_memories[constants.INSTANT_MEMORY]))

    def test_compose_instant_time_split_2(self):
        now = time.time()
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + 3):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 2})
            self.bio_memory.temp_memories[constants.INSTANT_MEMORY].append(mem)
            now = now + 2
        self.bio_memory.compose()
        self.assertEqual(1, len(self.bio_memory.temp_memories[constants.INSTANT_MEMORY]))

    def test_compose_short_number_no_split(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        self.bio_memory.temp_memories[constants.SHORT_MEMORY].append(mem)
        self.bio_memory.compose()
        self.assertEqual(1, len(self.bio_memory.temp_memories[constants.SHORT_MEMORY]))

    def test_compose_short_number_split_1_1(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + 1):
            self.bio_memory.temp_memories[constants.SHORT_MEMORY].append(mem)
        self.bio_memory.compose()
        self.assertEqual(1, len(self.bio_memory.temp_memories[constants.SHORT_MEMORY]))

    def test_compose_short_number_split_1_0(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + 0):
            self.bio_memory.temp_memories[constants.SHORT_MEMORY].append(mem)
        self.bio_memory.compose()
        self.assertEqual(0, len(self.bio_memory.temp_memories[constants.SHORT_MEMORY]))

    def test_compose_short_number_split_1_2(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + 2):
            self.bio_memory.temp_memories[constants.SHORT_MEMORY].append(mem)
        self.bio_memory.compose()
        self.assertEqual(2, len(self.bio_memory.temp_memories[constants.SHORT_MEMORY]))

    def test_compose_short_number_split_2(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + self.bio_memory.COMPOSE_NUMBER + 1):
            self.bio_memory.temp_memories[constants.SHORT_MEMORY].append(mem)
        self.bio_memory.compose()
        self.assertEqual(1, len(self.bio_memory.temp_memories[constants.SHORT_MEMORY]))

    def test_compose_short_time_no_split(self):
        now = time.time()
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER - 1):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 1})
            self.bio_memory.temp_memories[constants.SHORT_MEMORY].append(mem)
            now = now + 1
        self.bio_memory.compose()
        self.assertEqual(self.bio_memory.COMPOSE_NUMBER - 1, len(self.bio_memory.temp_memories[constants.SHORT_MEMORY]))

    def test_compose_short_time_split_1_1(self):
        now = time.time()
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER - 1):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 3})
            self.bio_memory.temp_memories[constants.SHORT_MEMORY].append(mem)
            now = now + 3
        self.bio_memory.compose()
        self.assertEqual(self.bio_memory.COMPOSE_NUMBER - 1, len(self.bio_memory.temp_memories[constants.SHORT_MEMORY]))

    def test_compose_short_time_split_1_0(self):
        now = time.time()
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER - 1):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 2})
            self.bio_memory.temp_memories[constants.SHORT_MEMORY].append(mem)
            now = now + 2
        self.bio_memory.compose()
        self.assertEqual(self.bio_memory.COMPOSE_NUMBER - 1, len(self.bio_memory.temp_memories[constants.SHORT_MEMORY]))

    def test_compose_short_time_split_1_2(self):
        now = time.time()
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 3})
            self.bio_memory.temp_memories[constants.SHORT_MEMORY].append(mem)
            now = now + 3
        self.bio_memory.compose()
        self.assertEqual(0, len(self.bio_memory.temp_memories[constants.SHORT_MEMORY]))

    def test_compose_short_time_split_2(self):
        now = time.time()
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + 3):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 2})
            self.bio_memory.temp_memories[constants.SHORT_MEMORY].append(mem)
            now = now + 2
        self.bio_memory.compose()
        self.assertEqual(3, len(self.bio_memory.temp_memories[constants.SHORT_MEMORY]))

    def test_compose_long_number_no_split(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        self.bio_memory.temp_memories[constants.LONG_MEMORY].append(mem)
        self.bio_memory.compose()
        self.assertEqual(1, len(self.bio_memory.temp_memories[constants.LONG_MEMORY]))

    def test_compose_long_number_split_1_1(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + 1):
            self.bio_memory.temp_memories[constants.LONG_MEMORY].append(mem)
        self.bio_memory.compose()
        self.assertEqual(1 + 1, len(self.bio_memory.temp_memories[constants.LONG_MEMORY]))

    def test_compose_long_number_split_1_0(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + 0):
            self.bio_memory.temp_memories[constants.LONG_MEMORY].append(mem)
        self.bio_memory.compose()
        self.assertEqual(1, len(self.bio_memory.temp_memories[constants.LONG_MEMORY]))

    def test_compose_long_number_split_1_2(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + 2):
            self.bio_memory.temp_memories[constants.LONG_MEMORY].append(mem)
        self.bio_memory.compose()
        self.assertEqual(1 + 2, len(self.bio_memory.temp_memories[constants.LONG_MEMORY]))

    def test_compose_long_number_split_2(self):
        mem = self.bio_memory.BASIC_MEMORY.copy()
        mem.update({constants.MID: 1000, constants.HAPPEN_TIME: time.time()})
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + self.bio_memory.COMPOSE_NUMBER + 1):
            self.bio_memory.temp_memories[constants.LONG_MEMORY].append(mem)
        self.bio_memory.compose()
        self.assertEqual(1 + 2, len(self.bio_memory.temp_memories[constants.LONG_MEMORY]))

    def test_compose_long_time_no_split(self):
        now = time.time()
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER - 1):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 1})
            self.bio_memory.temp_memories[constants.LONG_MEMORY].append(mem)
            now = now + 1
        self.bio_memory.compose()
        self.assertEqual(self.bio_memory.COMPOSE_NUMBER - 1, len(self.bio_memory.temp_memories[constants.LONG_MEMORY]))

    def test_compose_long_time_split_1_1(self):
        now = time.time()
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER - 1):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 3})
            self.bio_memory.temp_memories[constants.LONG_MEMORY].append(mem)
            now = now + 3
        self.bio_memory.compose()
        self.assertEqual(self.bio_memory.COMPOSE_NUMBER - 1, len(self.bio_memory.temp_memories[constants.LONG_MEMORY]))

    def test_compose_long_time_split_1_0(self):
        now = time.time()
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER - 1):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 2})
            self.bio_memory.temp_memories[constants.LONG_MEMORY].append(mem)
            now = now + 2
        self.bio_memory.compose()
        self.assertEqual(self.bio_memory.COMPOSE_NUMBER - 1, len(self.bio_memory.temp_memories[constants.LONG_MEMORY]))

    def test_compose_long_time_split_1_2(self):
        now = time.time()
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 3})
            self.bio_memory.temp_memories[constants.LONG_MEMORY].append(mem)
            now = now + 3
        self.bio_memory.compose()
        self.assertEqual(1, len(self.bio_memory.temp_memories[constants.LONG_MEMORY]))

    def test_compose_long_time_split_2(self):
        now = time.time()
        for num in range(1, 1 + self.bio_memory.COMPOSE_NUMBER + 3):
            mem = self.bio_memory.BASIC_MEMORY.copy()
            mem.update({constants.MID: 1000, constants.HAPPEN_TIME: now + 2})
            self.bio_memory.temp_memories[constants.LONG_MEMORY].append(mem)
            now = now + 2
        self.bio_memory.compose()
        self.assertEqual(3 + 1, len(self.bio_memory.temp_memories[constants.LONG_MEMORY]))


if __name__ == "__main__":
    unittest.main()
