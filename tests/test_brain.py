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

    def test_associate_active_memories_normal(self):
        # normal case
        brain = Brain()
        memories = []
        for x in range(0, 4):
            m = memory.create()
            m.set_memory_type(constants.LONG_MEMORY)
            m.status = constants.MATCHED
            m.parent = set(memories)
            memories.append(m)
        brain.active_memories = memories[1:]
        brain.associate()
        self.assertEqual(4, len(brain.active_memories))
        # dead case
        brain.active_memories = memories[1:]
        memories[0].live = False
        brain.associate()
        self.assertEqual(3, len(brain.active_memories))
        # duplicated case
        brain.active_memories = memories
        memories[0].live = True
        brain.associate()
        self.assertEqual(4, len(brain.active_memories))
        # base case
        brain.active_memories = memories[2:]
        memories[0].matched_time = time.time()
        memories[1].matched_time = time.time() - 4000
        brain.associate()
        self.assertEqual(3, len(brain.active_memories))
        self.assertTrue(memories[0] in brain.active_memories)
        self.assertFalse(memories[1] in brain.active_memories)
        # low desire desire
        brain.active_memories = memories[2:]
        memories[0].reward = 1
        memories[1].reward = 1
        brain.associate()
        self.assertEqual(3, len(brain.active_memories))
        self.assertTrue(memories[1] in brain.active_memories)
        self.assertFalse(memories[0] in brain.active_memories)

    def test_match_virtual_memories(self):
        brain = Brain()
        # match one
        memories = test_memory.build_a_tree(constants.MATCHING)
        brain.active_memories = memories
        for i in range(0, 2):
            memories[i].status = constants.MATCHED
        brain.match_memories()
        self.assertEqual(memories[2].status, constants.MATCHED)
        # match whole tree
        memories = test_memory.build_a_tree(constants.MATCHING)
        brain.active_memories = memories
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
        brain.active_memories = memories
        for _ in range(0, 3):
            m = memory.create()
            m.status = constants.MATCHED
            m.memory_type = memory.MEMORY_TYPES.index(constants.FEATURE_MEMORY)
            m.feature_type = memory.MEMORY_FEATURES.index(constants.ACTION_REWARD)
            brain.active_memories.append(m)
        brain.active_memories[-1].matched_time = time.time() - 1
        brain.compose_memories()
        self.assertEqual(20, len(brain.active_memories))
        new_sound = brain.active_memories[14]
        self.assertEqual(constants.MATCHED, new_sound.status)
        self.assertEqual(1, len(new_sound.children))
        new_vision = brain.active_memories[15]
        self.assertEqual(2, len(new_vision.children))
        self.assertEqual(4, len(brain.active_memories[-1].children))

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
        brain.activate_parent(memories[0])
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
