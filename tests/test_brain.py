import time
import unittest
from unittest.mock import MagicMock

from src import constants
from src.brain import Brain
from src.features import SpeechFeature
from src.memory import Memory


class TestBrain(unittest.TestCase):

    def test_recognize_speech(self):
        brain = Brain()
        self.assertIsNone(brain.recognize_speech([]))

    def test_add_real_memories(self):
        brain = Brain()
        s1 = SpeechFeature(1, 1)
        s2 = SpeechFeature(1, 2)
        brain.find_real = MagicMock(return_value=None)
        memories = brain.add_real_memories([s1, s2])
        self.assertEqual(2, len(memories))

    def test_get_parent_type(self):
        brain = Brain()
        m1 = brain.create_memory(constants.real, SpeechFeature(1, 1), constants.speech)
        self.assertEqual(constants.pack_real, brain.get_parent_type(m1))
        m1.MEMORY_TYPE = constants.pack_real
        self.assertEqual(constants.instant, brain.get_parent_type(m1))
        m1.MEMORY_TYPE = constants.instant
        self.assertEqual(constants.pack_instant, brain.get_parent_type(m1))
        m1.MEMORY_TYPE = constants.pack_instant
        self.assertEqual(constants.short, brain.get_parent_type(m1))
        m1.MEMORY_TYPE = constants.short
        self.assertEqual(constants.short, brain.get_parent_type(m1))

    def test_find_parents(self):
        brain = Brain()
        self.assertIsNone(brain.find_parents([]))
        # test real memory
        m1 = brain.create_memory(constants.real, SpeechFeature(1, 1), constants.speech)
        m2 = brain.create_memory(constants.real, SpeechFeature(1, 2), constants.speech)
        m3 = brain.create_memory(constants.real, SpeechFeature(1, 3), constants.speech)
        m4 = brain.add_memory([m1, m2])
        m5 = brain.add_memory([m1, m2, m3])
        full_matches, partial_matches = brain.find_parents([m1, m2, m3])
        self.assertEqual(1, len(full_matches))
        self.assertEqual(2, len(partial_matches))
        self.assertEqual(m5, full_matches.pop())
        # test order memory
        m4.MEMORY_TYPE = constants.pack_instant
        m5.MEMORY_TYPE = constants.pack_instant
        m6 = brain.add_memory([m4, m5])
        self.assertEqual(constants.short, m6.MEMORY_TYPE)
        full_matches, partial_matches = brain.find_parents([m4, m5])
        self.assertEqual(1, len(full_matches))
        # test incorrect order
        full_matches, partial_matches = brain.find_parents([m5, m4])
        self.assertEqual(0, len(full_matches))

    def test_add_memory(self):
        brain = Brain()
        m1 = brain.create_memory(constants.real, SpeechFeature(1, 1), constants.speech)
        m2 = brain.create_memory(constants.pack_real, [m1])
        m3 = brain.create_memory(constants.real, SpeechFeature(1, 3), constants.speech)
        m4 = brain.create_memory(constants.pack_real, [m3])
        self.assertIsNone(brain.add_memory([]))
        self.assertIsNotNone(brain.add_memory([m1]))
        # test add disorder memory
        brain.find_parents = MagicMock(return_value=([], []))
        n1 = brain.add_memory([m1, m3])
        self.assertEqual({m1, m3}, n1.data)
        self.assertNotEqual(m2.MID, n1.MID)
        # test return disorder memory
        brain.find_parents = MagicMock(return_value=([m2], [m2]))
        n1 = brain.add_memory([m1])
        self.assertEqual(m2.MID, n1.MID)
        # test best match equal
        brain.context_memories = {m2}
        m3.context = {m2.MID}
        brain.get_parent_type = MagicMock(return_value=constants.short)
        brain.sort_context = MagicMock(return_value=([m3, m4]))
        brain.find_parents = MagicMock(return_value=([m2], [m2]))
        n2 = brain.add_memory([m2, m4])
        self.assertEqual(m3.MID, n2.MID)
        # test best match NOT equal
        brain.context_memories = {}
        n2 = brain.add_memory([m2, m4])
        self.assertNotEqual(m3.MID, n2.MID)
        # test match_contexts
        brain.match_contexts = MagicMock(return_value='match_contexts')
        n2 = brain.add_memory([m2, m4])
        self.assertNotEqual('match_contexts', n2)
        # test not match_contexts
        brain.match_contexts = MagicMock(return_value=None)
        n2 = brain.add_memory([m2, m4])
        self.assertNotEqual(m3.MID, n2.MID)

    def test_get_common_contexts(self):
        brain = Brain()
        m1 = brain.create_memory(constants.real, SpeechFeature(1, 1), constants.speech)
        m2 = brain.create_memory(constants.real, SpeechFeature(1, 2), constants.speech)
        brain.context_memories = {m1, m2}
        m2.context = {m1.MID}
        self.assertEqual({m1}, brain.get_common_contexts(m2))

    def test_get_context_weight(self):
        brain = Brain()
        m1 = brain.create_memory(constants.real, SpeechFeature(1, 1), constants.speech)
        m2 = brain.create_memory(constants.real, SpeechFeature(1, 2), constants.speech)
        m3 = brain.create_memory(constants.real, SpeechFeature(1, 2), constants.speech)
        m2.context_weight = 0.5
        m3.context_weight = 0.6
        brain.get_common_contexts = MagicMock(return_value={m2, m3})
        self.assertEqual(1.1, brain.get_context_weight(m1))

    def test_sort_context(self):
        brain = Brain()
        m1 = brain.create_memory(constants.real, SpeechFeature(1, 1), constants.speech)
        m2 = brain.create_memory(constants.real, SpeechFeature(1, 2), constants.speech)
        m3 = brain.create_memory(constants.real, SpeechFeature(1, 2), constants.speech)
        brain.context_memories = {m1, m2, m3}
        m1.context_weight = 0.7
        m2.context_weight = 0.5
        m3.context_weight = 0.6
        m1.context = {m2.MID, m3.MID}
        m2.context = {m1.MID, m3.MID}
        m3.context = {m2.MID, m1.MID}
        self.assertEqual([m2, m3, m1], brain.sort_context({m1, m2, m3}))

    def test_add_to_instant_queue(self):
        brain = Brain()
        m1 = brain.create_memory(constants.real, SpeechFeature(1, 1), constants.speech)
        self.assertEqual(m1, brain.add_to_instant_queue(constants.speech, m1))
        self.assertIsNone(brain.add_to_instant_queue(constants.speech, m1))

    def test_match_contexts(self):
        brain = Brain()
        m1 = brain.create_memory(constants.real, SpeechFeature(1, 1), constants.speech)
        m2 = brain.create_memory(constants.real, SpeechFeature(1, 2), constants.speech)
        m3 = brain.create_memory(constants.real, SpeechFeature(1, 2), constants.speech)
        m1.context = {m2.MID, m3.MID}
        m2.context = {m1.MID, m3.MID}
        m3.context = {m2.MID, m1.MID}
        self.assertEqual(m3, brain.match_contexts({m1, m2, m3}, {m1, m2}))

    def test_process(self):
        brain = Brain()
        self.assertIsNone(brain.recognize_temporal(set()))

    def test_get_retrievability(self):
        self.assertEqual(1, Brain.get_retrievability(Brain.memory_cycles[0] - 1, 0))
        self.assertEqual(1, Brain.get_retrievability(Brain.memory_cycles[0], 0))
        self.assertEqual(0.99, Brain.get_retrievability(Brain.memory_cycles[0] + 1, 0))
        self.assertEqual(1, Brain.get_retrievability(14, 1))
        self.assertEqual(0.99, Brain.get_retrievability(30, 1))
        self.assertEqual(0.98, Brain.get_retrievability(60, 1))
        self.assertEqual(0.95, Brain.get_retrievability(150, 1))
        self.assertEqual(0.90, Brain.get_retrievability(60 * 5, 1))
        self.assertEqual(0.79, Brain.get_retrievability(60 * 10, 1))
        self.assertEqual(0.58, Brain.get_retrievability(60 * 20, 1))
        self.assertEqual(0.44, Brain.get_retrievability(60 * 60, 1))
        self.assertEqual(0.26, Brain.get_retrievability(60 * 60 * 24, 1))
        self.assertEqual(0.23, Brain.get_retrievability(60 * 60 * 24 * 7, 1))
        self.assertEqual(0.21, Brain.get_retrievability(60 * 60 * 24 * 30, 1))
        self.assertEqual(0.20, Brain.get_retrievability(60 * 60 * 24 * 30 * 2, 1))
        self.assertEqual(1, Brain.get_retrievability(60 * 60 * 24 * 30, len(Brain.memory_cycles)))

    def test_activate_memory(self):
        stability = 0
        # test not strengthen in short time
        m = Memory(constants.real, None)
        m.CREATED_TIME = m.activated_time = m.strengthen_time = time.time() - 5
        Brain.activate_memory(m)
        self.assertEqual(stability, m.stability)
        # test strengthen
        m.CREATED_TIME = m.activated_time = m.strengthen_time = time.time() - 16
        Brain.activate_memory(m)
        stability += 1
        self.assertEqual(stability, m.stability)
        # test not strengthen in second short time
        m.CREATED_TIME = m.activated_time = m.strengthen_time = time.time() - 20
        Brain.activate_memory(m)
        self.assertEqual(stability, m.stability)
        # test not strengthen if short elapse time after last strengthen_time
        m.CREATED_TIME = time.time() - 300
        m.strengthen_time = time.time() - 20
        Brain.activate_memory(m)
        self.assertEqual(stability, m.stability)
        # test strengthen in another long time
        m.CREATED_TIME = m.activated_time = m.strengthen_time = time.time() - 2592000
        Brain.activate_memory(m)
        stability += 1
        self.assertEqual(stability, m.stability)
        # test can't strength continuously
        for _ in range(10):
            Brain.activate_memory(m)
        self.assertEqual(stability, m.stability)
        # test not strengthen_time when stability is maximum
        m.CREATED_TIME = m.activated_time = m.strengthen_time = time.time() - 1200
        m.stability = len(Brain.memory_cycles)
        Brain.activate_memory(m)
        stability = len(Brain.memory_cycles)
        self.assertEqual(stability, m.stability)

    def test_activate_memory_continuously(self):
        stability = 0
        # test not strengthen in short time
        m = Memory(constants.real, None)
        m.CREATED_TIME = m.activated_time = m.strengthen_time = time.time() - 1
        Brain.activate_memory(m)
        self.assertEqual(stability, m.stability)
        for i in range(2, Brain.memory_cycles[0]):
            m.CREATED_TIME = m.activated_time = m.strengthen_time = time.time() - i
        self.assertEqual(stability, m.stability)
        m.CREATED_TIME = m.activated_time = m.strengthen_time = time.time() - (Brain.memory_cycles[0] + 1)
        Brain.activate_memory(m)
        stability += 1
        self.assertEqual(stability, m.stability)

    def test_validate_memory(self):
        # test memory fail to validate
        m = Memory(constants.real, None)
        Brain.is_steady = MagicMock(return_value=False)
        m.CREATED_TIME = m.activated_time = time.time() - 2592000
        exist = True
        for _ in range(100):
            if exist:
                exist = Brain.validate_memory(m)
        self.assertEqual(False, exist)
        # test memory protected by steady
        Brain.is_steady = MagicMock(return_value=True)
        m.activated_time = time.time()
        exist = True
        for _ in range(100):
            if exist:
                exist = Brain.validate_memory(m)
        self.assertEqual(True, exist)
        # test memory always retrievable in very short time
        exist = True
        Brain.is_steady = MagicMock(return_value=False)
        m.CREATED_TIME = m.activated_time = time.time() - 10
        for _ in range(300):
            if exist:
                exist = Brain.validate_memory(m)
        self.assertEqual(True, exist)

    def test_is_steady(self):
        m = Memory(constants.real, None)
        m.CREATED_TIME = m.activated_time = time.time() - 10
        self.assertEqual(True, Brain.is_steady(m))
        m.CREATED_TIME = m.activated_time = time.time() - 20
        self.assertEqual(False, Brain.is_steady(m))

    def test_cleanup_memories(self):
        brain = Brain()
        m1 = brain.create_memory(constants.real, SpeechFeature(1, 1), constants.speech)
        m2 = brain.create_memory(constants.pack_real, {m1})
        m3 = brain.create_memory(constants.instant, [m2])
        m4 = brain.create_memory(constants.short, [m3])
        m3.data_indexes = {m4.MID}
        brain.validate_memory = MagicMock(return_value=True)
        brain.cleanup_memories()
        # normal case
        self.assertEqual(4, len(brain.all_memories))
        self.assertEqual(1, len(m3.data_indexes))
        self.assertEqual(1, len(m2.data))
        self.assertEqual(1, len(m3.data))
        # test cleanup data index
        del brain.all_memories[m4.MID]
        self.assertEqual(3, len(brain.all_memories))
        brain.cleanup_memories()
        self.assertEqual(0, len(m3.data_indexes))
        # test cleanup data
        self.assertTrue(type(m2.data) == set)
        self.assertTrue(type(m4.data) == list)
        del brain.all_memories[m1.MID]
        brain.cleanup_memories()
        self.assertEqual(0, len(m2.data))
        del brain.all_memories[m2.MID]
        brain.cleanup_memories()
        self.assertEqual(0, len(m3.data))
        # test memory forget
        brain.validate_memory = MagicMock(return_value=False)
        brain.cleanup_memories()
        self.assertEqual(0, len(brain.all_memories))

    def test_reindex(self):
        brain = Brain()
        feature = SpeechFeature(1, 2, [[1, 2], [3, 4]])
        m1 = brain.create_memory(constants.real, feature, constants.speech)
        self.assertEqual(1, len(brain.categorized_memory[constants.speech]))
        self.assertEqual(1, len(brain.memory_cache[constants.speech]))
        # test creation
        brain.reindex()
        self.assertEqual(1, len(brain.categorized_memory[constants.speech]))
        self.assertEqual(0, len(brain.memory_cache[constants.speech]))
        self.assertNotEqual(None, brain.memory_vp_tree[constants.speech])
        self.assertEqual(1, brain.n_memories[constants.speech])
        # test deletion
        brain.categorized_memory[constants.speech] = {}
        brain.reindex()
        self.assertEqual(None, brain.memory_vp_tree[constants.speech])
        self.assertEqual(0, brain.n_memories[constants.speech])

    def test_input_memory(self):
        brain = Brain()
        m1 = brain.create_memory(constants.real, SpeechFeature(1, 1), constants.speech)
        m2 = brain.add_memory([m1])
        self.assertIsNone(brain.add_memory([]))
        self.assertIsNotNone(brain.add_memory([m1]))
        # test not found and then create memory
        brain.find_parents = MagicMock(return_value=(None, set()))
        self.assertEqual({m1.MID}, m2.data)
        self.assertEqual({m2.MID}, m1.data_indexes)
        # test found memory
        brain.find_parents = MagicMock(return_value=({m2}, set()))
        m3 = brain.add_memory([m1])
        self.assertEqual(m2, m3)

    def test_get_valid_memories(self):
        brain = Brain()
        m1 = brain.create_memory(constants.real, SpeechFeature(1, 1), constants.speech)
        self.assertEqual([m1.MID], brain.get_valid_memories([m1.MID]))
        self.assertEqual([m1], brain.get_valid_memories([m1.MID], output_type='Memory'))
        self.assertEqual([m1.MID], brain.get_valid_memories([m1]))
        self.assertEqual([m1], brain.get_valid_memories([m1], output_type='Memory'))
        self.assertEqual([], brain.get_valid_memories(["not exist"]))
        self.assertEqual({m1.MID}, brain.get_valid_memories({m1.MID}))
        del brain.all_memories[m1.MID]
        self.assertEqual([], brain.get_valid_memories([m1]))

    def test_add_working(self):
        brain = Brain()
        # test add none
        self.assertEqual([], brain.add_working(None, []))
        m1 = brain.create_memory(constants.real, SpeechFeature(1, 1), constants.speech)
        # test add into blank list
        self.assertEqual([m1], brain.add_working(m1, []))
        # test add the same memory
        self.assertEqual([m1], brain.add_working(m1, []))
        # test n_limit
        ls = [1, 2, 3, m1]
        brain.get_valid_memories = MagicMock(return_value=ls)
        self.assertEqual(ls, brain.add_working(m1, ls, n_limit=4))
        ls = [1, 2, 3, 4, 5, m1]
        brain.get_valid_memories = MagicMock(return_value=ls)
        self.assertEqual([3, 4, 5, m1], brain.add_working(m1, ls, n_limit=4))
        # test time_limit
        m1.activated_time = time.time() - 6
        m2 = brain.create_memory(constants.real, SpeechFeature(1, 2), constants.speech)
        m2.activated_time = time.time() - 4
        brain.get_valid_memories = MagicMock(return_value=[m1])
        self.assertEqual([m2], brain.add_working(m2, [], time_limit=5))

    def test_get_memory_duration(self):
        self.assertEqual(5, Brain.get_memory_duration(constants.short))

    def test_create_memory(self):
        brain = Brain()
        m1 = brain.create_memory(constants.real, SpeechFeature(1, 1), constants.speech)
        m2 = brain.create_memory(constants.real, SpeechFeature(1, 2), constants.speech)
        self.assertEqual(SpeechFeature, type(m1.data))
        m2 = brain.create_memory(constants.pack_real, [m1, m2])
        self.assertEqual(set, type(m2.data))
        m3 = brain.create_memory(constants.short, [m1, m2])
        self.assertEqual(list, type(m3.data))

    def test_update_contexts(self):
        brain = Brain()
        m1 = brain.create_memory(constants.real, SpeechFeature(1, 1), constants.speech)
        brain.get_valid_memories = MagicMock(return_value=[m1])
        brain.get_memory_duration = MagicMock(return_value=0)
        brain.update_contexts()
        self.assertEqual(0, len(brain.context_memories))
        brain.get_memory_duration = MagicMock(return_value=5)
        brain.update_contexts()
        self.assertEqual(1, len(brain.context_memories))
        m2 = brain.create_memory(constants.real, SpeechFeature(1, 2), constants.speech)
        m2.stability = 9
        brain.get_valid_memories = MagicMock(return_value=[m1, m2])
        brain.update_contexts(1)
        self.assertEqual(1, len(brain.context_memories))
        m1.stability = m2.stability
        m1.activated_time = m2.activated_time + 1
        brain.update_contexts(1)
        self.assertEqual(m1.MID, brain.context_memories.pop().MID)
        brain.update_contexts()
        self.assertEqual(2, len(brain.context_memories))

    def test_update_weight(self):
        brain = Brain()
        m1 = brain.create_memory(constants.real, SpeechFeature(1, 1), constants.speech)
        m2 = brain.create_memory(constants.real, SpeechFeature(1, 2), constants.speech)
        m3 = brain.create_memory(constants.real, SpeechFeature(1, 3), constants.speech)
        m4 = brain.add_memory([m1, m2])
        m5 = brain.add_memory([m2, m3])
        m6 = brain.add_memory([m1, m2, m3])
        m4.context_indexes = {m5.MID, m6.MID}
        m5.context_indexes = {m6.MID}
        brain.update_context_weight(m4)
        brain.update_context_weight(m5)
        self.assertGreater(m5.context_weight, m4.context_weight)


if __name__ == "__main__":
    unittest.main()
