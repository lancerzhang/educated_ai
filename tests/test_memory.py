import unittest, memory
from db import Database
from tinydb import TinyDB
from tinydb.storages import MemoryStorage


class TestMemory(unittest.TestCase):
    database = None

    def setUp(self):
        self.database = Database(TinyDB(storage=MemoryStorage))
        memory.forget_memory = False

    # test find parent memories
    def test_find_parents1(self):
        mem1 = memory.basic_memory.copy()
        mem1.update({'parents': [5, 6, 7]})
        mem2 = memory.basic_memory.copy()
        mem2.update({'parents': [6, 7, 8]})
        mem3 = memory.basic_memory.copy()
        mem3.update({'parents': [7, 8, 9]})
        working_memory = [mem1, mem2, mem3]
        parent_counts = memory.find_parents(working_memory)
        self.assertIsNotNone(parent_counts)
        self.assertEqual(1, parent_counts.get(5))
        self.assertEqual(3, parent_counts.get(7))

    # test find parent memories
    def test_find_parents2(self):
        mem1 = memory.basic_memory.copy()
        mem1.update({'parents': [5, 6, 7]})
        mem3 = memory.basic_memory.copy()
        mem3.update({'parents': [8, 9]})
        working_memory = [mem1, mem3]
        parent_counts = memory.find_parents(working_memory)
        self.assertIsNotNone(parent_counts)
        self.assertEqual(1, parent_counts.get(5))
        self.assertEqual(1, parent_counts.get(7))

    # test can not find exp memory, as all count are 1
    def test_find_exp_mem_id0(self):
        mem1 = memory.basic_memory.copy()
        mem1.update({'parents': [5, 6, 7]})
        mem2 = memory.basic_memory.copy()
        mem2.update({'parents': [8, 9]})
        working_memory = [mem1, mem2]
        related_memory_ids = memory.find_related_memory_ids(working_memory)
        self.assertEqual(0, len(related_memory_ids))

    # test find exp memory, the top one
    def test_find_exp_mem_id1(self):
        mem1 = memory.basic_memory.copy()
        mem1.update({'parents': [5, 6, 7]})
        mem2 = memory.basic_memory.copy()
        mem2.update({'parents': [6, 7, 8]})
        mem3 = memory.basic_memory.copy()
        mem3.update({'parents': [7, 8, 9]})
        working_memory = [mem1, mem2, mem3]
        related_memory_ids = memory.find_related_memory_ids(working_memory)
        self.assertEqual(1, len(related_memory_ids))

    # test find exp memory, one of the tops
    def test_find_exp_mem_id2(self):
        mem1 = memory.basic_memory.copy()
        mem1.update({'parents': [5, 6, 7]})
        mem2 = memory.basic_memory.copy()
        mem2.update({'parents': [5, 6, 7]})
        working_memory = [mem1, mem2]
        related_memory_ids = memory.find_related_memory_ids(working_memory)
        self.assertEqual(3, len(related_memory_ids))

    def test_find_exp_memory0(self):
        el1 = self.database.add_memory({'reward':100})
        el2 = self.database.add_memory({'reward':99})
        el3 = self.database.add_memory({'reward':98})
        mem1=self.database.get_memory(el1)
        mem2 = self.database.get_memory(el2)
        mem3 = self.database.get_memory(el3)
        related_memory_ids = [mem1, mem2, mem3]
        exp_memory=memory.find_exp_memory(related_memory_ids)
        self.assertEqual(1, exp_memory)

    def test_find_exp_memory1(self):
        el1 = self.database.add_memory({'reward':97})
        el2 = self.database.add_memory({'reward':99})
        el3 = self.database.add_memory({'reward':99})
        mem1=self.database.get_memory(el1)
        mem2 = self.database.get_memory(el2)
        mem3 = self.database.get_memory(el3)
        related_memory_ids = [mem1, mem2, mem3]
        exp_memory=memory.find_exp_memory(related_memory_ids)
        self.assertEqual(2, exp_memory)


if __name__ == "__main__":
    unittest.main()
