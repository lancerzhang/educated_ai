import logging
import random

from pynput.mouse import Button, Controller

from . import constants
from . import util
from .brain import Brain
from .memory import Memory
from .memory import MemoryType
from .memory import RealType

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
        physical_memories = self.brain.get_matched_slice_memories(RealType.ACTION_MOUSE_CLICK)
        for m in physical_memories:
            for c in m.children:
                self.reproduce_mouse_click(c)
            m.post_matched()

    @util.timeit
    def reproduce_mouse_click(self, m: Memory):
        if m.click_type == constants.LEFT_CLICK:
            self.left_click()
            m.matched()
            m.post_matched()

    @util.timeit
    def feel_clicks(self, click):
        q = Memory(MemoryType.REAL, real_type=RealType.ACTION_MOUSE_CLICK, click_type=click)
        m = self.brain.put_memory(q)
        self.brain.compose_memory([m], MemoryType.SLICE, real_type=RealType.ACTION_MOUSE_CLICK)

    @util.timeit
    def left_click(self):
        self.mouse.click(Button.left)

    @util.timeit
    def explore(self):
        ri = random.randint(0, 100)
        if ri > 0:
            return
        self.left_click()
