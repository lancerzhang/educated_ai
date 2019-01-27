import constants
import logging
import memory
import random
import time
from pynput.mouse import Button, Controller

logger = logging.getLogger('Action')
logger.setLevel(logging.INFO)


class Action(object):
    LEFT_CLICK = 'lcl'

    def __init__(self, ds):
        self.mouse = Controller()
        self.data_adaptor = ds

    def process(self, working_memories, sequential_time_memories, work_status, button):
        actor_mouse_memories = [mem for mem in working_memories if
                                constants.MEMORY_DURATION in mem and
                                mem[constants.MEMORY_DURATION] is constants.SLICE_MEMORY and
                                mem[constants.STATUS] is constants.MATCHING and
                                constants.PHYSICAL_MEMORY_TYPE in mem and
                                mem[constants.PHYSICAL_MEMORY_TYPE] is constants.ACTION_MOUSE]

        matched_feature_memories = self.match_actor_mouse_memories(actor_mouse_memories)

        for mem in matched_feature_memories:
            working_memories.append(mem)

        if button is constants.MOUSE_LEFT:
            new_slice_memory = self.feel_left_click()
            if new_slice_memory is not None:
                sequential_time_memories[constants.SLICE_MEMORY].append(new_slice_memory)
                working_memories.append(new_slice_memory)
        elif not work_status[constants.BUSY][constants.MEDIUM_DURATION] or not work_status[constants.REWARD]:
            self.explore()

    def match_actor_mouse_memories(self, memories):
        matched_memories = []
        for mem in memories:
            click_type = mem[constants.CLICK_TYPE]
            if click_type is self.LEFT_CLICK:
                self.mouse.click(Button.left)
                memory.recall_memory(mem)
                matched_memories.append(mem)
        return matched_memories

    def feel_left_click(self):
        logger.debug('feel_left_click')
        click_type = self.LEFT_CLICK
        mem = self.data_adaptor.get_action_mouse_memory(click_type)
        if mem is None:
            action = {constants.PHYSICAL_MEMORY_TYPE: constants.ACTION_MOUSE, constants.CLICK_TYPE: click_type}
            action_memory = memory.add_physical_memory(action)
        else:
            memory.recall_memory(mem)
            action_memory = mem
        slice_memory = memory.add_collection_memory(constants.SLICE_MEMORY, [action_memory], constants.ACTION_MOUSE)
        return slice_memory

    def left_click(self):
        self.mouse.click(Button.left)
        return self.feel_left_click()

    def explore(self):
        ri = random.randint(0, 100)
        if ri > 0:
            return
        self.mouse.click(Button.left)
        logger.debug('explore')
