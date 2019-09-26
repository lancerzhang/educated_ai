from components.memory import Memory
from components import constants
from components import memory
import time
import unittest


def build_a_tree(status=constants.DORMANT):
    memory.id_sequence = 0
    memories = []
    for x in range(0, 11):
        m = memory.create()
        m.status = status
        memories.append(m)
    for i in range(0, 2):
        memories[i].memory_type = memory.MEMORY_TYPES.index(constants.FEATURE_MEMORY)
    for i in range(2, 4):
        memories[i].memory_type = memory.MEMORY_TYPES.index(constants.SLICE_MEMORY)
    for i in range(4, 6):
        memories[i].memory_type = memory.MEMORY_TYPES.index(constants.INSTANT_MEMORY)
    for i in range(6, 8):
        memories[i].memory_type = memory.MEMORY_TYPES.index(constants.SHORT_MEMORY)
    for i in range(8, 11):
        memories[i].memory_type = memory.MEMORY_TYPES.index(constants.LONG_MEMORY)
    memories[2].children = memories[0:2]
    memories[4].children = memories[2:4]
    memories[6].children = memories[4:6]
    memories[8].children = memories[6:8]
    memories[10].children = memories[8:10]
    return memories


class TestMemory(unittest.TestCase):

    def setUp(self):
        memory.id_sequence = 0

    def test_get_desire(self):
        # normal case
        memory1 = Memory()
        self.assertEqual(memory.BASE_DESIRE, memory1.get_desire())
        memory1.matched_time = time.time() - 1000
        self.assertEqual(memory.BASE_DESIRE, memory1.get_desire())
        memory1.reward = 1
        self.assertAlmostEqual(memory.BASE_DESIRE + 0.25, memory1.get_desire(), 2)
        memory1.matched_time = time.time() - 4001
        self.assertEqual(1, memory1.get_desire())

    def test_activate_tree_left_leaf(self):
        memories = build_a_tree()
        # 1st validation
        memories[8].activate_tree()
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
        memories[8].activate_tree()
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
        memories[8].activate_tree()
        self.assertEqual(memories[3].status, constants.MATCHING)
        memories[4].status = constants.MATCHED
        memories[8].activate_tree()
        self.assertEqual(memories[5].status, constants.MATCHING)

    def test_activate_tree_middle_leaf(self):
        memories = build_a_tree()
        memories[8].status = constants.MATCHING
        memories[9].children = memories[6:8]
        # 1st validation
        memories[10].activate_tree()
        self.assertEqual(memories[9].status, constants.DORMANT)
        # match 1st long
        memories[8].status = constants.MATCHED
        memories[10].activate_tree()
        self.assertEqual(memories[0].status, constants.MATCHING)
        self.assertEqual(memories[1].status, constants.MATCHING)
        self.assertEqual(memories[2].status, constants.MATCHING)
        self.assertEqual(memories[4].status, constants.MATCHING)
        self.assertEqual(memories[6].status, constants.MATCHING)
        self.assertEqual(memories[9].status, constants.MATCHING)

    def test_match(self):
        memories = []
        for x in range(0, 4):
            m = memory.create()
            m.status = constants.MATCHING
            memories.append(m)
        for i in range(0, 2):
            memories[i].memory_type = memory.MEMORY_TYPES.index(constants.FEATURE_MEMORY)
        for i in range(2, 4):
            memories[i].memory_type = memory.MEMORY_TYPES.index(constants.SLICE_MEMORY)
        memories[2].children = memories[0:2]
        self.assertFalse(memories[2].match())
        for i in range(0, 2):
            memories[i].status = constants.MATCHED
        self.assertTrue(memories[2].match())

    def test_equals(self):
        memories = build_a_tree()
        # memory type not equal
        self.assertFalse(memories[1].equal(memories[2]))
        # slice memory equals without order
        self.assertFalse(memories[3].equal(memories[2]))
        memories[3].children = [memories[1], memories[0]]
        self.assertTrue(memories[3].equal(memories[2]))
        # other memory equals with order
        memories[5].children = [memories[3], memories[2]]
        self.assertFalse(memories[5].equal(memories[4]))


if __name__ == "__main__":
    unittest.main()
