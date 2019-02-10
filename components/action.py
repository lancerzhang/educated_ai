import constants
import logging
import random
from pynput.mouse import Button, Controller

logger = logging.getLogger('Action')
logger.setLevel(logging.INFO)


class Action(object):
    LEFT_CLICK = 'lcl'

    def __init__(self, bm):
        self.mouse = Controller()
        self.bio_memory = bm

    def process(self, working_memories, sequential_time_memories, work_status, button):
        actor_mouse_memories = [mem for mem in working_memories if
                                constants.MEMORY_DURATION in mem and
                                mem[constants.MEMORY_DURATION] is constants.SLICE_MEMORY and
                                mem[constants.STATUS] is constants.MATCHING and
                                constants.PHYSICAL_MEMORY_TYPE in mem and
                                mem[constants.PHYSICAL_MEMORY_TYPE] is constants.ACTION_MOUSE]

        if len(actor_mouse_memories) > 0:
            new_slice_memory = self.match_actor_mouse_memories(actor_mouse_memories)
            self.bio_memory.add_new_slice_memory(new_slice_memory, sequential_time_memories, working_memories)

        if button is constants.MOUSE_LEFT:
            new_slice_memory = self.feel_left_click()
            self.bio_memory.add_new_slice_memory(new_slice_memory, sequential_time_memories, working_memories)
        elif not work_status[constants.BUSY][constants.MEDIUM_DURATION] or not work_status[constants.REWARD]:
            self.explore()

    def match_actor_mouse_memories(self, memories):
        slice_memory = memories[0]
        physical_memories = self.bio_memory.get_live_sub_memories(slice_memory, constants.CHILD_MEM)
        if len(physical_memories) < 1:
            return
        physical_memory = physical_memories[0]  # assume only one feature memory
        logger.info('reproduce actor_mouse_memories {0}'.format(physical_memory))
        click_type = physical_memory[constants.CLICK_TYPE]
        if click_type is self.LEFT_CLICK:
            self.mouse.click(Button.left)
            self.bio_memory.recall_memory(physical_memory)
            self.bio_memory.recall_memory(slice_memory)
            return slice_memory
        return None

    def feel_left_click(self):
        logger.debug('feel_left_click')
        click_type = self.LEFT_CLICK
        physical_memory = self.bio_memory.get_action_mouse_memory(click_type)
        if physical_memory is None:
            action = {constants.PHYSICAL_MEMORY_TYPE: constants.ACTION_MOUSE, constants.CLICK_TYPE: click_type}
            action_memory = self.bio_memory.add_physical_memory(action)
        else:
            self.bio_memory.recall_memory(physical_memory)
            action_memory = physical_memory
        slice_memory = self.bio_memory.add_collection_memory(constants.SLICE_MEMORY, [action_memory], constants.ACTION_MOUSE)
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
