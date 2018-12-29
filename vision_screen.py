from vision import Vision
import cv2
import mss
import numpy as np


class ScreenVision(Vision):
    sct = None

    def __init__(self, ds):
        self.sct = mss.mss()
        monitor = self.sct.monitors[1]
        self.SCREEN_WIDTH = monitor['width']
        self.SCREEN_HEIGHT = monitor['height']
        create_window() # Mac
        super(ScreenVision, self).__init__(ds)

    def grab(self, top, left, width, height):
        mon = {"top": top, "left": left, "width": width, "height": height}
        img = self.sct.grab(mon)
        return np.array(img)


def create_window():
    # Create a black image
    img = np.zeros((300, 300, 3), np.uint8)
    # Write some Text
    font = cv2.FONT_HERSHEY_SIMPLEX
    bottom_left_corner_of_text = (50, 50)
    font_scale = 1
    font_color = (255, 255, 255)
    cv2.putText(img, 'Hello World!',
                bottom_left_corner_of_text,
                font,
                font_scale,
                font_color)
