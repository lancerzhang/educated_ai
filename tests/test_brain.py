from components.memory import Memory
from components.brain import Brain
from components import constants
from tests import test_memory
import time
import unittest


class TestBrain(unittest.TestCase):

    def setUp(self):
        pass

    def test_associate_active_memories_normal(self):
        # normal case
        brain = Brain()
        memories = []
        for x in range(0, 4):
            m = Memory()
            m.create()
            m.parent = set(memories)
            memories.append(m)
        brain.active_memories = memories[1:]
        brain.associate_active_memories()
        self.assertEqual(4, len(brain.active_memories))
        # dead case
        brain.active_memories = memories[1:]
        memories[0].live = False
        brain.associate_active_memories()
        self.assertEqual(3, len(brain.active_memories))
        # duplicated case
        brain.active_memories = memories
        memories[0].live = True
        brain.associate_active_memories()
        self.assertEqual(4, len(brain.active_memories))
        # base case
        brain.active_memories = memories[2:]
        memories[0].matched_time = time.time()
        memories[1].matched_time = time.time() - 4000
        brain.associate_active_memories()
        self.assertEqual(3, len(brain.active_memories))
        self.assertTrue(memories[0] in brain.active_memories)
        self.assertFalse(memories[1] in brain.active_memories)
        # low desire desire
        brain.active_memories = memories[2:]
        memories[0].reward = 1
        memories[1].reward = 1
        brain.associate_active_memories()
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
        brain.match_virtual_memories()
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
        brain.match_virtual_memories()
        self.assertEqual(memories[10].status, constants.MATCHED)


if __name__ == "__main__":
    unittest.main()
