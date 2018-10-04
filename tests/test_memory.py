import unittest, memory, sound, time, copy
from db import Database
from tinydb import TinyDB
from tinydb.storages import MemoryStorage
from tinydb.database import Document


class TestMemory(unittest.TestCase):
    database = None

    def setUp(self):
        self.database = Database(TinyDB(storage=MemoryStorage))
        memory.forget_memory = False
        memory.db = self.database

    # test find parent memories
    def test_count_parent_id1(self):
        mem1 = memory.BASIC_MEMORY.copy()
        mem1.update({memory.PARENTS: [5, 6, 7]})
        mem2 = memory.BASIC_MEMORY.copy()
        mem2.update({memory.PARENTS: [6, 7, 8]})
        mem3 = memory.BASIC_MEMORY.copy()
        mem3.update({memory.PARENTS: [7, 8, 9]})
        working_memory = [mem1, mem2, mem3]
        parent_counts = memory.count_parent_id(working_memory)
        self.assertIsNotNone(parent_counts)
        self.assertEqual(1, parent_counts.get(5))
        self.assertEqual(3, parent_counts.get(7))

    # test find parent memories
    def test_count_parent_id2(self):
        mem1 = memory.BASIC_MEMORY.copy()
        mem1.update({memory.PARENTS: [5, 6, 7]})
        mem3 = memory.BASIC_MEMORY.copy()
        mem3.update({memory.PARENTS: [8, 9]})
        working_memory = [mem1, mem3]
        parent_counts = memory.count_parent_id(working_memory)
        self.assertIsNotNone(parent_counts)
        self.assertEqual(1, parent_counts.get(5))
        self.assertEqual(1, parent_counts.get(7))

    # test can not find exp memory, as all count are 1
    def test_find_max_related_memory_ids0(self):
        mem1 = memory.BASIC_MEMORY.copy()
        mem1.update({memory.PARENTS: [5, 6, 7]})
        mem2 = memory.BASIC_MEMORY.copy()
        mem2.update({memory.PARENTS: [8, 9]})
        working_memory = [mem1, mem2]
        related_memory_ids = memory.find_max_related_memory_ids(working_memory)
        self.assertEqual(0, len(related_memory_ids))

    # test find exp memory, the top one
    def test_find_max_related_memory_ids1(self):
        mem1 = memory.BASIC_MEMORY.copy()
        mem1.update({memory.PARENTS: [5, 6, 7]})
        mem2 = memory.BASIC_MEMORY.copy()
        mem2.update({memory.PARENTS: [6, 7, 8]})
        mem3 = memory.BASIC_MEMORY.copy()
        mem3.update({memory.PARENTS: [7, 8, 9]})
        working_memories = [mem1, mem2, mem3]
        related_memory_ids = memory.find_max_related_memory_ids(working_memories)
        self.assertEqual(1, len(related_memory_ids))

    # test find exp memory, one of the tops
    def test_find_max_related_memory_ids2(self):
        mem1 = memory.BASIC_MEMORY.copy()
        mem1.update({memory.PARENTS: [5, 6, 7]})
        mem2 = memory.BASIC_MEMORY.copy()
        mem2.update({memory.PARENTS: [5, 6, 7]})
        working_memories = [mem1, mem2]
        related_memory_ids = memory.find_max_related_memory_ids(working_memories)
        self.assertEqual(3, len(related_memory_ids))

    def test_find_max_related_memory_success(self):
        el1 = self.database.add_memory()
        el2 = self.database.add_memory({memory.PARENTS: [5, 6, el1[memory.ID]]})
        el3 = self.database.add_memory({memory.PARENTS: [6, el1[memory.ID], 8]})
        working_memories = [el2, el3]
        memories = memory.find_max_related_memories(working_memories)
        self.assertEqual(1, len(memories))
        mem = self.database.get_memory(el2[memory.ID])
        self.assertEqual(el1[memory.ID], mem[memory.PARENTS][0])

    def test_find_max_related_memory_empty(self):
        el1 = self.database.add_memory({memory.PARENTS: [5, 6, 7]})
        el2 = self.database.add_memory({memory.PARENTS: [6, 7, 8]})
        working_memories = [el1, el2]
        memories = memory.find_max_related_memories(working_memories)
        self.assertEqual(0, len(memories))

    def test_find_max_related_memory_limit(self):
        el1 = self.database.add_memory()
        el2 = self.database.add_memory()
        el3 = self.database.add_memory({memory.PARENTS: [5, 6, el1[memory.ID], el2[memory.ID]]})
        el4 = self.database.add_memory({memory.PARENTS: [6, el1[memory.ID], el2[memory.ID], 8]})
        working_memories = [el3, el4]
        memories = memory.find_max_related_memories(working_memories, 1)
        self.assertEqual(1, len(memories))

    def test_find_target0(self):
        el1 = self.database._add_memory({memory.REWARD: 100})
        el2 = self.database._add_memory({memory.REWARD: 99})
        el3 = self.database._add_memory({memory.REWARD: 98})
        mem1 = self.database._get_memory(el1)
        mem2 = self.database._get_memory(el2)
        mem3 = self.database._get_memory(el3)
        related_memory_ids = [mem1, mem2, mem3]
        exp_memory = memory.find_reward_target(related_memory_ids)
        self.assertEqual(el1, exp_memory)

    def test_find_target1(self):
        el1 = self.database._add_memory({memory.REWARD: 97})
        el2 = self.database._add_memory({memory.REWARD: 99})
        el3 = self.database._add_memory({memory.REWARD: 99})
        mem1 = self.database._get_memory(el1)
        mem2 = self.database._get_memory(el2)
        mem3 = self.database._get_memory(el3)
        related_memory_ids = [mem1, mem2, mem3]
        exp_memory = memory.find_reward_target(related_memory_ids)
        self.assertEqual(el2, exp_memory)

    def test_remove_memories(self):
        el1 = self.database.add_memory()
        el2 = self.database.add_memory()
        memory_list = [el1, el2]
        tobe_remove_list_ids = [el1[memory.ID]]
        memory.remove_memories(memory_list, tobe_remove_list_ids)
        self.assertEqual(1, len(memory_list))

    def test_remove_memories2(self):
        el1 = self.database.add_memory()
        el2 = self.database.add_memory()
        el3 = self.database.add_memory()
        memory_list = [el1, el2, el3]
        tobe_remove_list_ids = [el2[memory.ID]]
        memory.remove_memories(memory_list, tobe_remove_list_ids)
        self.assertEqual(2, len(memory_list))

    def test_remove_memories3(self):
        el1 = self.database.add_memory()
        el2 = self.database.add_memory()
        el3 = self.database.add_memory()
        memory_list = [el1, el2, el3]
        tobe_remove_list_ids = [el2[memory.ID], el3[memory.ID]]
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

    def test_remove_memory_children(self):
        children = [1, 2, 3, 4, 5]
        forgot = [1, 3, 5]
        el1 = self.database.add_memory({memory.CHILD_MEM: children})
        memory.remove_memory_children(children, forgot, el1[memory.ID])
        mem = self.database.get_memory(el1[memory.ID])
        self.assertEqual(2, len(mem[memory.CHILD_MEM]))
        self.assertEqual(4, mem[memory.CHILD_MEM][1])

    def test_get_valid_child_memory_empty(self):
        el1 = self.database.add_memory({memory.CHILD_MEM: []})
        memories = memory.get_live_child_memories(el1)
        self.assertEqual(0, len(memories))

    def test_get_valid_child_memory_success(self):
        el1 = self.database.add_memory()
        el2 = self.database.add_memory()
        el3 = self.database.add_memory({memory.CHILD_MEM: [el1[memory.ID], el2[memory.ID]]})
        child_memories1 = memory.get_live_child_memories(el3)
        self.assertEqual(2, len(child_memories1))

        el4 = self.database.add_memory({memory.CHILD_MEM: [el1[memory.ID], el2[memory.ID], 9]})
        child_memories2 = memory.get_live_child_memories(el4)
        self.assertEqual(2, len(child_memories2))
        self.assertEqual(el2[memory.ID], child_memories2[1][memory.ID])

        el5 = self.database.add_memory({memory.CHILD_MEM: [el1[memory.ID], 9, el2[memory.ID]]})
        child_memories3 = memory.get_live_child_memories(el5)
        self.assertEqual(2, len(child_memories3))
        self.assertEqual(el2[memory.ID], child_memories3[1][memory.ID])

        el6 = self.database.add_memory({memory.CHILD_MEM: [8, 9]})
        memory.get_live_child_memories(el6)
        mem = self.database.get_memory(el6[memory.ID])
        self.assertIsNone(mem)


if __name__ == "__main__":
    unittest.main()
