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
        memories[i].set_memory_type(constants.FEATURE_MEMORY)
    for i in range(2, 4):
        memories[i].set_memory_type(constants.SLICE_MEMORY)
    for i in range(4, 6):
        memories[i].set_memory_type(constants.INSTANT_MEMORY)
    for i in range(6, 8):
        memories[i].set_memory_type(constants.SHORT_MEMORY)
    for i in range(8, 11):
        memories[i].set_memory_type(constants.LONG_MEMORY)
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
            memories[i].set_memory_type(constants.FEATURE_MEMORY)
        for i in range(2, 4):
            memories[i].set_memory_type(constants.SLICE_MEMORY)
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

    def test_flatten(self):
        m1 = memory.create()
        m2 = memory.create()
        m3 = memory.create()
        m4 = memory.create()
        m1.parent.add(m3)
        m1.children.append(m4)
        m2.parent.add(m3)
        m2.children.append(m4)
        memories = set()
        memories.add(m1)
        memories.add(m2)
        new_memories = memory.flatten(set(memories))
        p1 = new_memories.pop().parent.pop()
        self.assertEqual(p1, 3)
        self.assertTrue(isinstance(p1, int))
        self.assertEqual(new_memories.pop().children, [4])

    def test_construct(self):
        m1 = memory.create()
        m2 = memory.create()
        m3 = memory.create()
        m4 = memory.create()
        m1.parent.add(3)
        m1.children.append(4)
        m2.parent.add(3)
        m2.children.append(4)
        memories = set()
        memories.add(m1)
        memories.add(m2)
        memories.add(m3)
        memories.add(m4)
        new_memories = memory.construct(set(memories))
        nm1 = new_memories.pop()
        p1 = nm1.parent.pop()
        self.assertEqual(p1, m3)
        self.assertTrue(isinstance(p1, Memory))
        self.assertEqual(new_memories.pop().children, [m4])

    def test_create_index_common(self):
        indexes = {}
        m1 = memory.create()
        m1.set_memory_type(constants.SLICE_MEMORY)
        h11 = m1.get_index()
        self.assertIsNotNone(h11)
        m1.set_memory_type(constants.FEATURE_MEMORY)
        m1.set_feature_type(constants.SOUND_FEATURE)
        h12 = m1.get_index()
        self.assertNotEqual(h11, h12)
        m1.set_feature_type(constants.ACTION_MOUSE_CLICK)
        h13 = m1.get_index()
        self.assertNotEqual(h12, h13)
        m1.degrees = 36
        m1.speed = 400
        m1.duration = 0.1
        h14 = m1.get_index()
        self.assertNotEqual(h13, h14)
        m1.zoom_type = 'zmi'
        m1.zoom_direction = 'zlt'
        h15 = m1.get_index()
        self.assertNotEqual(h14, h15)
        m2 = memory.create()
        m2.set_memory_type(constants.FEATURE_MEMORY)
        m2.set_feature_type(constants.ACTION_MOUSE_CLICK)
        m2.click_type = constants.LEFT_CLICK
        m3 = memory.create()
        m3.set_memory_type(constants.FEATURE_MEMORY)
        m3.set_feature_type(constants.ACTION_MOUSE_CLICK)
        m3.click_type = constants.LEFT_CLICK
        self.assertEqual(m2.get_index(), m3.get_index())
        m4 = memory.create()
        m4.set_memory_type(constants.SLICE_MEMORY)
        m4.children = [m1, m2]
        m5 = memory.create()
        m5.set_memory_type(constants.SLICE_MEMORY)
        m5.children = [m2, m1]
        self.assertEqual(m4.get_index(), m5.get_index())
        m4.set_memory_type(constants.SHORT_MEMORY)
        m5.set_memory_type(constants.SHORT_MEMORY)
        self.assertNotEqual(m4.get_index(), m5.get_index())
        m1.create_index(indexes)
        rm1 = indexes.get(m1.get_index())
        self.assertEqual(rm1.degrees, 36)

    def test_create_index_kernel(self):
        indexes = {}
        m1 = memory.create()
        m1.set_memory_type(constants.FEATURE_MEMORY)
        m1.set_feature_type(constants.SOUND_FEATURE)
        m1.kernel = '0,0,0,0,1,0,0,0,0'
        m1.feature = '0,0,0,0,1,0,0,0,0'
        m1.create_index(indexes)
        h1 = indexes.get(m1.get_index())
        self.assertEqual(1, len(h1))
        m1.create_index(indexes)
        h1 = indexes.get(m1.get_index())
        self.assertEqual(2, len(h1))
        m2 = memory.create()
        m2.set_memory_type(constants.FEATURE_MEMORY)
        m2.set_feature_type(constants.VISION_FEATURE)
        m2.kernel = '0,0,0,0,1,0,0,0,0'
        m2.feature = '0,0,0,0,1,0,0,0,0'
        m2.create_index(indexes)
        h2 = indexes.get(m2.get_index())
        self.assertEqual(1, len(h2))
        h1 = indexes.get(m1.get_index())
        self.assertEqual(2, len(h1))
        m3 = memory.create()
        m3.set_memory_type(constants.FEATURE_MEMORY)
        m3.set_feature_type(constants.VISION_FEATURE)
        m3.kernel = '1,0,0,0,1,0,0,0,0'
        m3.feature = '1,0,0,0,1,0,0,0,0'
        m3.create_index(indexes)
        h3 = indexes.get(m3.get_index())
        self.assertEqual(1, len(h3))
        h2 = indexes.get(m2.get_index())
        self.assertEqual(1, len(h2))
        h1 = indexes.get(m1.get_index())
        self.assertEqual(2, len(h1))


if __name__ == "__main__":
    unittest.main()
