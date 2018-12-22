from vision import Vision
import mss
import numpy as np


class ScreenVision(Vision):
    sct = None

    def __init__(self, ds):
        self.sct = mss.mss()
        monitor = self.sct.monitors[1]
        self.SCREEN_WIDTH = monitor['width']
        self.SCREEN_HEIGHT = monitor['height']
        super(ScreenVision, self).__init__(ds)

    def grab(self, top, left, width, height):
        mon = {"top": top, "left": left, "width": width, "height": height}
        img = self.sct.grab(mon)
        return np.array(img)
