import unittest, memory, sound, time, copy
from db import Database
from tinydb import TinyDB
from tinydb.storages import MemoryStorage


class TestMemory(unittest.TestCase):
    database = None

    def setUp(self):
        self.database = Database(TinyDB(storage=MemoryStorage))
        memory.forget_memory = False
        memory.db = self.database

    def test_split_working_memories_empty(self):
        memories = []
        result = memory.split_working_memories(memories)
        self.assertEqual(0, len(result[memory.NEW_MEMORIES]))
        self.assertEqual(0, len(result[memory.REST_OF_MEMORIES]))

    def test_split_working_memories_number_no_split(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        memories = [mem]
        result = memory.split_working_memories(memories)
        self.assertEqual(0, len(result[memory.NEW_MEMORIES]))
        self.assertEqual(1, len(result[memory.REST_OF_MEMORIES]))

    def test_split_working_memories_number_split_1_1(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        memories = []
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 1):
            memories.append(mem)
        result = memory.split_working_memories(memories)
        self.assertEqual(1, len(result[memory.NEW_MEMORIES]))
        self.assertEqual(1, len(result[memory.REST_OF_MEMORIES]))

    def test_split_working_memories_number_split_1_0(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        memories = []
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 0):
            memories.append(mem)
        result = memory.split_working_memories(memories)
        self.assertEqual(1, len(result[memory.NEW_MEMORIES]))
        self.assertEqual(0, len(result[memory.REST_OF_MEMORIES]))

    def test_split_working_memories_number_split_1_2(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        memories = []
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 2):
            memories.append(mem)
        result = memory.split_working_memories(memories)
        self.assertEqual(1, len(result[memory.NEW_MEMORIES]))
        self.assertEqual(2, len(result[memory.REST_OF_MEMORIES]))

    def test_split_working_memories_number_split_2(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        memories = []
        for num in range(1, 1 + memory.COMPOSE_NUMBER + memory.COMPOSE_NUMBER + 1):
            memories.append(mem)
        result = memory.split_working_memories(memories)
        self.assertEqual(2, len(result[memory.NEW_MEMORIES]))
        self.assertEqual(1, len(result[memory.REST_OF_MEMORIES]))

    def test_split_working_memories_time_no_split(self):
        now = time.time()
        memories = []
        for num in range(1, 1 + memory.COMPOSE_NUMBER - 1):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 1})
            memories.append(mem)
            now = now + 1
        result = memory.split_working_memories(memories, 6)
        self.assertEqual(0, len(result[memory.NEW_MEMORIES]))
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(result[memory.REST_OF_MEMORIES]))

    def test_split_working_memories_time_split_1_1(self):
        now = time.time()
        memories = []
        for num in range(1, 1 + memory.COMPOSE_NUMBER - 1):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 3})
            memories.append(mem)
            now = now + 3
        result = memory.split_working_memories(memories, 5)
        self.assertEqual(1, len(result[memory.NEW_MEMORIES]))
        self.assertEqual(1, len(result[memory.REST_OF_MEMORIES]))
        self.assertEqual(1, len(result[memory.CHILD_DAT1]))
        self.assertEqual(3, result[memory.CHILD_DAT1][0][1])

    def test_split_working_memories_time_split_0(self):
        now = time.time()
        memories = []
        for num in range(1, 1 + memory.COMPOSE_NUMBER - 1):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 2})
            memories.append(mem)
            now = now + 2
        result = memory.split_working_memories(memories, 5)
        self.assertEqual(0, len(result[memory.NEW_MEMORIES]))
        self.assertEqual(3, len(result[memory.REST_OF_MEMORIES]))

    def test_split_working_memories_time_split_1_2(self):
        now = time.time()
        memories = []
        for num in range(1, 1 + memory.COMPOSE_NUMBER):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 3})
            memories.append(mem)
            now = now + 3
        result = memory.split_working_memories(memories, 5)
        self.assertEqual(1, len(result[memory.NEW_MEMORIES]))
        self.assertEqual(2, len(result[memory.REST_OF_MEMORIES]))
        self.assertEqual(1, len(result[memory.CHILD_DAT1]))
        self.assertEqual(3, result[memory.CHILD_DAT1][0][1])

    def test_split_working_memories_time_split_2(self):
        now = time.time()
        memories = []
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 3):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 2})
            memories.append(mem)
            now = now + 2
        result = memory.split_working_memories(memories, 5)
        self.assertEqual(2, len(result[memory.NEW_MEMORIES]))
        self.assertEqual(1, len(result[memory.REST_OF_MEMORIES]))
        self.assertEqual(2, len(result[memory.CHILD_DAT1]))
        self.assertEqual(3, len(result[memory.CHILD_DAT1][0]))
        self.assertEqual(3, len(result[memory.CHILD_DAT1][1]))
        self.assertEqual(2, result[memory.CHILD_DAT1][0][1])
        self.assertEqual(2, result[memory.CHILD_DAT1][0][2])
        self.assertEqual(2, result[memory.CHILD_DAT1][1][1])
        self.assertEqual(2, result[memory.CHILD_DAT1][1][2])

    def test_split_working_memories_mix(self):
        now = time.time()
        memories = []
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 1):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 1})
            memories.append(mem)
            now = now + 1
        result = memory.split_working_memories(memories, 10)
        self.assertEqual(1, len(result[memory.NEW_MEMORIES]))
        self.assertEqual(1, len(result[memory.REST_OF_MEMORIES]))

    def test_compose_slice_number_no_split(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        working_memories[memory.SLICE_MEMORY].update({mem[memory.ID]: mem})
        new_working_memories[memory.SLICE_MEMORY].append(mem)
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(1, len(working_memories[memory.SLICE_MEMORY]))
        self.assertEqual(1, len(new_working_memories[memory.SLICE_MEMORY]))
        self.assertEqual(0, len(working_memories[memory.INSTANT_MEMORY]))

    def test_compose_slice_number_split_1_1(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 1):
            working_memories[memory.SLICE_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.SLICE_MEMORY].append(mem)
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + 1, len(working_memories[memory.SLICE_MEMORY]))
        self.assertEqual(1, len(working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(1, len(new_working_memories[memory.SLICE_MEMORY]))

    def test_compose_slice_number_split_1_0(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 0):
            working_memories[memory.SLICE_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.SLICE_MEMORY].append(mem)
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + 0, len(working_memories[memory.SLICE_MEMORY]))
        self.assertEqual(1, len(working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(0, len(new_working_memories[memory.SLICE_MEMORY]))

    def test_compose_slice_number_split_1_2(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 2):
            working_memories[memory.SLICE_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.SLICE_MEMORY].append(mem)
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + 2, len(working_memories[memory.SLICE_MEMORY]))
        self.assertEqual(1, len(working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(2, len(new_working_memories[memory.SLICE_MEMORY]))

    def test_compose_slice_number_split_2(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + memory.COMPOSE_NUMBER + 1):
            working_memories[memory.SLICE_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.SLICE_MEMORY].append(mem)
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + memory.COMPOSE_NUMBER + 1, len(working_memories[memory.SLICE_MEMORY]))
        self.assertEqual(2, len(working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(1, len(new_working_memories[memory.SLICE_MEMORY]))

    def test_compose_slice_time_no_split(self):
        now = time.time()
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER - 1):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 0.1})
            working_memories[memory.SLICE_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.SLICE_MEMORY].append(mem)
            now = now + 0.1
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(working_memories[memory.SLICE_MEMORY]))
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(new_working_memories[memory.SLICE_MEMORY]))
        self.assertEqual(0, len(working_memories[memory.INSTANT_MEMORY]))

    def test_compose_slice_time_split_1_1(self):
        now = time.time()
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER - 1):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 0.3})
            working_memories[memory.SLICE_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.SLICE_MEMORY].append(mem)
            now = now + 0.3
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(working_memories[memory.SLICE_MEMORY]))
        self.assertEqual(1, len(working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(1, len(new_working_memories[memory.SLICE_MEMORY]))

    def test_compose_slice_time_split_1_0(self):
        now = time.time()
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER - 1):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 0.2})
            working_memories[memory.SLICE_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.SLICE_MEMORY].append(mem)
            now = now + 0.2
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(working_memories[memory.SLICE_MEMORY]))
        self.assertEqual(0, len(working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(new_working_memories[memory.SLICE_MEMORY]))

    def test_compose_slice_time_split_1_2(self):
        now = time.time()
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 0.3})
            working_memories[memory.SLICE_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.SLICE_MEMORY].append(mem)
            now = now + 0.3
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER, len(working_memories[memory.SLICE_MEMORY]))
        self.assertEqual(1, len(working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(2, len(new_working_memories[memory.SLICE_MEMORY]))

    def test_compose_slice_time_split_2(self):
        now = time.time()
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 3):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 0.2})
            working_memories[memory.SLICE_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.SLICE_MEMORY].append(mem)
            now = now + 0.2
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + 3, len(working_memories[memory.SLICE_MEMORY]))
        self.assertEqual(2, len(working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(1, len(new_working_memories[memory.SLICE_MEMORY]))

    def test_compose_instant_number_no_split(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        working_memories[memory.INSTANT_MEMORY].update({mem[memory.ID]: mem})
        new_working_memories[memory.INSTANT_MEMORY].append(mem)
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(1, len(working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(1, len(new_working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(0, len(working_memories[memory.SHORT_MEMORY]))

    def test_compose_instant_number_split_1_1(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 1):
            working_memories[memory.INSTANT_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.INSTANT_MEMORY].append(mem)
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + 1, len(working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(1, len(working_memories[memory.SHORT_MEMORY]))
        self.assertEqual(1, len(new_working_memories[memory.INSTANT_MEMORY]))

    def test_compose_instant_number_split_1_0(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 0):
            working_memories[memory.INSTANT_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.INSTANT_MEMORY].append(mem)
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + 0, len(working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(1, len(working_memories[memory.SHORT_MEMORY]))
        self.assertEqual(0, len(new_working_memories[memory.INSTANT_MEMORY]))

    def test_compose_instant_number_split_1_2(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 2):
            working_memories[memory.INSTANT_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.INSTANT_MEMORY].append(mem)
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + 2, len(working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(1, len(working_memories[memory.SHORT_MEMORY]))
        self.assertEqual(2, len(new_working_memories[memory.INSTANT_MEMORY]))

    def test_compose_instant_number_split_2(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + memory.COMPOSE_NUMBER + 1):
            working_memories[memory.INSTANT_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.INSTANT_MEMORY].append(mem)
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + memory.COMPOSE_NUMBER + 1, len(working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(2, len(working_memories[memory.SHORT_MEMORY]))
        self.assertEqual(1, len(new_working_memories[memory.INSTANT_MEMORY]))

    def test_compose_instant_time_no_split(self):
        now = time.time()
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER - 1):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 1})
            working_memories[memory.INSTANT_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.INSTANT_MEMORY].append(mem)
            now = now + 1
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(new_working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(0, len(working_memories[memory.SHORT_MEMORY]))

    def test_compose_instant_time_split_1_1(self):
        now = time.time()
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER - 1):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 3})
            working_memories[memory.INSTANT_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.INSTANT_MEMORY].append(mem)
            now = now + 3
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(1, len(working_memories[memory.SHORT_MEMORY]))
        self.assertEqual(1, len(new_working_memories[memory.INSTANT_MEMORY]))

    def test_compose_instant_time_split_1_0(self):
        now = time.time()
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER - 1):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 2})
            working_memories[memory.INSTANT_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.INSTANT_MEMORY].append(mem)
            now = now + 2
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(0, len(working_memories[memory.SHORT_MEMORY]))
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(new_working_memories[memory.INSTANT_MEMORY]))

    def test_compose_instant_time_split_1_2(self):
        now = time.time()
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 3})
            working_memories[memory.INSTANT_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.INSTANT_MEMORY].append(mem)
            now = now + 3
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER, len(working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(1, len(working_memories[memory.SHORT_MEMORY]))
        self.assertEqual(2, len(new_working_memories[memory.INSTANT_MEMORY]))

    def test_compose_instant_time_split_2(self):
        now = time.time()
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 3):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 2})
            working_memories[memory.INSTANT_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.INSTANT_MEMORY].append(mem)
            now = now + 2
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + 3, len(working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(2, len(working_memories[memory.SHORT_MEMORY]))
        self.assertEqual(1, len(new_working_memories[memory.INSTANT_MEMORY]))

    def test_compose_short_number_no_split(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        working_memories[memory.SHORT_MEMORY].update({mem[memory.ID]: mem})
        new_working_memories[memory.SHORT_MEMORY].append(mem)
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(1, len(working_memories[memory.SHORT_MEMORY]))
        self.assertEqual(1, len(new_working_memories[memory.SHORT_MEMORY]))
        self.assertEqual(0, len(working_memories[memory.LONG_MEMORY]))

    def test_compose_short_number_split_1_1(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 1):
            working_memories[memory.SHORT_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.SHORT_MEMORY].append(mem)
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + 1, len(working_memories[memory.SHORT_MEMORY]))
        self.assertEqual(1, len(working_memories[memory.LONG_MEMORY]))
        self.assertEqual(1, len(new_working_memories[memory.SHORT_MEMORY]))

    def test_compose_short_number_split_1_0(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 0):
            working_memories[memory.SHORT_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.SHORT_MEMORY].append(mem)
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + 0, len(working_memories[memory.SHORT_MEMORY]))
        self.assertEqual(1, len(working_memories[memory.LONG_MEMORY]))
        self.assertEqual(0, len(new_working_memories[memory.SHORT_MEMORY]))

    def test_compose_short_number_split_1_2(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 2):
            working_memories[memory.SHORT_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.SHORT_MEMORY].append(mem)
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + 2, len(working_memories[memory.SHORT_MEMORY]))
        self.assertEqual(1, len(working_memories[memory.LONG_MEMORY]))
        self.assertEqual(2, len(new_working_memories[memory.SHORT_MEMORY]))

    def test_compose_short_number_split_2(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + memory.COMPOSE_NUMBER + 1):
            working_memories[memory.SHORT_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.SHORT_MEMORY].append(mem)
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + memory.COMPOSE_NUMBER + 1, len(working_memories[memory.SHORT_MEMORY]))
        self.assertEqual(2, len(working_memories[memory.LONG_MEMORY]))
        self.assertEqual(1, len(new_working_memories[memory.SHORT_MEMORY]))

    def test_compose_short_time_no_split(self):
        now = time.time()
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER - 1):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 1})
            working_memories[memory.SHORT_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.SHORT_MEMORY].append(mem)
            now = now + 1
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(working_memories[memory.SHORT_MEMORY]))
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(new_working_memories[memory.SHORT_MEMORY]))
        self.assertEqual(0, len(working_memories[memory.LONG_MEMORY]))

    def test_compose_short_time_split_1_1(self):
        now = time.time()
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER - 1):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 3})
            working_memories[memory.SHORT_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.SHORT_MEMORY].append(mem)
            now = now + 3
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(working_memories[memory.SHORT_MEMORY]))
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(new_working_memories[memory.SHORT_MEMORY]))
        self.assertEqual(0, len(working_memories[memory.LONG_MEMORY]))

    def test_compose_short_time_split_1_0(self):
        now = time.time()
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER - 1):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 2})
            working_memories[memory.SHORT_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.SHORT_MEMORY].append(mem)
            now = now + 2
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(working_memories[memory.SHORT_MEMORY]))
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(new_working_memories[memory.SHORT_MEMORY]))
        self.assertEqual(0, len(working_memories[memory.LONG_MEMORY]))

    def test_compose_short_time_split_1_2(self):
        now = time.time()
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 3})
            working_memories[memory.SHORT_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.SHORT_MEMORY].append(mem)
            now = now + 3
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER, len(working_memories[memory.SHORT_MEMORY]))
        self.assertEqual(0, len(new_working_memories[memory.SHORT_MEMORY]))
        self.assertEqual(1, len(working_memories[memory.LONG_MEMORY]))

    def test_compose_short_time_split_2(self):
        now = time.time()
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 3):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 2})
            working_memories[memory.SHORT_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.SHORT_MEMORY].append(mem)
            now = now + 2
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + 3, len(working_memories[memory.SHORT_MEMORY]))
        self.assertEqual(3, len(new_working_memories[memory.SHORT_MEMORY]))
        self.assertEqual(1, len(working_memories[memory.LONG_MEMORY]))

    def test_compose_long_number_no_split(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        working_memories[memory.LONG_MEMORY].update({mem[memory.ID]: mem})
        new_working_memories[memory.LONG_MEMORY].append(mem)
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(1, len(working_memories[memory.LONG_MEMORY]))
        self.assertEqual(1, len(new_working_memories[memory.LONG_MEMORY]))

    def test_compose_long_number_split_1_1(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 1):
            working_memories[memory.LONG_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.LONG_MEMORY].append(mem)
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + 1 + 1, len(working_memories[memory.LONG_MEMORY]))
        self.assertEqual(1 + 1, len(new_working_memories[memory.LONG_MEMORY]))

    def test_compose_long_number_split_1_0(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 0):
            working_memories[memory.LONG_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.LONG_MEMORY].append(mem)
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + 1, len(working_memories[memory.LONG_MEMORY]))
        self.assertEqual(1, len(new_working_memories[memory.LONG_MEMORY]))

    def test_compose_long_number_split_1_2(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 2):
            working_memories[memory.LONG_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.LONG_MEMORY].append(mem)
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + 2 + 1, len(working_memories[memory.LONG_MEMORY]))
        self.assertEqual(1 + 2, len(new_working_memories[memory.LONG_MEMORY]))

    def test_compose_long_number_split_2(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.ID: 1000, memory.HAPPEN_TIME: time.time()})
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + memory.COMPOSE_NUMBER + 1):
            working_memories[memory.LONG_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.LONG_MEMORY].append(mem)
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + memory.COMPOSE_NUMBER + 1 + 2, len(working_memories[memory.LONG_MEMORY]))
        self.assertEqual(1 + 2, len(new_working_memories[memory.LONG_MEMORY]))

    def test_compose_long_time_no_split(self):
        now = time.time()
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER - 1):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 1})
            working_memories[memory.LONG_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.LONG_MEMORY].append(mem)
            now = now + 1
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(working_memories[memory.LONG_MEMORY]))
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(new_working_memories[memory.LONG_MEMORY]))

    def test_compose_long_time_split_1_1(self):
        now = time.time()
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER - 1):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 3})
            working_memories[memory.LONG_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.LONG_MEMORY].append(mem)
            now = now + 3
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(working_memories[memory.LONG_MEMORY]))
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(new_working_memories[memory.LONG_MEMORY]))

    def test_compose_long_time_split_1_0(self):
        now = time.time()
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER - 1):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 2})
            working_memories[memory.LONG_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.LONG_MEMORY].append(mem)
            now = now + 2
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(working_memories[memory.LONG_MEMORY]))
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(new_working_memories[memory.LONG_MEMORY]))

    def test_compose_long_time_split_1_2(self):
        now = time.time()
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 3})
            working_memories[memory.LONG_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.LONG_MEMORY].append(mem)
            now = now + 3
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + 1, len(working_memories[memory.LONG_MEMORY]))
        self.assertEqual(1, len(new_working_memories[memory.LONG_MEMORY]))

    def test_compose_long_time_split_2(self):
        now = time.time()
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 3):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.ID: 1000, memory.HAPPEN_TIME: now + 2})
            working_memories[memory.LONG_MEMORY].update({mem[memory.ID] + num: mem})
            new_working_memories[memory.LONG_MEMORY].append(mem)
            now = now + 2
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + 3 + 1, len(working_memories[memory.LONG_MEMORY]))
        self.assertEqual(3 + 1, len(new_working_memories[memory.LONG_MEMORY]))


if __name__ == "__main__":
    unittest.main()
