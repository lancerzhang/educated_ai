from . import constants
from . import util
import logging
import random
from pynput.mouse import Button, Controller

logger = logging.getLogger('Action')
logger.setLevel(logging.INFO)


class Action(object):

    @util.timeit
    def __init__(self, bm):
        self.mouse = Controller()
        self.bio_memory = bm

    @util.timeit
    def process(self, status_controller, click, focus):
        work_status = status_controller.status
        self.reproduce_mouse_clicks()
        if focus:
            self.move(focus)
        if click:
            self.feel_clicks(click)
        elif not work_status[constants.BUSY][constants.MEDIUM_DURATION]:
            self.explore()

    @util.timeit
    def move(self, focus):
        self.mouse.position = (focus[constants.FOCUS_X], focus[constants.FOCUS_Y])

    @util.timeit
    def reproduce_mouse_clicks(self):
        physical_memories = self.bio_memory.prepare_matching_physical_memories(constants.ACTION_MOUSE_CLICK)
        for sbm in physical_memories:
            self.reproduce_mouse_click(sbm)
        self.bio_memory.verify_matching_physical_memories()

    @util.timeit
    def reproduce_mouse_click(self, bm):
        click_type = bm[constants.CLICK_TYPE]
        if click_type == constants.LEFT_CLICK:
            self.left_click()
            bm.update({constants.STATUS: constants.MATCHED})

    @util.timeit
    def feel_clicks(self, click):
        print('*** mouse left click ***')
        bm = self.bio_memory.get_mouse_click_memory(click)
        if bm is None:
            bm = self.bio_memory.add_mouse_click_memory(click)
        else:
            self.bio_memory.recall_physical_memory(bm)
        self.bio_memory.add_slice_memory([bm], bm[constants.PHYSICAL_MEMORY_TYPE])

    @util.timeit
    def left_click(self):
        self.mouse.click(Button.left)

    @util.timeit
    def explore(self):
        ri = random.randint(0, 100)
        if ri > 0:
            return
        self.left_click()
