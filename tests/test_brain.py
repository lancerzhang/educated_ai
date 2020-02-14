from components.memory import Memory
from components.brain import Brain
from components import constants
from components import memory
from components import util
from tests import test_memory
import time
import unittest


class TestBrain(unittest.TestCase):

    def setUp(self):
        memory.id_sequence = 0

    def test_associate_active_memories(self):
        # normal case
        brain = Brain()
        memories = test_memory.build_a_tree()
        memories[0].status = constants.MATCHED
        brain.memories = memories
        active_memories = {memories[0]}
        brain.active_memories = active_memories
        brain.associate()
        self.assertEqual(constants.MATCHING, memories[10].status)

    def test_match_virtual_memories(self):
        brain = Brain()
        # match one
        memories = test_memory.build_a_tree(constants.MATCHING)
        brain.active_memories = set(memories)
        for i in range(0, 2):
            memories[i].status = constants.MATCHED
        brain.match_memories()
        self.assertEqual(memories[2].status, constants.MATCHED)
        # match whole tree
        memories = test_memory.build_a_tree(constants.MATCHING)
        brain.active_memories = set(memories)
        memories[3].status = constants.MATCHED
        memories[5].status = constants.MATCHED
        memories[7].status = constants.MATCHED
        memories[9].status = constants.MATCHED
        for i in range(0, 2):
            memories[i].status = constants.MATCHED
        brain.match_memories()
        self.assertEqual(memories[10].status, constants.MATCHED)

    def test_compose_memory(self):
        brain = Brain()
        memories = test_memory.build_a_tree(constants.MATCHING)
        brain.memories = set(memories)
        brain.reindex()
        # existing memory
        m1 = brain.compose_memory([memories[0], memories[1]], memory.MEMORY_TYPES.index(constants.SLICE_MEMORY))
        self.assertEqual(2, len(m1.children))
        self.assertEqual(3, m1.mid)
        self.assertEqual(1, len(brain.active_memories))
        self.assertEqual(constants.MATCHED, m1.status)
        fm = memory.create()
        fm.memory_type = memory.MEMORY_TYPES.index(constants.FEATURE_MEMORY)
        fm.reward = 1
        # compose new memory
        m2 = brain.compose_memory([memories[0], memories[1], fm], memory.MEMORY_TYPES.index(constants.SLICE_MEMORY),
                                  memory.MEMORY_FEATURES.index(constants.SOUND_FEATURE))
        self.assertEqual(3, len(m2.children))
        self.assertEqual(13, m2.mid)
        self.assertEqual(0.9, m2.reward)
        self.assertEqual(constants.MATCHED, m2.status)
        self.assertEqual(memory.MEMORY_FEATURES.index(constants.SOUND_FEATURE), m2.feature_type)

    def test_compose_active_memories(self):
        brain = Brain()
        memories = test_memory.build_a_tree(constants.MATCHED)
        memories[0].feature_type = memory.MEMORY_FEATURES.index(constants.SOUND_FEATURE)
        memories[1].feature_type = memory.MEMORY_FEATURES.index(constants.SOUND_FEATURE)
        memories[1].status = constants.MATCHING
        for _ in range(0, 3):
            m = memory.create()
            m.status = constants.MATCHED
            m.memory_type = memory.MEMORY_TYPES.index(constants.FEATURE_MEMORY)
            m.feature_type = memory.MEMORY_FEATURES.index(constants.VISION_FEATURE)
            memories.append(m)
        memories[-1].matched_time = time.time() - 1
        brain.active_memories = set(memories)
        for m in memories:
            if m.memory_type == 0:
                brain.work_memories[m.memory_type][m.feature_type].append(m)
            else:
                brain.work_memories[m.memory_type].append(m)
        brain.compose_memories()
        self.assertEqual(20, len(brain.active_memories))

    def test_cleanup_active_memories(self):
        brain = Brain()
        memories = test_memory.build_a_tree()
        for m in memories:
            m.activate()
        brain.active_memories = memories
        brain.ACTIVE_LONG_MEMORY_LIMIT = 2
        brain.cleanup_active_memories()
        self.assertEqual(10, len(brain.active_memories))
        memories[0].kill()
        brain.cleanup_active_memories()
        self.assertEqual(9, len(brain.active_memories))
        memories[1].active_end_time = time.time() - 1
        brain.cleanup_active_memories()
        self.assertEqual(8, len(brain.active_memories))

    def test_cleanup_memories(self):
        brain = Brain()
        memories = test_memory.build_a_tree()
        for m in memories:
            m.last_recall_time = time.time() - 1
        memories[0].last_recall_time = time.time() - 65000000
        brain.memories = set(memories)
        brain.cleanup_memories()
        self.assertEqual(6, len(brain.memories))

    def test_persist_memories(self):
        brain = Brain()
        memories = test_memory.build_a_tree()
        brain.memories = set(memories)
        brain.active_memories = memories
        brain.save()
        memory.id_sequence = 0
        brain2 = Brain()
        brain2.load()
        self.assertTrue(isinstance(brain2.memories, set))
        self.assertEqual(7, len(brain2.memories))
        m2 = util.get_from_set(brain2.memories, 3)
        self.assertEqual(2, len(m2.children))
        self.assertEqual(len(memories), memory.id_sequence)

    def test_activate_parent(self):
        brain = Brain()
        memories = test_memory.build_a_tree()
        brain.memories = set(memories)
        brain.active_memories = memories
        brain.extend_matching_parent(memories[0])
        self.assertTrue(memories[2].active_end_time > 0)
        self.assertTrue(memories[4].active_end_time > 0)
        self.assertTrue(memories[6].active_end_time > 0)
        self.assertTrue(memories[8].active_end_time > 0)
        self.assertTrue(memories[10].active_end_time > 0)

    def test_activate_tree_left_leaf(self):
        memories = test_memory.build_a_tree()
        brain = Brain()
        # 1st validation
        brain.activate_children_tree(memories[8])
        self.assertEqual(memories[0].status, constants.MATCHING)
        self.assertEqual(memories[1].status, constants.MATCHING)
        self.assertEqual(memories[2].status, constants.MATCHING)
        self.assertNotEqual(memories[3].status, constants.MATCHING)
        self.assertEqual(memories[4].status, constants.MATCHING)
        self.assertNotEqual(memories[5].status, constants.MATCHING)
        self.assertEqual(memories[6].status, constants.MATCHING)
        self.assertNotEqual(memories[7].status, constants.MATCHING)
        self.assertEqual(memories[8].status, constants.MATCHING)
        # 2nd validation, nothing change
        brain.activate_children_tree(memories[8])
        self.assertEqual(memories[0].status, constants.MATCHING)
        self.assertEqual(memories[1].status, constants.MATCHING)
        self.assertEqual(memories[2].status, constants.MATCHING)
        self.assertNotEqual(memories[3].status, constants.MATCHING)
        self.assertEqual(memories[4].status, constants.MATCHING)
        self.assertNotEqual(memories[5].status, constants.MATCHING)
        self.assertEqual(memories[6].status, constants.MATCHING)
        self.assertNotEqual(memories[7].status, constants.MATCHING)
        self.assertEqual(memories[8].status, constants.MATCHING)
        # 3rd validation, something matched
        memories[2].status = constants.MATCHED
        brain.activate_children_tree(memories[8])
        self.assertEqual(memories[3].status, constants.MATCHING)
        memories[4].status = constants.MATCHED
        brain.activate_children_tree(memories[8])
        self.assertEqual(memories[5].status, constants.MATCHING)

    def test_activate_tree_middle_leaf(self):
        brain = Brain()
        memories = test_memory.build_a_tree()
        memories[8].status = constants.MATCHING
        memories[9].children = memories[6:8]
        # 1st validation
        brain.activate_children_tree(memories[10])
        self.assertEqual(memories[9].status, constants.DORMANT)
        # match 1st long
        memories[8].status = constants.MATCHED
        brain.activate_children_tree(memories[10])
        self.assertEqual(memories[0].status, constants.MATCHING)
        self.assertEqual(memories[1].status, constants.MATCHING)
        self.assertEqual(memories[2].status, constants.MATCHING)
        self.assertEqual(memories[4].status, constants.MATCHING)
        self.assertEqual(memories[6].status, constants.MATCHING)
        self.assertEqual(memories[9].status, constants.MATCHING)


if __name__ == "__main__":
    unittest.main()
