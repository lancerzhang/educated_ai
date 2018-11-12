import unittest, memory, status, time, copy
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
        mem1.update({memory.PARENT_MEM: [5, 6, 7]})
        mem2 = memory.BASIC_MEMORY.copy()
        mem2.update({memory.PARENT_MEM: [6, 7, 8]})
        mem3 = memory.BASIC_MEMORY.copy()
        mem3.update({memory.PARENT_MEM: [7, 8, 9]})
        seq_time_memories = [mem1, mem2, mem3]
        parent_counts = memory.count_parent_id(seq_time_memories)
        self.assertIsNotNone(parent_counts)
        self.assertEqual(1, parent_counts.get(5))
        self.assertEqual(3, parent_counts.get(7))

    # test find parent memories
    def test_count_parent_id2(self):
        mem1 = memory.BASIC_MEMORY.copy()
        mem1.update({memory.PARENT_MEM: [5, 6, 7]})
        mem3 = memory.BASIC_MEMORY.copy()
        mem3.update({memory.PARENT_MEM: [8, 9]})
        seq_time_memories = [mem1, mem3]
        parent_counts = memory.count_parent_id(seq_time_memories)
        self.assertIsNotNone(parent_counts)
        self.assertEqual(1, parent_counts.get(5))
        self.assertEqual(1, parent_counts.get(7))

    def test_find_max_related_memory_success(self):
        mem1 = self.database.add_memory()
        mem2 = self.database.add_memory({memory.PARENT_MEM: [5, 6, mem1[memory.ID]]})
        mem3 = self.database.add_memory({memory.PARENT_MEM: [6, mem1[memory.ID], 8]})
        seq_time_memories = [mem2, mem3]
        memories = memory.find_update_max_related_memories(seq_time_memories)
        self.assertEqual(1, len(memories))
        mem = self.database.get_memory(mem2[memory.ID])
        self.assertEqual(mem1[memory.ID], mem[memory.PARENT_MEM][0])

    def test_find_max_related_memory_empty(self):
        mem1 = self.database.add_memory({memory.PARENT_MEM: [5, 6, 7]})
        mem2 = self.database.add_memory({memory.PARENT_MEM: [6, 7, 8]})
        seq_time_memories = [mem1, mem2]
        memories = memory.find_update_max_related_memories(seq_time_memories)
        self.assertEqual(0, len(memories))

    def test_find_max_related_memory_limit(self):
        mem1 = self.database.add_memory()
        mem2 = self.database.add_memory()
        mem3 = self.database.add_memory({memory.PARENT_MEM: [5, 6, mem1[memory.ID], mem2[memory.ID]]})
        mem4 = self.database.add_memory({memory.PARENT_MEM: [6, mem1[memory.ID], mem2[memory.ID], 8]})
        seq_time_memories = [mem3, mem4]
        memories = memory.find_update_max_related_memories(seq_time_memories, 1)
        self.assertEqual(1, len(memories))

    def test_remove_memory_children(self):
        children = [1, 2, 3, 4, 5]
        forgot = [1, 3, 5]
        mem1 = self.database.add_memory({memory.CHILD_MEM: children})
        memory.remove_dead_memories(memory.CHILD_MEM, children, forgot, mem1[memory.ID])
        mem = self.database.get_memory(mem1[memory.ID])
        self.assertEqual(2, len(mem[memory.CHILD_MEM]))
        self.assertEqual(4, mem[memory.CHILD_MEM][1])

    def get_live_sub_memories_empty(self):
        mem1 = self.database.add_memory({memory.CHILD_MEM: []})
        memories = memory.get_live_sub_memories(mem1, memory.CHILD_MEM)
        self.assertEqual(0, len(memories))

    def get_live_sub_memories_success(self):
        mem1 = self.database.add_memory()
        mem2 = self.database.add_memory()
        mem3 = self.database.add_memory({memory.CHILD_MEM: [mem1[memory.ID], mem2[memory.ID]]})
        child_memories1 = memory.get_live_sub_memories(mem3, memory.CHILD_MEM)
        self.assertEqual(2, len(child_memories1))

        mem4 = self.database.add_memory({memory.CHILD_MEM: [mem1[memory.ID], mem2[memory.ID], 9]})
        child_memories2 = memory.get_live_sub_memories(mem4, memory.CHILD_MEM)
        self.assertEqual(2, len(child_memories2))
        self.assertEqual(mem2[memory.ID], child_memories2[1][memory.ID])

        el5 = self.database.add_memory({memory.CHILD_MEM: [mem1[memory.ID], 9, mem2[memory.ID]]})
        child_memories3 = memory.get_live_sub_memories(el5, memory.CHILD_MEM)
        self.assertEqual(2, len(child_memories3))
        self.assertEqual(mem2[memory.ID], child_memories3[1][memory.ID])

        el6 = self.database.add_memory({memory.CHILD_MEM: [8, 9]})
        memory.get_live_sub_memories(el6, memory.CHILD_MEM)
        mem = self.database.get_memory(el6[memory.ID])
        self.assertIsNone(mem)

    def test_get_memories(self):
        mem1 = self.database.add_memory({memory.STATUS: memory.MATCHED, memory.DURATION: 1, memory.REWARD: 0.5})
        mem2 = self.database.add_memory({memory.STATUS: memory.MATCHING, memory.DURATION: 1, memory.REWARD: 0.6})
        mem3 = self.database.add_memory({memory.STATUS: memory.EXPIRED, memory.DURATION: 3, memory.REWARD: 0.3})
        memories = [mem1, mem2, mem3]
        matched_list = [x for x in memories if x[memory.STATUS] is memory.MATCHED]
        self.assertEqual(1, len(matched_list))
        sorted_list1 = sorted(memories, key=lambda x: (x[memory.DURATION]), reverse=True)
        self.assertEqual(memory.EXPIRED, sorted_list1[0][memory.STATUS])
        sorted_list2 = sorted(memories, key=lambda x: (x[memory.REWARD]), reverse=True)
        self.assertEqual(memory.MATCHING, sorted_list2[0][memory.STATUS])
        sorted_list3 = sorted(memories, key=lambda x: (x[memory.DURATION], x[memory.REWARD]))
        self.assertEqual(memory.MATCHED, sorted_list3[0][memory.STATUS])

    def test_find_max_related_memories(self):
        mem1 = self.database.add_memory()
        mem2 = self.database.add_memory()
        mem3 = memory.BASIC_MEMORY.copy()
        mem3.update({memory.ID: 3})
        mem4 = memory.BASIC_MEMORY.copy()
        mem4.update({memory.ID: 4})
        mem5 = self.database.add_memory({memory.PARENT_MEM: [mem1[memory.ID], mem2[memory.ID], mem3[memory.ID]]})
        mem6 = self.database.add_memory({memory.PARENT_MEM: [mem2[memory.ID], mem3[memory.ID], mem4[memory.ID]]})
        memories = [mem5, mem6]
        tobe_remove_list_ids = []
        related_memories = memory.find_max_related_memories(memories, tobe_remove_list_ids)
        self.assertEquals(2, len(related_memories))
        self.assertEquals(2, len(tobe_remove_list_ids))
        mem7 = self.database.add_memory({memory.PARENT_MEM: [mem2[memory.ID], mem3[memory.ID], mem4[memory.ID]]})
        memories.append(mem7)
        tobe_remove_list_ids2 = []
        related_memories2 = memory.find_max_related_memories(memories, tobe_remove_list_ids2, 1)
        self.assertEquals(1, len(related_memories2))
        self.assertEquals(mem2[memory.ID], related_memories2[0][memory.ID])

    def test_remove_dead_memories(self):
        child_mem = ['a1', 'b2', 'c3']
        mem1 = self.database.add_memory({memory.CHILD_MEM: child_mem})
        forget_ids = ['c3']
        memory.remove_dead_memories(memory.CHILD_MEM, child_mem, forget_ids, mem1[memory.ID])
        mem1b = self.database.get_memory(mem1[memory.ID])
        forget_ids2 = ['a1', 'b2']
        self.assertEquals(forget_ids2, mem1b[memory.CHILD_MEM])
        memory.remove_dead_memories(memory.CHILD_MEM, mem1b[memory.CHILD_MEM], forget_ids2, mem1[memory.ID])
        mem1c = self.database.get_memory(mem1[memory.ID])
        self.assertIsNone(mem1c)

    def test_search_sub_memories(self):
        mem1 = self.database.add_memory()
        mem2 = self.database.add_memory()
        mem3 = self.database.add_memory({memory.CHILD_MEM: [mem1[memory.ID], mem2[memory.ID]]})
        mem4 = self.database.add_memory()
        mem6 = self.database.add_memory({memory.CHILD_MEM: [mem4[memory.ID], mem2[memory.ID]]})
        memories = [mem3, mem6]
        distinct_sub_memory_list = []
        sub_memory_dict = {}
        memory.search_sub_memories(memories, distinct_sub_memory_list, sub_memory_dict)
        self.assertEquals(3, len(distinct_sub_memory_list))
        self.assertEquals(2, len(sub_memory_dict))

    def test_create_working_memory(self):
        seq_time_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        mem1 = self.database.add_memory({memory.REWARD: 1})
        mem2 = self.database.add_memory({memory.REWARD: 2})
        memories = [mem1, mem2]
        memory.create_working_memory(seq_time_memories, [memories], memory.SLICE_MEMORY)
        self.assertEquals(2, seq_time_memories[memory.SLICE_MEMORY][0][memory.REWARD])

    def test_append_working_memories(self):
        mem1 = self.database.add_memory({memory.MEMORY_DURATION: memory.INSTANT_MEMORY})
        working_memories = []
        new_memories = [mem1]
        memory.append_working_memories(working_memories, new_memories)
        self.assertEquals(1, len(working_memories))
        self.assertGreater(working_memories[0][memory.START_TIME], 0)
        self.assertGreater(working_memories[0][memory.END_TIME], 0)
        self.assertGreater(working_memories[0][memory.LAST_RECALL], 0)
        memory.append_working_memories(working_memories, new_memories)
        self.assertEquals(1, len(working_memories))
        mem2 = self.database.add_memory({memory.MEMORY_DURATION: memory.INSTANT_MEMORY})
        mem3 = self.database.add_memory({memory.MEMORY_DURATION: memory.INSTANT_MEMORY})
        new_memories2 = [mem2, mem3]
        memory.append_working_memories(working_memories, new_memories2, 1)
        self.assertEquals(2, len(working_memories))

    def test_associate_slice_empty(self):
        memory.threshold_of_working_memories = 3
        mem0 = self.database.add_memory({memory.END_TIME: 1})
        pmem1 = self.database.add_memory(
            {memory.LAST_RECALL: 1, memory.REWARD: 1, memory.MEMORY_DURATION: memory.SLICE_MEMORY})
        pmem2 = self.database.add_memory(
            {memory.LAST_RECALL: 2, memory.REWARD: 2, memory.MEMORY_DURATION: memory.SLICE_MEMORY})
        now = time.time() + 100
        mem3 = self.database.add_memory(
            {memory.END_TIME: now, memory.STATUS: memory.MATCHED,
             memory.PARENT_MEM: [5, 6, pmem1[memory.ID], pmem2[memory.ID]]})
        mem4 = self.database.add_memory(
            {memory.END_TIME: now, memory.STATUS: memory.MATCHED,
             memory.PARENT_MEM: [6, pmem1[memory.ID], pmem2[memory.ID], 8]})
        mem3[memory.LAST_RECALL] = now
        mem4[memory.LAST_RECALL] = now
        memories = [mem0, mem3, mem4]
        working_memories = memory.associate(memories)
        self.assertEqual(3, len(working_memories))
        self.assertEqual(2, working_memories[2][memory.REWARD])

    def test_prepare_expectation(self):
        mem1 = self.database.add_memory({memory.MEMORY_DURATION: memory.SLICE_MEMORY})
        mem2 = self.database.add_memory({memory.MEMORY_DURATION: memory.SLICE_MEMORY})
        imem1 = self.database.add_memory(
            {memory.MEMORY_DURATION: memory.INSTANT_MEMORY, memory.STATUS: memory.MATCHING,
             memory.CHILD_MEM: [5, 6, mem1[memory.ID], mem2[memory.ID]]})
        imem2 = self.database.add_memory(
            {memory.MEMORY_DURATION: memory.INSTANT_MEMORY, memory.STATUS: memory.MATCHING})
        smem1 = self.database.add_memory(
            {memory.MEMORY_DURATION: memory.SHORT_MEMORY, memory.STATUS: memory.MATCHING,
             memory.CHILD_MEM: [5, 6, imem1[memory.ID], imem2[memory.ID]]})
        working_memories = [imem1, smem1]
        memory.prepare_expectation(working_memories)
        self.assertEquals(4, len(working_memories))

    def test_check_expectation(self):
        new_time = time.time() + 10000
        sequential_time_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        mem1 = self.database.add_memory(
            {memory.MEMORY_DURATION: memory.SLICE_MEMORY, memory.STATUS: memory.MATCHED, memory.END_TIME: new_time})
        mem2 = self.database.add_memory(
            {memory.MEMORY_DURATION: memory.SLICE_MEMORY, memory.STATUS: memory.MATCHED, memory.END_TIME: new_time})
        mem3 = self.database.add_memory(
            {memory.MEMORY_DURATION: memory.SLICE_MEMORY, memory.STATUS: memory.MATCHING, memory.END_TIME: new_time})
        imem1 = self.database.add_memory(
            {memory.MEMORY_DURATION: memory.INSTANT_MEMORY, memory.STATUS: memory.MATCHING,
             memory.CHILD_MEM: [5, 6, mem1[memory.ID], mem2[memory.ID]], memory.END_TIME: new_time})
        imem2 = self.database.add_memory(
            {memory.MEMORY_DURATION: memory.INSTANT_MEMORY, memory.STATUS: memory.MATCHING,
             memory.CHILD_MEM: [mem3[memory.ID]], memory.END_TIME: new_time})
        smem1 = self.database.add_memory(
            {memory.MEMORY_DURATION: memory.SHORT_MEMORY, memory.STATUS: memory.MATCHING,
             memory.CHILD_MEM: [5, 6, imem1[memory.ID], imem2[memory.ID]], memory.END_TIME: new_time})
        smem2 = self.database.add_memory(
            {memory.MEMORY_DURATION: memory.SHORT_MEMORY, memory.STATUS: memory.MATCHED, memory.END_TIME: new_time})
        smem3 = self.database.add_memory(
            {memory.MEMORY_DURATION: memory.SHORT_MEMORY, memory.STATUS: memory.MATCHING, memory.END_TIME: 1})
        working_memories = [mem1, mem2, imem1, imem2, smem1, smem2, smem3, mem3]
        memory.check_expectation(working_memories, sequential_time_memories)
        self.assertEquals(memory.MATCHED, imem1[memory.STATUS])
        self.assertEquals(memory.MATCHING, imem2[memory.STATUS])
        self.assertEquals(memory.MATCHING, smem1[memory.STATUS])
        self.assertEquals(memory.EXPIRED, smem3[memory.STATUS])
        self.assertEquals(1, len(sequential_time_memories[memory.INSTANT_MEMORY]))
        matched_memories = [mem for mem in working_memories if mem[memory.STATUS] is memory.MATCHED]
        self.assertEquals(5, len(matched_memories))
        matching_memories = [mem for mem in working_memories if mem[memory.STATUS] is memory.MATCHING]
        self.assertEquals(2, len(matching_memories))
        expired_memories = [mem for mem in working_memories if mem[memory.STATUS] is memory.EXPIRED]
        self.assertEquals(1, len(expired_memories))

    def test_cleanup_working_memories(self):
        new_time = time.time() + 10000
        reward = {status.REWARD: True}
        mem1 = self.database.add_memory(
            {memory.MEMORY_DURATION: memory.LONG_MEMORY, memory.STATUS: memory.MATCHED, memory.REWARD: 2,
             memory.END_TIME: new_time})
        mem2 = self.database.add_memory(
            {memory.MEMORY_DURATION: memory.LONG_MEMORY, memory.STATUS: memory.MATCHING, memory.REWARD: 1,
             memory.END_TIME: new_time})
        mem3 = self.database.add_memory(
            {memory.MEMORY_DURATION: memory.SHORT_MEMORY, memory.STATUS: memory.MATCHED, memory.REWARD: 1,
             memory.END_TIME: new_time})
        memories = [mem1, mem2, mem3]
        memory.threshold_of_working_memories = 2
        working_memories = memory.cleanup_working_memories(memories, reward)
        self.assertEquals(2, len(working_memories))
        self.assertEquals(1, working_memories[0][memory.REWARD])
        self.assertEquals(memory.LONG_MEMORY, working_memories[0][memory.MEMORY_DURATION])
        reward2 = {status.REWARD: False}
        working_memories2 = memory.cleanup_working_memories(memories, reward2)
        self.assertEquals(2, working_memories2[0][memory.REWARD])
        self.assertEquals(memory.LONG_MEMORY, working_memories2[1][memory.MEMORY_DURATION])

    def test_verify_slice_memory_match_result(self):
        fmem1 = self.database.add_memory({memory.STATUS: memory.MATCHED})
        fmem2 = self.database.add_memory({memory.STATUS: memory.MATCHED})
        fmem3 = self.database.add_memory({memory.STATUS: memory.MATCHING})
        smem1 = self.database.add_memory({memory.MEMORY_DURATION: memory.SLICE_MEMORY, memory.STATUS: memory.MATCHING,
                                          memory.CHILD_MEM: [fmem1[memory.ID], fmem2[memory.ID]]})
        smem2 = self.database.add_memory({memory.MEMORY_DURATION: memory.SLICE_MEMORY, memory.STATUS: memory.MATCHING,
                                          memory.CHILD_MEM: [fmem1[memory.ID], fmem3[memory.ID]]})
        slice_memories = [smem1, smem2]
        slice_memory_children = {smem1[memory.ID]: [fmem1, fmem2], smem2[memory.ID]: [fmem1, fmem3]}
        all_matched_feature_memories = memory.verify_slice_memory_match_result(slice_memories, slice_memory_children)
        self.assertEquals(2, len(all_matched_feature_memories))


if __name__ == "__main__":
    unittest.main()
