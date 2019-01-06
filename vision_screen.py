from vision import Vision
import logging
import mss
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')


class ScreenVision(Vision):

    def __init__(self, ds):
        logging.info('start to capture screen.')
        self.sct = mss.mss()
        monitor = self.sct.monitors[1]
        self.SCREEN_WIDTH = monitor['width']
        self.SCREEN_HEIGHT = monitor['height']
        super(ScreenVision, self).__init__(ds)

    def grab(self, top, left, width, height):
        mon = {"top": top, "left": left, "width": width, "height": height}
        img = self.sct.grab(mon)
        return np.array(img)
