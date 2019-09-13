from components.memory import Memory
from components.brain import Brain
import unittest


class TestBrain(unittest.TestCase):

    def setUp(self):
        pass

    def test_associate_active_memories_normal(self):
        brain = Brain()
        memory1 = Memory()
        memory1.create()
        memory2 = Memory()
        memory2.create()
        memory3 = Memory()
        memory3.create()
        memory4 = Memory()
        memory4.create()
        memory2.parent = {memory1}
        memory3.parent = {memory1, memory2}
        memory4.parent = {memory1, memory2, memory3}
        brain.active_memories = [memory2, memory3, memory4]
        brain.associate_active_memories()
        self.assertEqual(4, len(brain.active_memories))


if __name__ == "__main__":
    unittest.main()
