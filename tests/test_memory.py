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

    # test find parent memories
    def test_find_parents1(self):
        mem1 = memory.BASIC_MEMORY.copy()
        mem1.update({memory.PARENTS: [5, 6, 7]})
        mem2 = memory.BASIC_MEMORY.copy()
        mem2.update({memory.PARENTS: [6, 7, 8]})
        mem3 = memory.BASIC_MEMORY.copy()
        mem3.update({memory.PARENTS: [7, 8, 9]})
        working_memory = [mem1, mem2, mem3]
        parent_counts = memory.find_parents(working_memory)
        self.assertIsNotNone(parent_counts)
        self.assertEqual(1, parent_counts.get(5))
        self.assertEqual(3, parent_counts.get(7))

    # test find parent memories
    def test_find_parents2(self):
        mem1 = memory.BASIC_MEMORY.copy()
        mem1.update({memory.PARENTS: [5, 6, 7]})
        mem3 = memory.BASIC_MEMORY.copy()
        mem3.update({memory.PARENTS: [8, 9]})
        working_memory = [mem1, mem3]
        parent_counts = memory.find_parents(working_memory)
        self.assertIsNotNone(parent_counts)
        self.assertEqual(1, parent_counts.get(5))
        self.assertEqual(1, parent_counts.get(7))

    # test can not find exp memory, as all count are 1
    def test_find_exp_mem_id0(self):
        mem1 = memory.BASIC_MEMORY.copy()
        mem1.update({memory.PARENTS: [5, 6, 7]})
        mem2 = memory.BASIC_MEMORY.copy()
        mem2.update({memory.PARENTS: [8, 9]})
        working_memory = [mem1, mem2]
        related_memory_ids = memory.find_related_memory_ids(working_memory)
        self.assertEqual(0, len(related_memory_ids))

    # test find exp memory, the top one
    def test_find_exp_mem_id1(self):
        mem1 = memory.BASIC_MEMORY.copy()
        mem1.update({memory.PARENTS: [5, 6, 7]})
        mem2 = memory.BASIC_MEMORY.copy()
        mem2.update({memory.PARENTS: [6, 7, 8]})
        mem3 = memory.BASIC_MEMORY.copy()
        mem3.update({memory.PARENTS: [7, 8, 9]})
        working_memory = [mem1, mem2, mem3]
        related_memory_ids = memory.find_related_memory_ids(working_memory)
        self.assertEqual(1, len(related_memory_ids))

    # test find exp memory, one of the tops
    def test_find_exp_mem_id2(self):
        mem1 = memory.BASIC_MEMORY.copy()
        mem1.update({memory.PARENTS: [5, 6, 7]})
        mem2 = memory.BASIC_MEMORY.copy()
        mem2.update({memory.PARENTS: [5, 6, 7]})
        working_memory = [mem1, mem2]
        related_memory_ids = memory.find_related_memory_ids(working_memory)
        self.assertEqual(3, len(related_memory_ids))

    def test_find_target0(self):
        el1 = self.database._add_memory({memory.REWARD: 100})
        el2 = self.database._add_memory({memory.REWARD: 99})
        el3 = self.database._add_memory({memory.REWARD: 98})
        mem1 = self.database._get_memory(el1)
        mem2 = self.database._get_memory(el2)
        mem3 = self.database._get_memory(el3)
        related_memory_ids = [mem1, mem2, mem3]
        exp_memory = memory.find_reward_target(related_memory_ids)
        self.assertEqual(1, exp_memory)

    def test_find_target1(self):
        el1 = self.database._add_memory({memory.REWARD: 97})
        el2 = self.database._add_memory({memory.REWARD: 99})
        el3 = self.database._add_memory({memory.REWARD: 99})
        mem1 = self.database._get_memory(el1)
        mem2 = self.database._get_memory(el2)
        mem3 = self.database._get_memory(el3)
        related_memory_ids = [mem1, mem2, mem3]
        exp_memory = memory.find_reward_target(related_memory_ids)
        self.assertEqual(2, exp_memory)

    def test_remove_memories(self):
        el1 = self.database.add_memory()
        el2 = self.database.add_memory()
        memory_list = [el1, el2]
        tobe_remove_list_ids = [el1.doc_id]
        memory.remove_memories(memory_list, tobe_remove_list_ids)
        self.assertEqual(1, len(memory_list))

    def test_remove_memories2(self):
        el1 = self.database.add_memory()
        el2 = self.database.add_memory()
        el3 = self.database.add_memory()
        memory_list = [el1, el2, el3]
        tobe_remove_list_ids = [el2.doc_id]
        memory.remove_memories(memory_list, tobe_remove_list_ids)
        self.assertEqual(2, len(memory_list))

    def test_remove_memories3(self):
        el1 = self.database.add_memory()
        el2 = self.database.add_memory()
        el3 = self.database.add_memory()
        memory_list = [el1, el2, el3]
        tobe_remove_list_ids = [el2.doc_id, el3.doc_id]
        memory.remove_memories(memory_list, tobe_remove_list_ids)
        self.assertEqual(1, len(memory_list))

    def test_get_common_parents(self):
        memory.db = self.database
        feature_memories = []
        c1 = self.database.add_sound({sound.FEATURE: sound.FEATURE_MAX_ENERGY, sound.ENERGY: 5000})
        feature_memories.append(c1)
        common_parents = memory.find_common_parents(feature_memories)
        self.assertEqual(0, len(common_parents))
        self.assertEqual(1, len(feature_memories))
        c2 = self.database.add_sound({sound.FEATURE: sound.FEATURE_MAX_ENERGY, sound.ENERGY: 5000})
        feature_memories.append(c2)
        # now add 2 children to a parent
        self.database.add_parent([c1, c2])
        common_parents = memory.find_common_parents(feature_memories)
        self.assertEqual(1, len(common_parents))
        self.assertEqual(0, len(feature_memories))

    def test_split_working_memories_empty(self):
        memories = []
        result = memory.split_working_memories(memories)
        self.assertEqual(0, len(result[memory.NEW_MEMORIES]))
        self.assertEqual(0, len(result[memory.REST_OF_MEMORIES]))

    def test_split_working_memories_number_no_split(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.HAPPEN_TIME: time.time()})
        memories = [mem]
        result = memory.split_working_memories(memories)
        self.assertEqual(0, len(result[memory.NEW_MEMORIES]))
        self.assertEqual(1, len(result[memory.REST_OF_MEMORIES]))

    def test_split_working_memories_number_split_1_1(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.HAPPEN_TIME: time.time()})
        memories = []
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 1):
            memories.append(mem)
        result = memory.split_working_memories(memories)
        self.assertEqual(1, len(result[memory.NEW_MEMORIES]))
        self.assertEqual(1, len(result[memory.REST_OF_MEMORIES]))

    def test_split_working_memories_number_split_1_2(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.HAPPEN_TIME: time.time()})
        memories = []
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 2):
            memories.append(mem)
        result = memory.split_working_memories(memories)
        self.assertEqual(1, len(result[memory.NEW_MEMORIES]))
        self.assertEqual(2, len(result[memory.REST_OF_MEMORIES]))

    def test_split_working_memories_number_split_2(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({memory.HAPPEN_TIME: time.time()})
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
            mem.update({memory.HAPPEN_TIME: now + 1})
            memories.append(mem)
            now = now + 1
        result = memory.split_working_memories(memories, 6)
        self.assertEqual(0, len(result[memory.NEW_MEMORIES]))
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(result[memory.REST_OF_MEMORIES]))

    def test_split_working_memories_time_split_1_1(self):
        now = time.time()
        memories = []
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 1):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.HAPPEN_TIME: now + 1})
            memories.append(mem)
            now = now + 1
        result = memory.split_working_memories(memories, 5)
        self.assertEqual(1, len(result[memory.NEW_MEMORIES]))
        self.assertEqual(1, len(result[memory.REST_OF_MEMORIES]))

    def test_split_working_memories_time_split_1_2(self):
        now = time.time()
        memories = []
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 2):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.HAPPEN_TIME: now + 1})
            memories.append(mem)
            now = now + 1
        result = memory.split_working_memories(memories, 5)
        self.assertEqual(1, len(result[memory.NEW_MEMORIES]))
        self.assertEqual(2, len(result[memory.REST_OF_MEMORIES]))

    def test_split_working_memories_time_split_2(self):
        now = time.time()
        memories = []
        for num in range(1, memory.COMPOSE_NUMBER + 1 + memory.COMPOSE_NUMBER + 1):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.HAPPEN_TIME: now + 1})
            memories.append(mem)
            now = now + 1
        result = memory.split_working_memories(memories, 5)
        self.assertEqual(2, len(result[memory.NEW_MEMORIES]))
        self.assertEqual(1, len(result[memory.REST_OF_MEMORIES]))

    def test_split_working_memories_mix(self):
        now = time.time()
        memories = []
        for num in range(1, memory.COMPOSE_NUMBER + 1 + 1):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({memory.HAPPEN_TIME: now + 1})
            memories.append(mem)
            now = now + 1
        result = memory.split_working_memories(memories, 10)
        self.assertEqual(1, len(result[memory.NEW_MEMORIES]))
        self.assertEqual(1, len(result[memory.REST_OF_MEMORIES]))

    def test_compose_slice_number_no_split(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({'doc_id': 1000, memory.HAPPEN_TIME: time.time()})
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        working_memories[memory.SLICE_MEMORY].update({mem['doc_id']: mem})
        new_working_memories[memory.SLICE_MEMORY].append(mem)
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(1, len(working_memories[memory.SLICE_MEMORY]))
        self.assertEqual(1, len(new_working_memories[memory.SLICE_MEMORY]))

    def test_compose_slice_number_split_1_1(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({'doc_id': 1000, memory.HAPPEN_TIME: time.time()})
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 1):
            working_memories[memory.SLICE_MEMORY].update({mem['doc_id'] + num: mem})
            new_working_memories[memory.SLICE_MEMORY].append(mem)
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + 1, len(working_memories[memory.SLICE_MEMORY]))
        self.assertEqual(1, len(working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(1, len(new_working_memories[memory.SLICE_MEMORY]))

    def test_compose_slice_number_split_1_2(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({'doc_id': 1000, memory.HAPPEN_TIME: time.time()})
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 2):
            working_memories[memory.SLICE_MEMORY].update({mem['doc_id'] + num: mem})
            new_working_memories[memory.SLICE_MEMORY].append(mem)
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + 2, len(working_memories[memory.SLICE_MEMORY]))
        self.assertEqual(1, len(working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(2, len(new_working_memories[memory.SLICE_MEMORY]))

    def test_compose_slice_number_split_2(self):
        mem = memory.BASIC_MEMORY.copy()
        mem.update({'doc_id': 1000, memory.HAPPEN_TIME: time.time()})
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + memory.COMPOSE_NUMBER + 1):
            working_memories[memory.SLICE_MEMORY].update({mem['doc_id'] + num: mem})
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
            mem.update({'doc_id': 1000 + num, memory.HAPPEN_TIME: now + 0.1})
            working_memories[memory.SLICE_MEMORY].update({mem['doc_id'] + num: mem})
            new_working_memories[memory.SLICE_MEMORY].append(mem)
            now = now + 0.1
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(working_memories[memory.SLICE_MEMORY]))
        self.assertEqual(memory.COMPOSE_NUMBER - 1, len(new_working_memories[memory.SLICE_MEMORY]))

    def test_compose_slice_time_split_1_1(self):
        now = time.time()
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 1):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({'doc_id': 1000 + num, memory.HAPPEN_TIME: now + 0.1})
            working_memories[memory.SLICE_MEMORY].update({mem['doc_id'] + num: mem})
            new_working_memories[memory.SLICE_MEMORY].append(mem)
            now = now + 0.1
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + 1, len(working_memories[memory.SLICE_MEMORY]))
        self.assertEqual(1, len(working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(1, len(new_working_memories[memory.SLICE_MEMORY]))

    def test_compose_slice_time_split_1_2(self):
        now = time.time()
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + 2):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({'doc_id': 1000 + num, memory.HAPPEN_TIME: now + 0.1})
            working_memories[memory.SLICE_MEMORY].update({mem['doc_id'] + num: mem})
            new_working_memories[memory.SLICE_MEMORY].append(mem)
            now = now + 0.1
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + 2, len(working_memories[memory.SLICE_MEMORY]))
        self.assertEqual(1, len(working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(2, len(new_working_memories[memory.SLICE_MEMORY]))

    def test_compose_slice_time_split_2(self):
        now = time.time()
        working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
        new_working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        for num in range(1, 1 + memory.COMPOSE_NUMBER + memory.COMPOSE_NUMBER + 1):
            mem = memory.BASIC_MEMORY.copy()
            mem.update({'doc_id': 1000 + num, memory.HAPPEN_TIME: now + 0.1})
            working_memories[memory.SLICE_MEMORY].update({mem['doc_id'] + num: mem})
            new_working_memories[memory.SLICE_MEMORY].append(mem)
            now = now + 0.1
        memory.compose(working_memories, new_working_memories)
        self.assertEqual(memory.COMPOSE_NUMBER + memory.COMPOSE_NUMBER + 1, len(working_memories[memory.SLICE_MEMORY]))
        self.assertEqual(2, len(working_memories[memory.INSTANT_MEMORY]))
        self.assertEqual(1, len(new_working_memories[memory.SLICE_MEMORY]))


if __name__ == "__main__":
    unittest.main()
