import time
import unittest

from components import constants
from components.brain import Brain
from components.memory import Memory


class TestBrain(unittest.TestCase):

    def test_get_retrievability(self):
        self.assertEqual(1, Brain.get_retrievability(14, 0))
        self.assertEqual(0.99, Brain.get_retrievability(30, 0))
        self.assertEqual(0.98, Brain.get_retrievability(60, 0))
        self.assertEqual(0.95, Brain.get_retrievability(150, 0))
        self.assertEqual(0.90, Brain.get_retrievability(60 * 5, 0))
        self.assertEqual(0.79, Brain.get_retrievability(60 * 10, 0))
        self.assertEqual(0.58, Brain.get_retrievability(60 * 20, 0))
        self.assertEqual(0.44, Brain.get_retrievability(60 * 60, 0))
        self.assertEqual(0.26, Brain.get_retrievability(60 * 60 * 24, 0))
        self.assertEqual(0.23, Brain.get_retrievability(60 * 60 * 24 * 7, 0))
        self.assertEqual(0.21, Brain.get_retrievability(60 * 60 * 24 * 30, 0))
        self.assertEqual(0.20, Brain.get_retrievability(60 * 60 * 24 * 30 * 2, 0))
        self.assertEqual(1, Brain.get_retrievability(60 * 60 * 24 * 30, len(Brain.memory_cycles)))

    def test_activate_memory(self):
        stability = 0
        m = Memory(constants.real, None)
        m.created_time = m.activated_time = time.time() - 5
        Brain.activate_memory(m)
        self.assertEqual(stability, m.stability)
        m.created_time = m.activated_time = time.time() - 16
        Brain.activate_memory(m)
        stability += 1
        self.assertEqual(stability, m.stability)
        m.created_time = m.activated_time = time.time() - 20
        Brain.activate_memory(m)
        self.assertEqual(stability, m.stability)
        m.created_time = time.time() - 300
        m.activated_time = time.time() - 20
        Brain.activate_memory(m)
        self.assertEqual(stability, m.stability)
        m.created_time = m.activated_time = time.time() - 2592000
        Brain.activate_memory(m)
        stability += 1
        self.assertEqual(stability, m.stability)
        for _ in range(10):
            Brain.activate_memory(m)
        self.assertEqual(stability, m.stability)
        m.created_time = m.activated_time = time.time() - 1200
        m.stability = len(Brain.memory_cycles)
        Brain.activate_memory(m)
        stability = len(Brain.memory_cycles)
        self.assertEqual(stability, m.stability)

    def test_validate_memory(self):
        # test memory fail to validate
        m = Memory(constants.real, None)
        m.created_time = m.activated_time = time.time() - 2592000
        exist = True
        for _ in range(100):
            if exist:
                exist = Brain.validate_memory(m)
        self.assertEqual(False, exist)
        # test memory protected by steady
        m.activated_time = time.time()
        exist = True
        for _ in range(100):
            if exist:
                exist = Brain.validate_memory(m)
        self.assertEqual(True, exist)
        # test memory always retrievable in very short time
        m.created_time = m.activated_time = time.time() - 10
        exist = True
        for _ in range(300):
            if exist:
                exist = Brain.validate_memory(m)
        self.assertEqual(True, exist)


if __name__ == "__main__":
    unittest.main()
