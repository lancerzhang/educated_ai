from components.bio_memory import BioMemory
from components.data_adaptor import DataAdaptor
from tinydb import TinyDB
from tinydb.storages import MemoryStorage
from components.data_tinydb import DataTinyDB
from components import constants
import copy
import time
import unittest


class TestBioMemory(unittest.TestCase):

    def setUp(self):
        database = DataTinyDB(TinyDB(storage=MemoryStorage))
        da = DataAdaptor(database)
        bm = BioMemory(da)
        bm.forget_memory = False
        self.bio_memory = bm
        self.data_adaptor = da

    # test find parent memories
    def test_count_parent_id1(self):
        mem1 = self.bio_memory.BASIC_MEMORY.copy()
        mem1.update({constants.PARENT_MEM: [5, 6, 7]})
        mem2 = self.bio_memory.BASIC_MEMORY.copy()
        mem2.update({constants.PARENT_MEM: [6, 7, 8]})
        mem3 = self.bio_memory.BASIC_MEMORY.copy()
        mem3.update({constants.PARENT_MEM: [7, 8, 9]})
        seq_time_memories = [mem1, mem2, mem3]
        parent_counts = self.bio_memory.count_parent_id(seq_time_memories)
        self.assertIsNotNone(parent_counts)
        self.assertEqual(1, parent_counts.get(5))
        self.assertEqual(3, parent_counts.get(7))

    # test find parent memories
    def test_count_parent_id2(self):
        mem1 = self.bio_memory.BASIC_MEMORY.copy()
        mem1.update({constants.PARENT_MEM: [5, 6, 7]})
        mem3 = self.bio_memory.BASIC_MEMORY.copy()
        mem3.update({constants.PARENT_MEM: [8, 9]})
        seq_time_memories = [mem1, mem3]
        parent_counts = self.bio_memory.count_parent_id(seq_time_memories)
        self.assertIsNotNone(parent_counts)
        self.assertEqual(1, parent_counts.get(5))
        self.assertEqual(1, parent_counts.get(7))

    def test_find_max_related_memory_success(self):
        mem1 = self.data_adaptor.add_memory()
        mem2 = self.data_adaptor.add_memory({constants.PARENT_MEM: [5, 6, mem1[constants.MID]]})
        mem3 = self.data_adaptor.add_memory({constants.PARENT_MEM: [6, mem1[constants.MID], 8]})
        seq_time_memories = [mem2, mem3]
        memories = self.bio_memory.find_update_max_related_memories(seq_time_memories)
        self.assertEqual(1, len(memories))
        mem = self.data_adaptor._get_memory(mem2[constants.MID])
        self.assertEqual(mem1[constants.MID], mem[constants.PARENT_MEM][0])

    def test_find_max_related_memory_empty(self):
        mem1 = self.data_adaptor.add_memory({constants.PARENT_MEM: [5, 6, 7]})
        mem2 = self.data_adaptor.add_memory({constants.PARENT_MEM: [6, 7, 8]})
        seq_time_memories = [mem1, mem2]
        memories = self.bio_memory.find_update_max_related_memories(seq_time_memories)
        self.assertEqual(0, len(memories))

    def test_find_max_related_memory_limit(self):
        mem1 = self.data_adaptor.add_memory()
        mem2 = self.data_adaptor.add_memory()
        mem3 = self.data_adaptor.add_memory({constants.PARENT_MEM: [5, 6, mem1[constants.MID], mem2[constants.MID]]})
        mem4 = self.data_adaptor.add_memory({constants.PARENT_MEM: [6, mem1[constants.MID], mem2[constants.MID], 8]})
        seq_time_memories = [mem3, mem4]
        memories = self.bio_memory.find_update_max_related_memories(seq_time_memories, 1)
        self.assertEqual(1, len(memories))

    def test_remove_memory_children(self):
        children = [1, 2, 3, 4, 5]
        forgot = [1, 3, 5]
        mem1 = self.data_adaptor.add_memory({constants.CHILD_MEM: children})
        self.bio_memory.reduce_list_field(constants.CHILD_MEM, children, forgot, mem1[constants.MID])
        mem = self.data_adaptor._get_memory(mem1[constants.MID])
        self.assertEqual(2, len(mem[constants.CHILD_MEM]))
        self.assertEqual(4, mem[constants.CHILD_MEM][1])

    def test_search_live_child_memories_empty(self):
        mem1 = self.data_adaptor.add_memory({constants.CHILD_MEM: []})
        memories = self.bio_memory.search_live_child_memories(mem1)
        self.assertEqual(0, len(memories))

    def test_search_live_child_memories_success(self):
        mem1 = self.data_adaptor.add_memory()
        mem2 = self.data_adaptor.add_memory()
        mem3 = self.data_adaptor.add_memory({constants.CHILD_MEM: [mem1[constants.MID], mem2[constants.MID]]})
        child_memories1 = self.bio_memory.search_live_child_memories(mem3)
        self.assertEqual(2, len(child_memories1))

        mem4 = self.data_adaptor.add_memory({constants.CHILD_MEM: [mem1[constants.MID], mem2[constants.MID], 9]})
        child_memories2 = self.bio_memory.search_live_child_memories(mem4)
        self.assertEqual(2, len(child_memories2))
        self.assertEqual(mem2[constants.MID], child_memories2[1][constants.MID])

        el5 = self.data_adaptor.add_memory({constants.CHILD_MEM: [mem1[constants.MID], 9, mem2[constants.MID]]})
        child_memories3 = self.bio_memory.search_live_child_memories(el5)
        self.assertEqual(2, len(child_memories3))
        self.assertEqual(mem2[constants.MID], child_memories3[1][constants.MID])

        el6 = self.data_adaptor.add_memory({constants.CHILD_MEM: [8, 9]})
        self.bio_memory.search_live_child_memories(el6)
        mem = self.data_adaptor._get_memory(el6[constants.MID])
        self.assertIsNone(mem)

    def test_get_memories(self):
        mem1 = self.data_adaptor.add_memory(
            {constants.STATUS: constants.MATCHED, constants.MOVE_DURATION: 1, constants.REWARD: 0.5})
        mem2 = self.data_adaptor.add_memory(
            {constants.STATUS: constants.MATCHING, constants.MOVE_DURATION: 1, constants.REWARD: 0.6})
        mem3 = self.data_adaptor.add_memory(
            {constants.STATUS: constants.EXPIRED, constants.MOVE_DURATION: 3, constants.REWARD: 0.3})
        memories = [mem1, mem2, mem3]
        matched_list = [x for x in memories if x[constants.STATUS] is constants.MATCHED]
        self.assertEqual(1, len(matched_list))
        sorted_list1 = sorted(memories, key=lambda x: (x[constants.MOVE_DURATION]), reverse=True)
        self.assertEqual(constants.EXPIRED, sorted_list1[0][constants.STATUS])
        sorted_list2 = sorted(memories, key=lambda x: (x[constants.REWARD]), reverse=True)
        self.assertEqual(constants.MATCHING, sorted_list2[0][constants.STATUS])
        sorted_list3 = sorted(memories, key=lambda x: (x[constants.MOVE_DURATION], x[constants.REWARD]))
        self.assertEqual(constants.MATCHED, sorted_list3[0][constants.STATUS])

    def test_find_max_related_memories(self):
        mem1 = self.data_adaptor.add_memory()
        mem2 = self.data_adaptor.add_memory()
        mem3 = self.bio_memory.BASIC_MEMORY.copy()
        mem3.update({constants.MID: 3})
        mem4 = self.bio_memory.BASIC_MEMORY.copy()
        mem4.update({constants.MID: 4})
        mem5 = self.data_adaptor.add_memory(
            {constants.PARENT_MEM: [mem1[constants.MID], mem2[constants.MID], mem3[constants.MID]]})
        mem6 = self.data_adaptor.add_memory(
            {constants.PARENT_MEM: [mem2[constants.MID], mem3[constants.MID], mem4[constants.MID]]})
        memories = [mem5, mem6]
        tobe_remove_list_ids = []
        related_memories = self.bio_memory.find_max_related_memories(memories, tobe_remove_list_ids)
        self.assertEquals(2, len(related_memories))
        self.assertEquals(2, len(tobe_remove_list_ids))
        mem7 = self.data_adaptor.add_memory(
            {constants.PARENT_MEM: [mem2[constants.MID], mem3[constants.MID], mem4[constants.MID]]})
        memories.append(mem7)
        tobe_remove_list_ids2 = []
        related_memories2 = self.bio_memory.find_max_related_memories(memories, tobe_remove_list_ids2, 1)
        self.assertEquals(1, len(related_memories2))
        self.assertEquals(mem2[constants.MID], related_memories2[0][constants.MID])

    def test_remove_dead_memories(self):
        child_mem = ['a1', 'b2', 'c3']
        mem1 = self.data_adaptor.add_memory({constants.CHILD_MEM: child_mem})
        forget_ids = ['c3']
        self.bio_memory.reduce_list_field(constants.CHILD_MEM, child_mem, forget_ids, mem1[constants.MID])
        mem1b = self.data_adaptor._get_memory(mem1[constants.MID])
        forget_ids2 = ['a1', 'b2']
        self.assertEquals(forget_ids2, mem1b[constants.CHILD_MEM])
        self.bio_memory.reduce_list_field(constants.CHILD_MEM, mem1b[constants.CHILD_MEM], forget_ids2,
                                          mem1[constants.MID])
        mem1c = self.data_adaptor._get_memory(mem1[constants.MID])
        self.assertIsNone(mem1c)

    def test_create_working_memory(self):
        mem1 = self.data_adaptor.add_memory({constants.REWARD: 1})
        mem2 = self.data_adaptor.add_memory({constants.REWARD: 3})
        memories = [mem1, mem2]
        self.bio_memory.working_memories = memories
        self.bio_memory.add_collection_memories([memories], constants.SLICE_MEMORY)
        self.assertEquals(2, self.bio_memory.temp_memories[constants.SLICE_MEMORY][0][constants.REWARD])

    def test_append_working_memories(self):
        mem1 = self.data_adaptor.add_memory({constants.VIRTUAL_MEMORY_TYPE: constants.INSTANT_MEMORY})
        working_memories = []
        new_memories = [mem1]
        self.bio_memory.new_working_memories(working_memories, new_memories)
        self.assertEquals(1, len(working_memories))
        self.assertGreater(working_memories[0][constants.START_TIME], 0)
        self.assertGreater(working_memories[0][constants.END_TIME], 0)
        self.assertGreater(working_memories[0][constants.LAST_RECALL_TIME], 0)
        self.bio_memory.new_working_memories(working_memories, new_memories)
        self.assertEquals(1, len(working_memories))
        mem2 = self.data_adaptor.add_memory({constants.VIRTUAL_MEMORY_TYPE: constants.INSTANT_MEMORY})
        mem3 = self.data_adaptor.add_memory({constants.VIRTUAL_MEMORY_TYPE: constants.INSTANT_MEMORY})
        new_memories2 = [mem2, mem3]
        self.bio_memory.new_working_memories(working_memories, new_memories2, 1)
        self.assertEquals(2, len(working_memories))

    def test_associate_slice_empty(self):
        mem0 = self.data_adaptor.add_memory({constants.STATUS: constants.MATCHING, constants.END_TIME: 1})
        pmem1 = self.data_adaptor.add_memory(
            {constants.LAST_RECALL_TIME: 1, constants.REWARD: 1, constants.VIRTUAL_MEMORY_TYPE: constants.SLICE_MEMORY})
        pmem2 = self.data_adaptor.add_memory(
            {constants.LAST_RECALL_TIME: 2, constants.REWARD: 2, constants.VIRTUAL_MEMORY_TYPE: constants.SLICE_MEMORY})
        now = time.time() + 100
        mem3 = self.data_adaptor.add_memory(
            {constants.END_TIME: now, constants.STATUS: constants.MATCHED,
             constants.PARENT_MEM: [5, 6, pmem1[constants.MID], 7]})
        mem4 = self.data_adaptor.add_memory(
            {constants.END_TIME: now, constants.STATUS: constants.MATCHING,
             constants.PARENT_MEM: [6, 7, pmem2[constants.MID], 8]})
        mem3[constants.LAST_RECALL_TIME] = now
        mem4[constants.LAST_RECALL_TIME] = now
        wm = [mem0, mem3, mem4]
        self.bio_memory.working_memories = wm
        self.bio_memory.associate()
        self.assertEqual(4, len(wm))

    def test_prepare_matching_virtual_memories(self):
        mem1 = self.data_adaptor.add_memory({constants.VIRTUAL_MEMORY_TYPE: constants.SLICE_MEMORY})
        mem2 = self.data_adaptor.add_memory({constants.VIRTUAL_MEMORY_TYPE: constants.SLICE_MEMORY})
        imem1 = self.data_adaptor.add_memory(
            {constants.VIRTUAL_MEMORY_TYPE: constants.INSTANT_MEMORY, constants.STATUS: constants.MATCHING,
             constants.CHILD_MEM: [5, 6, mem1[constants.MID], mem2[constants.MID]]})
        imem2 = self.data_adaptor.add_memory(
            {constants.VIRTUAL_MEMORY_TYPE: constants.INSTANT_MEMORY, constants.STATUS: constants.MATCHING})
        smem1 = self.data_adaptor.add_memory(
            {constants.VIRTUAL_MEMORY_TYPE: constants.SHORT_MEMORY, constants.STATUS: constants.MATCHING,
             constants.CHILD_MEM: [5, 6, imem1[constants.MID], imem2[constants.MID]]})
        wm = [imem1, smem1]
        self.bio_memory.working_memories = wm
        self.bio_memory.prepare_matching_virtual_memories()
        self.assertEquals(4, len(self.bio_memory.working_memories))

    def test_check_matching_virtual_memories(self):
        new_time = time.time() + 10000
        mem1 = self.data_adaptor.add_memory(
            {constants.VIRTUAL_MEMORY_TYPE: constants.SLICE_MEMORY, constants.STATUS: constants.MATCHED,
             constants.END_TIME: new_time})
        mem2 = self.data_adaptor.add_memory(
            {constants.VIRTUAL_MEMORY_TYPE: constants.SLICE_MEMORY, constants.STATUS: constants.MATCHED,
             constants.END_TIME: new_time})
        mem3 = self.data_adaptor.add_memory(
            {constants.VIRTUAL_MEMORY_TYPE: constants.SLICE_MEMORY, constants.STATUS: constants.MATCHING,
             constants.END_TIME: new_time})
        imem1 = self.data_adaptor.add_memory(
            {constants.VIRTUAL_MEMORY_TYPE: constants.INSTANT_MEMORY, constants.STATUS: constants.MATCHING,
             constants.CHILD_MEM: [5, 6, mem1[constants.MID], mem2[constants.MID]], constants.END_TIME: new_time})
        imem2 = self.data_adaptor.add_memory(
            {constants.VIRTUAL_MEMORY_TYPE: constants.INSTANT_MEMORY, constants.STATUS: constants.MATCHING,
             constants.CHILD_MEM: [mem3[constants.MID]], constants.END_TIME: new_time})
        smem1 = self.data_adaptor.add_memory(
            {constants.VIRTUAL_MEMORY_TYPE: constants.SHORT_MEMORY, constants.STATUS: constants.MATCHING,
             constants.CHILD_MEM: [6, 7, imem1[constants.MID], imem2[constants.MID]], constants.END_TIME: new_time})
        smem2 = self.data_adaptor.add_memory(
            {constants.VIRTUAL_MEMORY_TYPE: constants.SHORT_MEMORY, constants.STATUS: constants.MATCHED,
             constants.END_TIME: new_time})
        smem3 = self.data_adaptor.add_memory(
            {constants.VIRTUAL_MEMORY_TYPE: constants.SHORT_MEMORY, constants.STATUS: constants.MATCHING,
             constants.END_TIME: 1})
        wm = [mem1, mem2, mem3, imem1, imem2, smem1, smem2, smem3]
        self.bio_memory.working_memories = wm
        self.bio_memory.check_matching_virtual_memories()
        self.assertEquals(constants.MATCHED, imem1[constants.STATUS])
        self.assertEquals(constants.MATCHING, imem2[constants.STATUS])
        self.assertEquals(constants.MATCHING, smem1[constants.STATUS])
        self.assertEquals(constants.EXPIRED, smem3[constants.STATUS])
        self.assertEquals(1, len(self.bio_memory.temp_memories[constants.INSTANT_MEMORY]))
        matched_memories = [mem for mem in wm if mem[constants.STATUS] is constants.MATCHED]
        self.assertEquals(4, len(matched_memories))
        matching_memories = [mem for mem in wm if mem[constants.STATUS] is constants.MATCHING]
        self.assertEquals(3, len(matching_memories))
        expired_memories = [mem for mem in wm if mem[constants.STATUS] is constants.EXPIRED]
        self.assertEquals(1, len(expired_memories))

    def test_cleanup_working_memories(self):
        new_time = time.time() + 10000
        now_time = time.time()
        mem1 = self.data_adaptor.add_memory(
            {constants.VIRTUAL_MEMORY_TYPE: constants.INSTANT_MEMORY, constants.STATUS: constants.MATCHED,
             constants.REWARD: 50,
             constants.END_TIME: new_time, constants.LAST_ACTIVE_TIME: now_time})
        mem2 = self.data_adaptor.add_memory(
            {constants.VIRTUAL_MEMORY_TYPE: constants.LONG_MEMORY, constants.STATUS: constants.MATCHING,
             constants.REWARD: 40,
             constants.END_TIME: new_time, constants.LAST_ACTIVE_TIME: now_time - 10})
        mem3 = self.data_adaptor.add_memory(
            {constants.VIRTUAL_MEMORY_TYPE: constants.SHORT_MEMORY, constants.STATUS: constants.MATCHED,
             constants.REWARD: 40,
             constants.END_TIME: new_time, constants.LAST_ACTIVE_TIME: now_time - 5})
        mem4 = self.data_adaptor.add_memory(
            {constants.VIRTUAL_MEMORY_TYPE: constants.SHORT_MEMORY, constants.STATUS: constants.MATCHING,
             constants.REWARD: 40,
             constants.END_TIME: now_time - 5, constants.LAST_ACTIVE_TIME: now_time - 5})
        self.bio_memory.THRESHOLD_OF_WORKING_MEMORIES = 2
        memories = [mem1, mem2, mem3, mem4]
        self.bio_memory.working_memories = memories
        self.bio_memory.cleanup_working_memories()
        self.assertEquals(2, len(self.bio_memory.working_memories))
        self.assertEquals(constants.INSTANT_MEMORY, self.bio_memory.working_memories[0][constants.VIRTUAL_MEMORY_TYPE])
        self.assertEquals(constants.LONG_MEMORY, self.bio_memory.working_memories[1][constants.VIRTUAL_MEMORY_TYPE])
        self.bio_memory.THRESHOLD_OF_WORKING_MEMORIES = 4
        memories2 = [mem1, mem2, mem3, mem4]
        self.bio_memory.working_memories = memories2
        self.bio_memory.cleanup_working_memories()
        self.assertEquals(3, len(self.bio_memory.working_memories))

    def test_verify_matching_physical_memories(self):
        fmem1 = self.data_adaptor.add_memory({constants.STATUS: constants.MATCHED})
        fmem2 = self.data_adaptor.add_memory({constants.STATUS: constants.MATCHED})
        fmem3 = self.data_adaptor.add_memory({constants.STATUS: constants.MATCHING})
        smem1 = self.data_adaptor.add_memory(
            {constants.VIRTUAL_MEMORY_TYPE: constants.SLICE_MEMORY, constants.STATUS: constants.MATCHING,
             constants.CHILD_MEM: [fmem1[constants.MID], fmem2[constants.MID]]})
        smem2 = self.data_adaptor.add_memory(
            {constants.VIRTUAL_MEMORY_TYPE: constants.SLICE_MEMORY, constants.STATUS: constants.MATCHING,
             constants.CHILD_MEM: [fmem1[constants.MID], fmem3[constants.MID]]})
        slice_memories = [smem1, smem2]
        slice_memory_children = {smem1[constants.MID]: [fmem1, fmem2], smem2[constants.MID]: [fmem1, fmem3]}
        self.bio_memory.matching_memories = slice_memories
        self.bio_memory.matching_child_memories = slice_memory_children
        self.bio_memory.verify_matching_physical_memories()
        self.assertEquals(2, len(self.bio_memory.matched_memories))

    def test_remove_continuous_duplicate_memory(self):
        mem1 = self.data_adaptor.add_memory()
        self.assertEqual(1, len(self.bio_memory.remove_duplicate_memory([mem1])))
        self.assertEqual(1, len(self.bio_memory.remove_duplicate_memory([mem1, mem1])))
        mem2 = self.data_adaptor.add_memory()
        self.assertEqual(2, len(self.bio_memory.remove_duplicate_memory([mem1, mem2])))
        self.assertEqual(2, len(self.bio_memory.remove_duplicate_memory([mem1, mem1, mem2, mem2])))
        self.assertEqual(2, len(self.bio_memory.remove_duplicate_memory([mem1, mem2, mem2, mem2])))
        self.assertEqual(2, len(self.bio_memory.remove_duplicate_memory([mem1, mem2, mem1, mem2])))

    def test_increase_list_field(self):
        # TODO
        return

    def test_activate_parent_memories(self):
        # TODO
        return


if __name__ == "__main__":
    unittest.main()