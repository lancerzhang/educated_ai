from components import memory
from components import util
from components.memory import Memory
from components.memory import MemoryType
from components.memory import MemoryStatus
from components.memory import RealType
import numpy as np
import time
import hashlib
import unittest


# parent (0,1)-2, (0)-3, (2,3)-4, (2)-5, (4,5)-6, (4)-7, (6,7)-8, (6)-9, (8,9)-10
def build_a_tree(status=MemoryStatus.SLEEP):
    memories = []
    memories.append(Memory(MemoryType.REAL, real_type=RealType.SOUND_FEATURE, kernel=b'0,-1,-1,1,0,1,1,-1,1',
                           feature=np.array([1, 228, 189, 55, 49, 37, 16, 35, 12])))
    memories.append(Memory(MemoryType.REAL, real_type=RealType.SOUND_FEATURE, kernel=b'0,-1,-1,1,0,1,1,-1,1',
                           feature=np.array([2, 228, 189, 55, 49, 37, 16, 35, 12])))
    memories.append(Memory(MemoryType.SLICE, real_type=-1, children=[memories[0], memories[1]]))
    memories.append(Memory(MemoryType.SLICE, real_type=-1, children=[memories[0]]))
    # memories[0].parent.add(memories[2])
    # memories[0].parent.add(memories[3])
    # memories[1].parent.add(memories[2])
    memories.append(Memory(MemoryType.INSTANT, real_type=-1, children=[memories[2], memories[3]]))
    memories.append(Memory(MemoryType.INSTANT, real_type=-1, children=[memories[2]]))
    # memories[2].parent.add(memories[4])
    # memories[2].parent.add(memories[5])
    # memories[3].parent.add(memories[4])
    memories.append(Memory(MemoryType.SHORT, real_type=-1, children=[memories[4], memories[5]]))
    memories.append(Memory(MemoryType.SHORT, real_type=-1, children=[memories[4]]))
    # memories[4].parent.add(memories[6])
    # memories[4].parent.add(memories[7])
    # memories[5].parent.add(memories[6])
    memories.append(Memory(MemoryType.LONG, real_type=-1, children=[memories[6], memories[7]]))
    memories.append(Memory(MemoryType.LONG, real_type=-1, children=[memories[6]]))
    # memories[6].parent.add(memories[8])
    # memories[6].parent.add(memories[9])
    # memories[7].parent.add(memories[9])
    memories.append(Memory(MemoryType.LONG, real_type=-1, children=[memories[8], memories[9]]))
    # memories[8].parent.add(memories[10])
    # memories[9].parent.add(memories[10])
    for m in memories:
        m.status = status
    return memories


class TestMemory(unittest.TestCase):

    def test_memory(self):
        memories = set()
        m1 = Memory(MemoryType.REAL, real_type=RealType.SOUND_FEATURE, kernel=b'0,0,0,0,1,0,0,0,0',
                    feature=[0, 0, 0, 0, 1, 0, 0, 0, 0])
        m1.recall_count = 9
        memories.add(m1)
        m2 = Memory(MemoryType.REAL, real_type=RealType.SOUND_FEATURE, kernel=b'0,0,0,0,1,0,0,0,0',
                    feature=[0, 0, 0, 0, 1, 0, 0, 0, 0])
        m2.recall_count = 1
        memories.add(m2)
        self.assertEqual(1, len(memories))
        self.assertEqual(9, memories.pop().recall_count)

    def test_calculate_protect_time(self):
        m = Memory(MemoryType.REAL)
        time1 = m.calculate_protect_time(1)
        self.assertEqual(int(time1), int(time.time() + np.sum(memory.TIME_SEC[1:11])))

    def test_get_desire(self):
        # normal case
        memory1 = Memory(MemoryType.REAL)
        self.assertEqual(memory.BASE_DESIRE, memory1.get_desire())
        memory1.matched_time = time.time() - 100
        self.assertEqual(memory.BASE_DESIRE, memory1.get_desire())
        memory1.reward = 1
        self.assertAlmostEqual(memory.BASE_DESIRE + 0.25, memory1.get_desire(), 2)
        memory1.matched_time = time.time() - 401
        self.assertEqual(1, memory1.get_desire())

    def test_hash(self):
        memories = build_a_tree()
        list1 = [memories[0], memories[1]]
        str1 = f'{list1}'
        print(str1)
        hash1 = hashlib.md5(str1.encode('utf-8')).hexdigest()
        list2 = [memories[0].mid, memories[1].mid]
        str2 = f'{list2}'
        print(str2)
        hash2 = hashlib.md5(str2.encode('utf-8')).hexdigest()
        self.assertNotEqual(hash1, hash2)

    def test_memory_hash(self):
        m1 = Memory(MemoryType.REAL, real_type=RealType.SOUND_FEATURE, kernel=b'0,0,0,0,1,0,0,0,0',
                    feature=[0, 0, 0, 0, 1, 0, 0, 0, 0])
        self.assertIsNotNone(m1.mid)
        m2 = Memory(MemoryType.REAL, real_type=RealType.SOUND_FEATURE, kernel=b'0,0,0,0,1,0,0,0,0',
                    feature=[0, 0, 0, 0, 1, 0, 0, 0, 0])
        # if content are the same, hash should be the same
        self.assertEqual(m1, m2)
        m3 = Memory(MemoryType.REAL, real_type=RealType.VISION_FEATURE, kernel=b'0,0,0,0,1,0,0,0,0',
                    feature=[0, 0, 0, 0, 1, 0, 0, 0, 0])
        # different feature type, hash should be different
        self.assertNotEqual(m3, m2)
        m4 = Memory(MemoryType.REAL, real_type=RealType.SOUND_FEATURE, kernel=b'0,0,0,0,1,0,0,0,0',
                    feature=[1, 0, 0, 0, 1, 0, 0, 0, 0])
        # different feature, hash should be different
        self.assertNotEqual(m4, m2)
        # different feature, kernel hash are the same
        self.assertEqual(m4.kernel_index, m2.kernel_index)
        # different feature type, kernel hash are different
        self.assertNotEqual(m4.kernel_index, m3.kernel_index)
        # test different memory type
        m5 = Memory(MemoryType.SLICE, real_type=RealType.SOUND_FEATURE, kernel=b'0,0,0,0,1,0,0,0,0',
                    feature=[1, 0, 0, 0, 1, 0, 0, 0, 0])
        self.assertNotEqual(m5, m4)
        # different channel
        m6 = Memory(MemoryType.REAL, real_type=RealType.VISION_FEATURE, kernel=b'0,0,0,0,1,0,0,0,0',
                    feature=[0, 0, 0, 0, 1, 0, 0, 0, 0], channel='y')
        m7 = Memory(MemoryType.REAL, real_type=RealType.VISION_FEATURE, kernel=b'0,0,0,0,1,0,0,0,0',
                    feature=[0, 0, 0, 0, 1, 0, 0, 0, 0], channel='u')
        self.assertNotEqual(m6.kernel_index, m7.kernel_index)

    def test_calculate_desire(self):
        m = Memory(MemoryType.REAL)
        m.matched_time = time.time()
        m.reward = 1
        self.assertAlmostEqual(m.get_desire(), memory.BASE_DESIRE, 1)
        m.reward = 0.5
        self.assertAlmostEqual(m.get_desire(), memory.BASE_DESIRE, 1)
        m.reward = 0
        self.assertAlmostEqual(m.get_desire(), memory.BASE_DESIRE, 1)
        m.matched_time = time.time() - 100
        m.reward = 1
        self.assertAlmostEqual(m.get_desire(), memory.BASE_DESIRE + 0.25, 1)
        m.matched_time = time.time() - 500
        self.assertEqual(m.get_desire(), 1)

    def test_calculate_strength(self):
        m = Memory(MemoryType.LONG)
        m.active_end_time = time.time() + m.get_duration()
        m.recall_count = 1
        self.assertAlmostEqual(m.get_strength(), memory.BASE_STRENGTH + 0.01, 2)
        m.active_end_time = time.time()
        self.assertAlmostEqual(m.get_strength(), memory.BASE_STRENGTH, 2)
        m.active_end_time = time.time() - 10
        self.assertAlmostEqual(m.get_strength(), memory.BASE_STRENGTH, 2)
        m.recall_count = 50
        m.active_end_time = time.time() + m.get_duration()
        self.assertAlmostEqual(m.get_strength(), memory.BASE_STRENGTH + 0.5, 2)
        m.recall_count = 99
        self.assertEqual(m.get_strength(), 1)

    def test_create_kernel_index(self):
        indexes = {}
        m1 = Memory(MemoryType.REAL, real_type=RealType.SOUND_FEATURE, kernel=b'0,0,0,0,1,0,0,0,0',
                    feature=[0, 0, 0, 0, 1, 0, 0, 0, 0])
        m1.create_index(indexes)
        self.assertEqual(1, len(indexes.get(m1.kernel_index)))
        m2 = Memory(MemoryType.REAL, real_type=RealType.SOUND_FEATURE, kernel=b'0,0,0,0,1,0,0,0,0',
                    feature=[0, 0, 0, 0, 1, 0, 0, 0, 0])
        m2.create_index(indexes)
        self.assertEqual(1, len(indexes.get(m1.kernel_index)))
        m3 = Memory(MemoryType.REAL, real_type=RealType.SOUND_FEATURE, kernel=b'0,0,0,0,1,0,0,0,0',
                    feature=[1, 0, 0, 0, 1, 0, 0, 0, 0])
        m3.create_index(indexes)
        self.assertEqual(2, len(indexes.get(m1.kernel_index)))
        self.assertEqual(2, len(indexes.get(m3.kernel_index)))

    def test_match_children_normal(self):
        memories = build_a_tree(MemoryStatus.MATCHING)
        memories[0].matched_time = time.time() - 0.1
        memories[1].matched_time = time.time() - 0.1
        memories[2].match_children()
        self.assertEqual(memories[2].status, MemoryStatus.MATCHED)
        memories[3].matched_time = time.time()
        self.assertEqual(memories[4].status, MemoryStatus.MATCHING)
        memories[4].match_children()
        self.assertEqual(memories[4].status, MemoryStatus.MATCHED)

    def test_match_children_exception(self):
        memories = []
        memories.append(Memory(MemoryType.REAL, real_type=RealType.SOUND_FEATURE, kernel=b'0,-1,-1,1,0,1,1,-1,1',
                               feature=np.array([1, 228, 189, 55, 49, 37, 16, 35, 12])))
        memories.append(Memory(MemoryType.REAL, real_type=RealType.SOUND_FEATURE, kernel=b'0,-1,-1,1,0,1,1,-1,1',
                               feature=np.array([2, 228, 189, 55, 49, 37, 16, 35, 12])))
        memories.append(Memory(MemoryType.REAL, real_type=RealType.SOUND_FEATURE, kernel=b'0,-1,-1,1,0,1,1,-1,1',
                               feature=np.array([3, 228, 189, 55, 49, 37, 16, 35, 12])))
        memories.append(Memory(MemoryType.SLICE, real_type=-1, children=[memories[0], memories[1], memories[2]]))
        for m in memories:
            m.status = MemoryStatus.MATCHING
        # case1
        memories[2].matched_time = time.time() - 1
        memories[3].match_children()
        self.assertEqual(MemoryStatus.MATCHED, memories[3].status)
        # case 2
        memories[2].matched_time = time.time()
        memories[2].status = MemoryStatus.DORMANT
        memories[3].match_children()
        self.assertEqual(MemoryStatus.MATCHED, memories[3].status)
        # case3
        memories[3].status = MemoryStatus.DORMANT
        memories[3].match_children()
        self.assertEqual(MemoryStatus.DORMANT, memories[3].status)

    def test_matched(self):
        m1 = Memory(MemoryType.REAL, real_type=RealType.SOUND_FEATURE, kernel=b'0,-1,-1,1,0,1,1,-1,1',
                    feature=np.array([1, 228, 189, 55, 49, 37, 16, 35, 12]))
        m1.status = MemoryStatus.SLEEP
        m1.matched_time = 0
        m1.matched(recall=False)
        self.assertEqual(MemoryStatus.MATCHED, m1.status)
        self.assertTrue(m1.matched_time > 0)

    def test_create_children_index(self):
        memories = build_a_tree()
        indexes = {}
        for m in memories:
            m.create_index(indexes)
        k1 = [memories[0].mid]
        h1 = memory.create_children_hash(k1, memories[2].memory_type)
        c1 = indexes.get(h1)
        k2 = [memories[1].mid]
        h2 = memory.create_children_hash(k2, memories[2].memory_type)
        c2 = indexes.get(h2)
        k3 = [memories[0].mid, memories[1].mid]
        h3 = memory.create_children_hash(k3, memories[2].memory_type)
        c3 = indexes.get(h3)
        k4 = [memories[1].mid, memories[0].mid]
        h4 = memory.create_children_hash(k4, memories[2].memory_type)
        c4 = indexes.get(h4)
        self.assertNotEqual(c1, c2)
        self.assertEqual(c2, c3)
        self.assertEqual(c4, c3)
        k5 = [memories[2].mid, memories[3].mid]
        h5 = memory.create_children_hash(k5, memories[4].memory_type)
        c5 = indexes.get(h5)
        k6 = [memories[3].mid, memories[2].mid]
        h6 = memory.create_children_hash(k6, memories[4].memory_type)
        c6 = indexes.get(h6)
        self.assertNotEqual(c5, c6)


if __name__ == "__main__":
    unittest.main()
