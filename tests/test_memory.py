import unittest, memory, status, time, copy, constants
from data_service import DataService
from tinydb import TinyDB
from tinydb.storages import MemoryStorage
from db_tinydb import DB_TinyDB


class TestMemory(unittest.TestCase):
    data_service = None
    database = None

    def setUp(self):
        database = DB_TinyDB(TinyDB(storage=MemoryStorage))
        self.data_service = DataService(database)
        memory.forget_memory = False
        memory.data_service = self.data_service

    # test find parent memories
    def test_count_parent_id1(self):
        mem1 = memory.BASIC_MEMORY.copy()
        mem1.update({constants.PARENT_MEM: [5, 6, 7]})
        mem2 = memory.BASIC_MEMORY.copy()
        mem2.update({constants.PARENT_MEM: [6, 7, 8]})
        mem3 = memory.BASIC_MEMORY.copy()
        mem3.update({constants.PARENT_MEM: [7, 8, 9]})
        seq_time_memories = [mem1, mem2, mem3]
        parent_counts = memory.count_parent_id(seq_time_memories)
        self.assertIsNotNone(parent_counts)
        self.assertEqual(1, parent_counts.get(5))
        self.assertEqual(3, parent_counts.get(7))

    # test find parent memories
    def test_count_parent_id2(self):
        mem1 = memory.BASIC_MEMORY.copy()
        mem1.update({constants.PARENT_MEM: [5, 6, 7]})
        mem3 = memory.BASIC_MEMORY.copy()
        mem3.update({constants.PARENT_MEM: [8, 9]})
        seq_time_memories = [mem1, mem3]
        parent_counts = memory.count_parent_id(seq_time_memories)
        self.assertIsNotNone(parent_counts)
        self.assertEqual(1, parent_counts.get(5))
        self.assertEqual(1, parent_counts.get(7))

    def test_find_max_related_memory_success(self):
        mem1 = self.data_service.add_memory()
        mem2 = self.data_service.add_memory({constants.PARENT_MEM: [5, 6, mem1[constants.MID]]})
        mem3 = self.data_service.add_memory({constants.PARENT_MEM: [6, mem1[constants.MID], 8]})
        seq_time_memories = [mem2, mem3]
        memories = memory.find_update_max_related_memories(seq_time_memories)
        self.assertEqual(1, len(memories))
        mem = self.data_service._get_memory(mem2[constants.MID])
        self.assertEqual(mem1[constants.MID], mem[constants.PARENT_MEM][0])

    def test_find_max_related_memory_empty(self):
        mem1 = self.data_service.add_memory({constants.PARENT_MEM: [5, 6, 7]})
        mem2 = self.data_service.add_memory({constants.PARENT_MEM: [6, 7, 8]})
        seq_time_memories = [mem1, mem2]
        memories = memory.find_update_max_related_memories(seq_time_memories)
        self.assertEqual(0, len(memories))

    def test_find_max_related_memory_limit(self):
        mem1 = self.data_service.add_memory()
        mem2 = self.data_service.add_memory()
        mem3 = self.data_service.add_memory({constants.PARENT_MEM: [5, 6, mem1[constants.MID], mem2[constants.MID]]})
        mem4 = self.data_service.add_memory({constants.PARENT_MEM: [6, mem1[constants.MID], mem2[constants.MID], 8]})
        seq_time_memories = [mem3, mem4]
        memories = memory.find_update_max_related_memories(seq_time_memories, 1)
        self.assertEqual(1, len(memories))

    def test_remove_memory_children(self):
        children = [1, 2, 3, 4, 5]
        forgot = [1, 3, 5]
        mem1 = self.data_service.add_memory({constants.CHILD_MEM: children})
        memory.reduce_list_field(constants.CHILD_MEM, children, forgot, mem1[constants.MID])
        mem = self.data_service._get_memory(mem1[constants.MID])
        self.assertEqual(2, len(mem[constants.CHILD_MEM]))
        self.assertEqual(4, mem[constants.CHILD_MEM][1])

    def get_live_sub_memories_empty(self):
        mem1 = self.data_service.add_memory({constants.CHILD_MEM: []})
        memories = memory.get_live_sub_memories(mem1, constants.CHILD_MEM)
        self.assertEqual(0, len(memories))

    def get_live_sub_memories_success(self):
        mem1 = self.data_service.add_memory()
        mem2 = self.data_service.add_memory()
        mem3 = self.data_service.add_memory({constants.CHILD_MEM: [mem1[constants.MID], mem2[constants.MID]]})
        child_memories1 = memory.get_live_sub_memories(mem3, constants.CHILD_MEM)
        self.assertEqual(2, len(child_memories1))

        mem4 = self.data_service.add_memory({constants.CHILD_MEM: [mem1[constants.MID], mem2[constants.MID], 9]})
        child_memories2 = memory.get_live_sub_memories(mem4, constants.CHILD_MEM)
        self.assertEqual(2, len(child_memories2))
        self.assertEqual(mem2[constants.MID], child_memories2[1][constants.MID])

        el5 = self.data_service.add_memory({constants.CHILD_MEM: [mem1[constants.MID], 9, mem2[constants.MID]]})
        child_memories3 = memory.get_live_sub_memories(el5, constants.CHILD_MEM)
        self.assertEqual(2, len(child_memories3))
        self.assertEqual(mem2[constants.MID], child_memories3[1][constants.MID])

        el6 = self.data_service.add_memory({constants.CHILD_MEM: [8, 9]})
        memory.get_live_sub_memories(el6, constants.CHILD_MEM)
        mem = self.data_service._get_memory(el6[constants.MID])
        self.assertIsNone(mem)

    def test_get_memories(self):
        mem1 = self.data_service.add_memory(
            {constants.STATUS: constants.MATCHED, constants.DURATION: 1, constants.REWARD: 0.5})
        mem2 = self.data_service.add_memory(
            {constants.STATUS: constants.MATCHING, constants.DURATION: 1, constants.REWARD: 0.6})
        mem3 = self.data_service.add_memory(
            {constants.STATUS: constants.EXPIRED, constants.DURATION: 3, constants.REWARD: 0.3})
        memories = [mem1, mem2, mem3]
        matched_list = [x for x in memories if x[constants.STATUS] is constants.MATCHED]
        self.assertEqual(1, len(matched_list))
        sorted_list1 = sorted(memories, key=lambda x: (x[constants.DURATION]), reverse=True)
        self.assertEqual(constants.EXPIRED, sorted_list1[0][constants.STATUS])
        sorted_list2 = sorted(memories, key=lambda x: (x[constants.REWARD]), reverse=True)
        self.assertEqual(constants.MATCHING, sorted_list2[0][constants.STATUS])
        sorted_list3 = sorted(memories, key=lambda x: (x[constants.DURATION], x[constants.REWARD]))
        self.assertEqual(constants.MATCHED, sorted_list3[0][constants.STATUS])

    def test_find_max_related_memories(self):
        mem1 = self.data_service.add_memory()
        mem2 = self.data_service.add_memory()
        mem3 = memory.BASIC_MEMORY.copy()
        mem3.update({constants.MID: 3})
        mem4 = memory.BASIC_MEMORY.copy()
        mem4.update({constants.MID: 4})
        mem5 = self.data_service.add_memory(
            {constants.PARENT_MEM: [mem1[constants.MID], mem2[constants.MID], mem3[constants.MID]]})
        mem6 = self.data_service.add_memory(
            {constants.PARENT_MEM: [mem2[constants.MID], mem3[constants.MID], mem4[constants.MID]]})
        memories = [mem5, mem6]
        tobe_remove_list_ids = []
        related_memories = memory.find_max_related_memories(memories, tobe_remove_list_ids)
        self.assertEquals(2, len(related_memories))
        self.assertEquals(2, len(tobe_remove_list_ids))
        mem7 = self.data_service.add_memory(
            {constants.PARENT_MEM: [mem2[constants.MID], mem3[constants.MID], mem4[constants.MID]]})
        memories.append(mem7)
        tobe_remove_list_ids2 = []
        related_memories2 = memory.find_max_related_memories(memories, tobe_remove_list_ids2, 1)
        self.assertEquals(1, len(related_memories2))
        self.assertEquals(mem2[constants.MID], related_memories2[0][constants.MID])

    def test_remove_dead_memories(self):
        child_mem = ['a1', 'b2', 'c3']
        mem1 = self.data_service.add_memory({constants.CHILD_MEM: child_mem})
        forget_ids = ['c3']
        memory.reduce_list_field(constants.CHILD_MEM, child_mem, forget_ids, mem1[constants.MID])
        mem1b = self.data_service._get_memory(mem1[constants.MID])
        forget_ids2 = ['a1', 'b2']
        self.assertEquals(forget_ids2, mem1b[constants.CHILD_MEM])
        memory.reduce_list_field(constants.CHILD_MEM, mem1b[constants.CHILD_MEM], forget_ids2, mem1[constants.MID])
        mem1c = self.data_service._get_memory(mem1[constants.MID])
        self.assertIsNone(mem1c)

    def test_search_sub_memories(self):
        mem1 = self.data_service.add_memory()
        mem2 = self.data_service.add_memory()
        mem3 = self.data_service.add_memory({constants.CHILD_MEM: [mem1[constants.MID], mem2[constants.MID]]})
        mem4 = self.data_service.add_memory()
        mem6 = self.data_service.add_memory({constants.CHILD_MEM: [mem4[constants.MID], mem2[constants.MID]]})
        memories = [mem3, mem6]
        distinct_sub_memory_list = []
        sub_memory_dict = {}
        memory.search_sub_memories(memories, distinct_sub_memory_list, sub_memory_dict)
        self.assertEquals(3, len(distinct_sub_memory_list))
        self.assertEquals(2, len(sub_memory_dict))

    def test_create_working_memory(self):
        working_memories = []
        seq_time_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        mem1 = self.data_service.add_memory({constants.REWARD: 1})
        mem2 = self.data_service.add_memory({constants.REWARD: 2})
        memories = [mem1, mem2]
        memory.create_working_memory(working_memories, seq_time_memories, [memories], constants.SLICE_MEMORY)
        self.assertEquals(2, seq_time_memories[constants.SLICE_MEMORY][0][constants.REWARD])

    def test_append_working_memories(self):
        mem1 = self.data_service.add_memory({constants.MEMORY_DURATION: memory.INSTANT_MEMORY})
        working_memories = []
        new_memories = [mem1]
        memory.append_working_memories(working_memories, new_memories)
        self.assertEquals(1, len(working_memories))
        self.assertGreater(working_memories[0][constants.START_TIME], 0)
        self.assertGreater(working_memories[0][constants.END_TIME], 0)
        self.assertGreater(working_memories[0][constants.LAST_RECALL], 0)
        memory.append_working_memories(working_memories, new_memories)
        self.assertEquals(1, len(working_memories))
        mem2 = self.data_service.add_memory({constants.MEMORY_DURATION: memory.INSTANT_MEMORY})
        mem3 = self.data_service.add_memory({constants.MEMORY_DURATION: memory.INSTANT_MEMORY})
        new_memories2 = [mem2, mem3]
        memory.append_working_memories(working_memories, new_memories2, 1)
        self.assertEquals(2, len(working_memories))

    def test_associate_slice_empty(self):
        memory.threshold_of_working_memories = 3
        mem0 = self.data_service.add_memory({constants.STATUS: constants.MATCHING, constants.END_TIME: 1})
        pmem1 = self.data_service.add_memory(
            {constants.LAST_RECALL: 1, constants.REWARD: 1, constants.MEMORY_DURATION: constants.SLICE_MEMORY})
        pmem2 = self.data_service.add_memory(
            {constants.LAST_RECALL: 2, constants.REWARD: 2, constants.MEMORY_DURATION: constants.SLICE_MEMORY})
        now = time.time() + 100
        mem3 = self.data_service.add_memory(
            {constants.END_TIME: now, constants.STATUS: constants.MATCHED,
             constants.PARENT_MEM: [5, 6, pmem1[constants.MID], pmem2[constants.MID]]})
        mem4 = self.data_service.add_memory(
            {constants.END_TIME: now, constants.STATUS: constants.MATCHED,
             constants.PARENT_MEM: [6, pmem1[constants.MID], pmem2[constants.MID], 8]})
        mem3[constants.LAST_RECALL] = now
        mem4[constants.LAST_RECALL] = now
        memories = [mem0, mem3, mem4]
        working_memories = memory.associate(memories)
        self.assertEqual(3, len(working_memories))
        self.assertEqual(2, working_memories[2][constants.REWARD])

    def test_prepare_expectation(self):
        mem1 = self.data_service.add_memory({constants.MEMORY_DURATION: constants.SLICE_MEMORY})
        mem2 = self.data_service.add_memory({constants.MEMORY_DURATION: constants.SLICE_MEMORY})
        imem1 = self.data_service.add_memory(
            {constants.MEMORY_DURATION: memory.INSTANT_MEMORY, constants.STATUS: constants.MATCHING,
             constants.CHILD_MEM: [5, 6, mem1[constants.MID], mem2[constants.MID]]})
        imem2 = self.data_service.add_memory(
            {constants.MEMORY_DURATION: memory.INSTANT_MEMORY, constants.STATUS: constants.MATCHING})
        smem1 = self.data_service.add_memory(
            {constants.MEMORY_DURATION: memory.SHORT_MEMORY, constants.STATUS: constants.MATCHING,
             constants.CHILD_MEM: [5, 6, imem1[constants.MID], imem2[constants.MID]]})
        working_memories = [imem1, smem1]
        memory.prepare_expectation(working_memories)
        self.assertEquals(4, len(working_memories))

    def test_check_expectation(self):
        new_time = time.time() + 10000
        sequential_time_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        mem1 = self.data_service.add_memory(
            {constants.MEMORY_DURATION: constants.SLICE_MEMORY, constants.STATUS: constants.MATCHED,
             constants.END_TIME: new_time})
        mem2 = self.data_service.add_memory(
            {constants.MEMORY_DURATION: constants.SLICE_MEMORY, constants.STATUS: constants.MATCHED,
             constants.END_TIME: new_time})
        mem3 = self.data_service.add_memory(
            {constants.MEMORY_DURATION: constants.SLICE_MEMORY, constants.STATUS: constants.MATCHING,
             constants.END_TIME: new_time})
        imem1 = self.data_service.add_memory(
            {constants.MEMORY_DURATION: memory.INSTANT_MEMORY, constants.STATUS: constants.MATCHING,
             constants.CHILD_MEM: [5, 6, mem1[constants.MID], mem2[constants.MID]], constants.END_TIME: new_time})
        imem2 = self.data_service.add_memory(
            {constants.MEMORY_DURATION: memory.INSTANT_MEMORY, constants.STATUS: constants.MATCHING,
             constants.CHILD_MEM: [mem3[constants.MID]], constants.END_TIME: new_time})
        smem1 = self.data_service.add_memory(
            {constants.MEMORY_DURATION: memory.SHORT_MEMORY, constants.STATUS: constants.MATCHING,
             constants.CHILD_MEM: [5, 6, imem1[constants.MID], imem2[constants.MID]], constants.END_TIME: new_time})
        smem2 = self.data_service.add_memory(
            {constants.MEMORY_DURATION: memory.SHORT_MEMORY, constants.STATUS: constants.MATCHED,
             constants.END_TIME: new_time})
        smem3 = self.data_service.add_memory(
            {constants.MEMORY_DURATION: memory.SHORT_MEMORY, constants.STATUS: constants.MATCHING,
             constants.END_TIME: 1})
        working_memories = [mem1, mem2, imem1, imem2, smem1, smem2, smem3, mem3]
        memory.check_expectation(working_memories, sequential_time_memories)
        self.assertEquals(constants.MATCHED, imem1[constants.STATUS])
        self.assertEquals(constants.MATCHING, imem2[constants.STATUS])
        self.assertEquals(constants.MATCHING, smem1[constants.STATUS])
        self.assertEquals(constants.EXPIRED, smem3[constants.STATUS])
        self.assertEquals(1, len(sequential_time_memories[memory.INSTANT_MEMORY]))
        matched_memories = [mem for mem in working_memories if mem[constants.STATUS] is constants.MATCHED]
        self.assertEquals(5, len(matched_memories))
        matching_memories = [mem for mem in working_memories if mem[constants.STATUS] is constants.MATCHING]
        self.assertEquals(2, len(matching_memories))
        expired_memories = [mem for mem in working_memories if mem[constants.STATUS] is constants.EXPIRED]
        self.assertEquals(1, len(expired_memories))

    def test_cleanup_working_memories(self):
        new_time = time.time() + 10000
        reward = {constants.REWARD: True}
        mem1 = self.data_service.add_memory(
            {constants.MEMORY_DURATION: memory.LONG_MEMORY, constants.STATUS: constants.MATCHED, constants.REWARD: 2,
             constants.END_TIME: new_time})
        mem2 = self.data_service.add_memory(
            {constants.MEMORY_DURATION: memory.LONG_MEMORY, constants.STATUS: constants.MATCHING, constants.REWARD: 1,
             constants.END_TIME: new_time})
        mem3 = self.data_service.add_memory(
            {constants.MEMORY_DURATION: memory.SHORT_MEMORY, constants.STATUS: constants.MATCHED, constants.REWARD: 1,
             constants.END_TIME: new_time})
        memories = [mem1, mem2, mem3]
        memory.threshold_of_working_memories = 2
        working_memories = memory.cleanup_working_memories(memories, reward)
        self.assertEquals(2, len(working_memories))
        self.assertEquals(1, working_memories[0][constants.REWARD])
        self.assertEquals(memory.LONG_MEMORY, working_memories[0][constants.MEMORY_DURATION])
        reward2 = {constants.REWARD: False}
        working_memories2 = memory.cleanup_working_memories(memories, reward2)
        self.assertEquals(2, working_memories2[0][constants.REWARD])
        self.assertEquals(memory.LONG_MEMORY, working_memories2[1][constants.MEMORY_DURATION])

    def test_verify_slice_memory_match_result(self):
        working_memories = []
        sequential_time_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        fmem1 = self.data_service.add_memory({constants.STATUS: constants.MATCHED})
        fmem2 = self.data_service.add_memory({constants.STATUS: constants.MATCHED})
        fmem3 = self.data_service.add_memory({constants.STATUS: constants.MATCHING})
        smem1 = self.data_service.add_memory(
            {constants.MEMORY_DURATION: constants.SLICE_MEMORY, constants.STATUS: constants.MATCHING,
             constants.CHILD_MEM: [fmem1[constants.MID], fmem2[constants.MID]]})
        smem2 = self.data_service.add_memory(
            {constants.MEMORY_DURATION: constants.SLICE_MEMORY, constants.STATUS: constants.MATCHING,
             constants.CHILD_MEM: [fmem1[constants.MID], fmem3[constants.MID]]})
        slice_memories = [smem1, smem2]
        slice_memory_children = {smem1[constants.MID]: [fmem1, fmem2], smem2[constants.MID]: [fmem1, fmem3]}
        all_matched_feature_memories = memory.verify_slice_memory_match_result(slice_memories, slice_memory_children,
                                                                               working_memories,
                                                                               sequential_time_memories)
        self.assertEquals(2, len(all_matched_feature_memories))

    def test_remove_continuous_duplicate_memory(self):
        mem1 = self.data_service.add_memory()
        self.assertEqual(1, len(memory.remove_duplicate_memory([mem1])))
        self.assertEqual(1, len(memory.remove_duplicate_memory([mem1, mem1])))
        mem2 = self.data_service.add_memory()
        self.assertEqual(2, len(memory.remove_duplicate_memory([mem1, mem2])))
        self.assertEqual(2, len(memory.remove_duplicate_memory([mem1, mem1, mem2, mem2])))
        self.assertEqual(2, len(memory.remove_duplicate_memory([mem1, mem2, mem2, mem2])))
        self.assertEqual(2, len(memory.remove_duplicate_memory([mem1, mem2, mem1, mem2])))

    def test_increase_list_field(self):
        # TODO
        return


if __name__ == "__main__":
    unittest.main()
