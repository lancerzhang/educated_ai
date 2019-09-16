from components.memory import Memory
from components.brain import Brain
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


if __name__ == "__main__":
    unittest.main()
