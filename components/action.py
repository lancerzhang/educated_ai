from . import constants
from . import memory
from . import util
from .brain import Brain
from .memory import Memory
import logging
import random
from pynput.mouse import Button, Controller

logger = logging.getLogger('Action')
logger.setLevel(logging.INFO)


class Action(object):

    @util.timeit
    def __init__(self, brain: Brain):
        self.brain = brain
        self.mouse = Controller()

    @util.timeit
    def process(self, click, focus):
        self.reproduce_mouse_clicks()
        if focus:
            self.move(focus)
        if click:
            self.feel_clicks(click)
        self.explore()

    @util.timeit
    def move(self, focus):
        self.mouse.position = (focus[constants.FOCUS_X], focus[constants.FOCUS_Y])

    @util.timeit
    def reproduce_mouse_clicks(self):
        physical_memories = self.brain.get_matching_feature_memories(constants.ACTION_MOUSE_CLICK)
        for m in physical_memories:
            self.reproduce_mouse_click(m)

    @util.timeit
    def reproduce_mouse_click(self, m: Memory):
        if m.click_type == constants.LEFT_CLICK:
            self.left_click()
            m.status = constants.MATCHED

    @util.timeit
    def feel_clicks(self, click):
        q = Memory()
        q.set_feature_type(constants.ACTION_MOUSE_CLICK)
        q.click_type = click
        m = self.brain.put_physical_memory(q)
        self.brain.put_virtual_memory([m], constants.SLICE_MEMORY)

    @util.timeit
    def left_click(self):
        self.mouse.click(Button.left)

    @util.timeit
    def explore(self):
        ri = random.randint(0, 100)
        if ri > 0:
            return
        self.left_click()
