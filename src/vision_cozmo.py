import cozmo
import cv2
import numpy as np

from . import util
from .vision import Vision


class CozmoVision(Vision):
    ready = False
    running = True
    robot = None

    @util.timeit
    def __init__(self, brain, favor):
        self.SCREEN_WIDTH = 320
        self.SCREEN_HEIGHT = 240
        self.ROI_ARR = [10, 20, 40, 80, 160]
        super(CozmoVision, self).__init__(brain, favor)

    def run_cozmo_thread(self):
        print('starting cozmo')
        cozmo.run_program(self.run_cozmo)
        while self.running:
            pass

    def run_cozmo(self, robot: cozmo.robot.Robot):
        print('run_cozmo')
        robot.camera.image_stream_enabled = True
        robot.camera.color_image_enabled = True
        self.robot = robot
        self.ready = True
        print(self.robot)

    @util.timeit
    def process(self, status, key):
        print('process')
        print(self.robot)
        latest_image = self.robot.world.latest_image.raw_image
        cv2.namedWindow("frame", cv2.WND_PROP_AUTOSIZE)
        cv2.setWindowProperty("frame", cv2.WND_PROP_AUTOSIZE, cv2.WND_PROP_AUTOSIZE)
        cv2.imshow('frame', latest_image)
        cv2.waitKey(1)

    @util.timeit
    def grab(self, top, left, width, height):
        latest_image = self.robot.world.latest_image.raw_image
        top = int(top)
        left = int(left)
        width = int(width)
        height = int(height)
        area = (left, top, left + width, top + height)
        return np.array(latest_image.crop(area))
