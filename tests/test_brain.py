from components.memory import Memory
from components.memory import MemoryStatus
from components.memory import MemoryType
from components.memory import RealType
from components.brain import Brain
from components import brain
from components import memory
from components import util
from tests import test_memory
from unittest.mock import patch
import numpy as np
import time
import unittest


class TestBrain(unittest.TestCase):

    def test_associate_1(self):
        brain1 = Brain()
        memories = test_memory.build_a_tree()
        memories[0].status = MemoryStatus.LIVING
        memories[1].status = MemoryStatus.LIVING
        brain1.memories = memories
        active_memories = {memories[0], memories[1]}
        brain1.active_memories = active_memories
        with patch.object(Memory, 'activate', return_value=None) as mock_method:
            brain1.associate()
        mock_method.assert_called_once_with()
        # print(f'counter:{brain1.counter}')

    def test_associate_2(self):
        brain1 = Brain()
        memories = test_memory.build_a_tree()
        memories[1].status = MemoryStatus.LIVING
        memories[8].parent = set()
        memories[9].parent = set()
        brain1.memories = memories
        active_memories = {memories[0], memories[1]}
        brain1.active_memories = active_memories
        brain1.associate()
        self.assertEqual(4, len(brain1.active_memories))
        self.assertEqual(MemoryStatus.MATCHING, memories[8].status)
        self.assertEqual(MemoryStatus.MATCHING, memories[9].status)

    def test_search_top_parent_1(self):
        brain1 = Brain()
        memories = test_memory.build_a_tree()
        memories[0].status = MemoryStatus.LIVING
        brain1.search_top_parent(memories[0])
        self.assertEqual(1, len(brain1.temp_set1))
        self.assertEqual(MemoryType.LONG, brain1.temp_set1.pop().memory_type)
        # exception case
        brain1.temp_set1.clear()
        memories[10].status = MemoryStatus.DORMANT
        brain1.search_top_parent(memories[0])
        self.assertEqual(0, len(brain1.temp_set1))

    def test_search_top_parent_2(self):
        brain1 = Brain()
        memories = test_memory.build_a_tree()
        memories[1].status = MemoryStatus.LIVING
        memories[8].parent = set()
        memories[9].parent = set()
        brain1.search_top_parent(memories[1])
        self.assertEqual(2, len(brain1.temp_set1))
        # exception case
        brain1.temp_set1.clear()
        memories[4].status = MemoryStatus.DORMANT
        memories[6].status = MemoryStatus.DORMANT
        brain1.search_top_parent(memories[1])
        self.assertEqual(0, len(brain1.temp_set1))

    def test_activate_tree_left_leaf(self):
        memories = test_memory.build_a_tree()
        memories[8].status = MemoryStatus.MATCHING
        brain1 = Brain()
        # 1st validation
        brain1.activate_children_tree(memories[8])
        # brain1.activate_children_tree(memories[8])
        # print(f'counter:{brain1.counter}')
        self.assertEqual(memories[0].status, MemoryStatus.MATCHING)
        self.assertEqual(memories[1].status, MemoryStatus.MATCHING)
        self.assertEqual(memories[2].status, MemoryStatus.MATCHING)
        self.assertEqual(memories[3].status, MemoryStatus.MATCHING)
        self.assertEqual(memories[4].status, MemoryStatus.MATCHING)
        self.assertNotEqual(memories[5].status, MemoryStatus.MATCHING)
        self.assertEqual(memories[6].status, MemoryStatus.MATCHING)
        self.assertNotEqual(memories[7].status, MemoryStatus.MATCHING)
        self.assertEqual(memories[8].status, MemoryStatus.MATCHING)
        # 2nd validation, nothing change
        brain1.temp_set1.clear()
        brain1.activate_children_tree(memories[8])
        self.assertEqual(memories[0].status, MemoryStatus.MATCHING)
        self.assertEqual(memories[1].status, MemoryStatus.MATCHING)
        self.assertEqual(memories[2].status, MemoryStatus.MATCHING)
        self.assertEqual(memories[3].status, MemoryStatus.MATCHING)
        self.assertEqual(memories[4].status, MemoryStatus.MATCHING)
        self.assertNotEqual(memories[5].status, MemoryStatus.MATCHING)
        self.assertEqual(memories[6].status, MemoryStatus.MATCHING)
        self.assertNotEqual(memories[7].status, MemoryStatus.MATCHING)
        self.assertEqual(memories[8].status, MemoryStatus.MATCHING)
        # 3rd validation, something matched
        memories[2].status = MemoryStatus.MATCHED
        brain1.temp_set1.clear()
        brain1.activate_children_tree(memories[8])
        self.assertEqual(memories[3].status, MemoryStatus.MATCHING)
        memories[4].status = MemoryStatus.MATCHED
        brain1.temp_set1.clear()
        brain1.activate_children_tree(memories[8])
        self.assertEqual(memories[5].status, MemoryStatus.MATCHING)

    def test_activate_tree_middle_leaf(self):
        brain1 = Brain()
        memories = test_memory.build_a_tree()
        memories[8].status = MemoryStatus.MATCHING
        memories[9].children = memories[6:8]
        # 1st validation
        brain1.activate_children_tree(memories[10])
        self.assertEqual(memories[9].status, MemoryStatus.SLEEP)
        # match 1st long
        memories[8].status = MemoryStatus.MATCHED
        brain1.temp_set1.clear()
        brain1.activate_children_tree(memories[10])
        self.assertEqual(memories[0].status, MemoryStatus.MATCHING)
        self.assertEqual(memories[1].status, MemoryStatus.MATCHING)
        self.assertEqual(memories[2].status, MemoryStatus.MATCHING)
        self.assertEqual(memories[4].status, MemoryStatus.MATCHING)
        self.assertEqual(memories[6].status, MemoryStatus.MATCHING)
        self.assertEqual(memories[9].status, MemoryStatus.MATCHING)

    def test_match_memories_all(self):
        brain1 = Brain()
        memories = test_memory.build_a_tree(MemoryStatus.MATCHED)
        brain1.active_memories = set(memories)
        brain1.match_memories()
        # print(f'counter:{brain1.counter}')
        for i in range(0, len(memories)):
            self.assertEqual(MemoryStatus.LIVING, memories[i].status)

    def test_match_memories_some_real(self):
        brain1 = Brain()
        memories = test_memory.build_a_tree(MemoryStatus.LIVING)
        for i in range(0, 2):
            memories[i].status = MemoryStatus.MATCHED
        memories[2].status = MemoryStatus.SLEEP
        brain1.active_memories = set(memories)
        brain1.match_memories()
        # print(f'counter:{brain1.counter}')
        for i in range(0, 3):
            self.assertEqual(MemoryStatus.LIVING, memories[i].status)

    def test_match_memories_some_virtual(self):
        brain1 = Brain()
        memories = test_memory.build_a_tree(MemoryStatus.LIVING)
        for i in range(0, 4):
            memories[i].status = MemoryStatus.MATCHED
        memories[4].status = MemoryStatus.SLEEP
        brain1.active_memories = set(memories)
        brain1.match_memories()
        self.assertEqual(MemoryStatus.LIVING, memories[4].status)

    def test_match_memories_not_match(self):
        brain1 = Brain()
        memories = test_memory.build_a_tree(MemoryStatus.LIVING)
        memories[0].matched_time = time.time() - 100
        memories[1].status = MemoryStatus.MATCHED
        memories[2].status = MemoryStatus.MATCHING
        brain1.active_memories = set(memories)
        brain1.match_memories()
        self.assertNotEqual(MemoryStatus.LIVING, memories[2].status)

    def test_match_memories_some_parent(self):
        brain1 = Brain()
        memories = test_memory.build_a_tree(MemoryStatus.LIVING)
        memories[0].status = MemoryStatus.MATCHED
        memories[1].matched_time = time.time() - 100
        memories[3].status = MemoryStatus.MATCHING
        brain1.active_memories = set(memories)
        brain1.match_memories()
        self.assertEqual(MemoryStatus.LIVING, memories[3].status)

    def test_extend_matching_parent(self):
        brain1 = Brain()
        memories = test_memory.build_a_tree(MemoryStatus.MATCHING)
        for i in range(0, len(memories)):
            memories[i].active_end_time = time.time()
        self.assertTrue(memories[10].active_end_time - time.time() < 1)
        brain1.extend_matching_parent(memories[0])
        self.assertTrue(memories[10].active_end_time - time.time() < 1)
        brain1.active_memories = set(memories)
        brain1.temp_set1.clear()
        brain1.extend_matching_parent(memories[0])
        self.assertTrue(memories[10].active_end_time - time.time() > 1)

    def test_find_similar_feature_memories(self):
        brain1 = Brain()
        memories = test_memory.build_a_tree(MemoryStatus.MATCHING)
        memories.append(Memory(MemoryType.REAL, real_type=RealType.VISION_FEATURE, kernel=b'0,-1,-1,1,0,1,1,-1,1',
                               channel='y', feature=np.array([1, 228, 189, 55, 49, 37, 16, 35, 12])))
        memories.append(Memory(MemoryType.REAL, real_type=RealType.VISION_FEATURE, kernel=b'0,-1,-1,1,0,1,1,-1,1',
                               channel='u', feature=np.array([1, 228, 189, 55, 49, 37, 16, 35, 12])))
        brain1.memories = memories
        brain1.reindex()
        em = brain1.find_similar_feature_memories(memories[0])
        self.assertTrue(em)
        em = brain1.find_similar_feature_memories(memories[11])
        self.assertTrue(em)
        em = brain1.find_similar_feature_memories(memories[12])
        self.assertTrue(em)

    def test_put_memory(self):
        brain1 = Brain()
        m1 = Memory(MemoryType.REAL, real_type=RealType.SOUND_FEATURE, kernel=b'0,-1,-1,1,0,1,1,-1,1',
                    feature=np.array([1, 228, 189, 55, 49, 37, 16, 35, 12]))
        m1.reward = 50
        brain1.memories = [m1]
        brain1.reindex()
        m2 = Memory(MemoryType.REAL, real_type=RealType.SOUND_FEATURE, kernel=b'0,-1,-1,1,0,1,1,-1,1',
                    feature=np.array([1, 228, 189, 55, 49, 37, 16, 35, 12]))
        self.assertEqual(0, m2.reward)
        m2 = brain1.put_memory(m2)
        self.assertEqual(50, m2.reward)

    def test_compose_memory(self):
        brain1 = Brain()
        memories = test_memory.build_a_tree(MemoryStatus.MATCHING)
        brain1.memories = set(memories)
        brain1.reindex()
        # existing memory
        m1 = brain1.compose_memory([memories[0], memories[1]], MemoryType.SLICE)
        self.assertEqual(m1, memories[2])
        # compose new memory
        fm = Memory(MemoryType.REAL, real_type=RealType.SOUND_FEATURE, kernel=b'0,-1,-1,1,0,1,1,-1,1',
                    feature=np.array([3, 228, 189, 55, 49, 37, 16, 35, 12]))
        m2 = brain1.compose_memory([memories[0], memories[1], fm], MemoryType.SLICE, RealType.SOUND_FEATURE)
        self.assertNotEqual(m2, memories[2])

    def test_compose_memories(self):
        brain1 = Brain()
        memories = test_memory.build_a_tree(MemoryStatus.MATCHED)
        brain1.memories = set(memories)
        brain1.active_memories = set(memories)
        brain1.put_memory(Memory(MemoryType.REAL, real_type=RealType.VISION_FEATURE, kernel=b'0,-1,-1,1,0,1,1,-1,1',
                                 channel='y', feature=np.array([1, 228, 189, 55, 49, 37, 16, 35, 12])))
        brain1.put_memory(Memory(MemoryType.REAL, real_type=RealType.VISION_FEATURE, kernel=b'0,-1,-1,1,0,1,1,-1,1',
                                 channel='u', feature=np.array([1, 228, 189, 55, 49, 37, 16, 35, 12])))
        brain1.compose_memories()
        self.assertEqual(len(memories) + 2 + 4, len(brain1.active_memories))

    def test_get_valid_work_memories(self):
        brain1 = Brain()
        memories = test_memory.build_a_tree(MemoryStatus.LIVING)
        for i in range(0, len(memories)):
            brain1.put_memory(memories[i])
        self.assertEqual(2, len(brain1.get_valid_work_memories(MemoryType.REAL, RealType.SOUND_FEATURE)))
        self.assertEqual(0, len(brain1.get_valid_work_memories(MemoryType.REAL, RealType.VISION_FEATURE)))
        self.assertEqual(2, len(brain1.get_valid_work_memories(MemoryType.SLICE, -1)))
        self.assertEqual(2, len(brain1.get_valid_work_memories(MemoryType.INSTANT, -1)))
        self.assertEqual(2, len(brain1.get_valid_work_memories(MemoryType.SHORT, -1)))
        self.assertEqual(3, len(brain1.get_valid_work_memories(MemoryType.LONG, -1)))

    def test_cleanup_active_memories(self):
        brain1 = Brain()
        memories = test_memory.build_a_tree()
        for m in memories:
            m.activate()
        brain1.active_memories = memories
        brain1.ACTIVE_LONG_MEMORY_LIMIT = 2
        brain1.cleanup_active_memories()
        self.assertEqual(11, len(brain1.active_memories))
        memories[0].deactivate()
        brain1.cleanup_active_memories()
        self.assertEqual(10, len(brain1.active_memories))
        memories[1].active_end_time = time.time() - 1
        brain1.cleanup_active_memories()
        self.assertEqual(9, len(brain1.active_memories))

    def test_cleanup_memories(self):
        brain1 = Brain()
        memories = test_memory.build_a_tree(MemoryStatus.SLEEP)
        brain1.memories = set(memories)
        brain1.cleanup_memories()
        self.assertEqual(11, len(brain1.memories))
        memories[0].status = MemoryStatus.MATCHING
        memories[1].status = MemoryStatus.MATCHING
        brain.MEMORIES_CLEANUP_NUM = 3
        brain.MEMORIES_NUM = 2
        brain1.cleanup_memories()
        self.assertEqual(2, len(brain1.memories))
        self.assertEqual(MemoryType.REAL, brain1.memories.pop().memory_type)

        # for m in memories:
        #     m.last_recall_time = time.time() - 1
        # memories[0].last_recall_time = time.time() - 65000000
        # brain1.memories = set(memories)
        # brain1.cleanup_memories()
        # self.assertEqual(6, len(brain1.memories))

    # def test_persist_memories(self):
    #     brain1 = Brain()
    #     memories = test_memory.build_a_tree()
    #     brain1.memories = set(memories)
    #     brain1.active_memories = memories
    #     brain1.save()
    #     memory.id_sequence = 0
    #     brain2 = Brain()
    #     brain2.load()
    #     self.assertTrue(isinstance(brain2.memories, set))
    #     self.assertEqual(7, len(brain2.memories))
    #     m2 = util.get_from_set(brain2.memories, 3)
    #     self.assertEqual(2, len(m2.children))
    #     self.assertEqual(len(memories), memory.id_sequence)
    #


if __name__ == "__main__":
    unittest.main()
