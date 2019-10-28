from .vision import Vision
from . import util
import mss
import numpy as np


class ScreenVision(Vision):

    @util.timeit
    def __init__(self, brain, favor):
        self.sct = mss.mss()
        monitor = self.sct.monitors[1]
        self.SCREEN_WIDTH = monitor['width']
        self.SCREEN_HEIGHT = monitor['height']
        super(ScreenVision, self).__init__(brain, favor)

    @util.timeit
    def grab(self, top, left, width, height):
        top = int(top)
        left = int(left)
        width = int(width)
        height = int(height)
        mon = {"top": top, "left": left, "width": width, "height": height}
        img = self.sct.grab(mon)
        return np.array(img)
