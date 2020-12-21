import time
import unittest
from unittest.mock import MagicMock

from src import constants
from src.brain import Brain
from src.features import VoiceFeature
from src.memory import Memory


class TestBrain(unittest.TestCase):

    def test_input_voice(self):
        brain = Brain()
        self.assertIsNone(brain.input_voice([]))
        brain.add_real_memories = MagicMock(return_value=None)
        brain.add_memory = MagicMock(return_value=None)
        ls1 = [1, 2]
        brain.add_working = MagicMock(return_value=ls1)
        brain.input_voice(ls1)
        mt = constants.instant + constants.voice
        self.assertEqual(ls1, brain.work_temporal_memories[mt])

    def test_process(self):
        brain = Brain()
        self.assertIsNone(brain.process(set()))

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
        m1 = brain.create_memory(constants.real, VoiceFeature(1, 1), constants.voice)
        m2 = brain.create_memory(constants.pack, {m1.MID})
        m3 = brain.create_memory(constants.instant, [m2.MID])
        m4 = brain.create_memory(constants.short, [m3.MID])
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
        self.assertEqual(True, type(m2.data) == set)
        self.assertEqual(True, type(m4.data) == set)
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
        feature = VoiceFeature(1, 2, [[1, 2], [3, 4]])
        m1 = brain.create_memory(constants.real, feature, constants.voice)
        self.assertEqual(1, len(brain.categorized_memory[constants.voice]))
        self.assertEqual(1, len(brain.memory_cache[constants.voice]))
        # test creation
        brain.reindex()
        self.assertEqual(1, len(brain.categorized_memory[constants.voice]))
        self.assertEqual(0, len(brain.memory_cache[constants.voice]))
        self.assertNotEqual(None, brain.memory_vp_tree[constants.voice])
        self.assertEqual(1, brain.n_memories[constants.voice])
        # test deletion
        brain.categorized_memory[constants.voice] = {}
        brain.reindex()
        self.assertEqual(None, brain.memory_vp_tree[constants.voice])
        self.assertEqual(0, brain.n_memories[constants.voice])

    def test_input_memory(self):
        brain = Brain()
        self.assertEqual(None, brain.add_memory(constants.instant, []))
        self.assertEqual(None, brain.add_memory(constants.short, [1]))
        # test not found and then create memory
        brain.find_memory = MagicMock(return_value=(None, set(), set()))
        m1 = brain.create_memory(constants.real, VoiceFeature(1, 1), constants.voice)
        m2 = brain.add_memory(constants.pack, [m1])
        self.assertEqual({m1.MID}, m2.data)
        self.assertEqual({m2.MID}, m1.data_indexes)
        # test found memory
        brain.find_memory = MagicMock(return_value=(m2, set(), set()))
        m3 = brain.add_memory(constants.pack, [m1])
        self.assertEqual(m2, m3)

    def test_get_valid_memories(self):
        brain = Brain()
        m1 = brain.create_memory(constants.real, VoiceFeature(1, 1), constants.voice)
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
        m1 = brain.create_memory(constants.real, VoiceFeature(1, 1), constants.voice)
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
        m2 = brain.create_memory(constants.real, VoiceFeature(1, 2), constants.voice)
        m2.activated_time = time.time() - 4
        brain.get_valid_memories = MagicMock(return_value=[m1])
        self.assertEqual([m2], brain.add_working(m2, [], time_limit=5))

    def test_get_memory_duration(self):
        self.assertEqual(5, Brain.get_memory_duration(constants.short))

    def test_create_memory(self):
        brain = Brain()
        m1 = brain.create_memory(constants.real, VoiceFeature(1, 1), constants.voice)
        self.assertEqual(VoiceFeature, type(m1.data))
        m2 = brain.create_memory(constants.pack, [1, 2])
        self.assertEqual(set, type(m2.data))
        m3 = brain.create_memory(constants.short, [1, 2])
        self.assertEqual(set, type(m3.data))

    def test_add_strong_contexts(self):
        brain = Brain()
        brain.update_strong_contexts = MagicMock()
        brain.add_strong_contexts([None])
        self.assertEqual(0, len(brain.strong_context_memories))
        m1 = brain.create_memory(constants.real, VoiceFeature(1, 1), constants.voice)
        brain.add_strong_contexts([m1])
        self.assertEqual(0, len(brain.strong_context_memories))
        m1.stability = 9
        brain.add_links = MagicMock()
        brain.add_strong_contexts([m1])
        self.assertEqual(1, len(brain.strong_context_memories))
        brain.add_strong_contexts([m1])
        self.assertEqual(1, len(brain.strong_context_memories))
        brain.add_links.assert_called_once()

    def test_add_links(self):
        brain = Brain()
        brain.find_link = MagicMock(return_value=None)
        m1 = brain.create_memory(constants.real, VoiceFeature(1, 1), constants.voice)
        brain.strong_context_memories.add(m1)
        brain.add_links(m1)
        brain.find_link.assert_not_called()
        m2 = brain.create_memory(constants.real, VoiceFeature(1, 2), constants.voice)
        self.assertEqual(0, len(brain.categorized_memory[constants.link]))
        self.assertEqual(0, len(m1.link_indexes))
        self.assertEqual(0, len(m2.link_indexes))
        brain.add_links(m2)
        self.assertEqual(1, len(brain.categorized_memory[constants.link]))
        self.assertEqual(1, len(m1.link_indexes))
        self.assertEqual(1, len(m2.link_indexes))

    def test_update_strong_contexts(self):
        brain = Brain()
        m1 = brain.create_memory(constants.real, VoiceFeature(1, 1), constants.voice)
        brain.get_valid_memories = MagicMock(return_value=[m1])
        brain.get_memory_duration = MagicMock(return_value=0)
        brain.update_strong_contexts()
        self.assertEqual(0, len(brain.strong_context_memories))
        brain.get_memory_duration = MagicMock(return_value=5)
        brain.update_strong_contexts()
        self.assertEqual(1, len(brain.strong_context_memories))
        m2 = brain.create_memory(constants.real, VoiceFeature(1, 2), constants.voice)
        m2.stability = 9
        brain.get_valid_memories = MagicMock(return_value=[m1, m2])
        brain.update_strong_contexts(1)
        self.assertEqual(1, len(brain.strong_context_memories))
        m1.stability = m2.stability
        m1.activated_time = m2.activated_time + 1
        brain.update_strong_contexts(1)
        self.assertEqual(m1.MID, brain.strong_context_memories.pop().MID)
        brain.update_strong_contexts()
        self.assertEqual(2, len(brain.strong_context_memories))

    def test_update_weak_contexts(self):
        brain = Brain()
        m1 = brain.create_memory(constants.short, [])
        m2 = brain.create_memory(constants.long, [])
        m3 = brain.create_memory(constants.link, [m1, m2])
        m1.link_indexes = {m3.MID}
        m2.link_indexes = {m3.MID}
        brain.strong_context_memories = {m1}
        brain.update_weak_contexts()
        self.assertEqual(2, len(brain.weak_context_memories))
        del brain.all_memories[m2]
        brain.update_weak_contexts()
        self.assertEqual(1, len(brain.weak_context_memories))
        del brain.all_memories[m3]
        brain.update_weak_contexts()
        self.assertEqual(0, len(brain.weak_context_memories))

    def test_find_context(self):
        brain = Brain()
        m1 = brain.create_memory(constants.short, [])
        m2 = brain.create_memory(constants.long, [])
        m3 = brain.create_memory(constants.link, [m1, m2])
        self.assertIsNone(brain.find_link([m1, m2]))
        self.assertIsNone(brain.find_link([m1]))
        m1.link_indexes = {m3.MID}
        m2.link_indexes = {m3.MID}
        self.assertEqual(m3.MID, brain.find_link([m1, m2]))
        self.assertEqual(int, type(m3.data.pop()))


if __name__ == "__main__":
    unittest.main()
