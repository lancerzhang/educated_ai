import constants
import logging
import random
from pynput.mouse import Button, Controller

logger = logging.getLogger('Action')
logger.setLevel(logging.INFO)


class Action(object):

    def __init__(self, bm):
        self.mouse = Controller()
        self.bio_memory = bm

    def process(self, work_status, click):
        self.reproduce_mouse_clicks()
        if click:
            self.feel_clicks(click)
        elif not work_status[constants.BUSY][constants.MEDIUM_DURATION] or not work_status[constants.REWARD]:
            self.explore()

    def reproduce_mouse_clicks(self):
        physical_memories = self.bio_memory.prepare_matching_memories(constants.ACTION_MOUSE_CLICK)
        for sbm in physical_memories:
            self.reproduce_mouse_click(sbm)
        self.bio_memory.verify_matching_memories()

    def reproduce_mouse_click(self, bm):
        click_type = bm[constants.CLICK_TYPE]
        if click_type is constants.LEFT_CLICK:
            self.left_click()
            bm.update({constants.STATUS: constants.MATCHED})

    def feel_clicks(self, click):
        logger.debug('feel_clicks')
        bm = self.bio_memory.get_mouse_click_memory(click)
        if bm is None:
            bm = self.bio_memory.add_mouse_click_memory(click)
        else:
            self.bio_memory.recall_physical_memory(bm)
        self.bio_memory.add_slice_memory([bm], bm[constants.PHYSICAL_MEMORY_TYPE])

    def left_click(self):
        self.mouse.click(Button.left)

    def explore(self):
        ri = random.randint(0, 100)
        if ri > 0:
            return
        self.left_click()
        logger.debug('explore')
