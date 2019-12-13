from .vision import Vision
from . import util
import cv2
import logging
import mss
import time


class VideoFileVision(Vision):

    @util.timeit
    def __init__(self, brain, favor, file_path, status):
        self.file_path = file_path
        self.cap = cv2.VideoCapture(file_path)
        self.FRAME_WIDTH = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.FRAME_HEIGHT = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        status.video_fps = fps
        self.source_frame = None
        sct = mss.mss()
        monitor = sct.monitors[1]
        self.monitor_width = monitor['width']
        super(VideoFileVision, self).__init__(brain, favor)

    @util.timeit
    def process(self, status, key):
        frame = status.video_frame
        status.video_frame = frame + 1
        ret, self.source_frame = self.cap.read()
        if self.source_frame is None:
            self.cap = cv2.VideoCapture(self.file_path)
            ret, self.source_frame = self.cap.read()
            status.video_frame = 1

        focus = super(VideoFileVision, self).process(status, key)
        display_frame = self.source_frame.copy()
        cv2.rectangle(display_frame, (self.current_block[self.START_X], self.current_block[self.START_Y]),
                      (self.current_block[self.START_X] + self.current_block[self.WIDTH],
                       self.current_block[self.START_Y] + self.current_block[self.HEIGHT]), (0, 255, 0), 1)

        if self.monitor_width == self.FRAME_WIDTH:
            cv2.namedWindow("frame", cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty("frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.namedWindow("frame", cv2.WND_PROP_AUTOSIZE)
            cv2.setWindowProperty("frame", cv2.WND_PROP_AUTOSIZE, cv2.WND_PROP_AUTOSIZE)
        cv2.imshow('frame', display_frame)
        t1 = time.time()
        cv2.waitKey(1)  # TODO why it take long time to process after running for a while?
        t2 = time.time()
        if t2 - t1 > 0.1:
            logging.info(f'VideoFileVision.process take long time "{t2 - t1}" for cv2.waitKey(1)')
        return focus

    @util.timeit
    def grab(self, top, left, width, height):
        top = int(top)
        left = int(left)
        width = int(width)
        height = int(height)
        return self.source_frame[top:top + height, left:left + width]
