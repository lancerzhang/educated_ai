import hashlib
import time

import cv2
import mss

from . import util
from .vision import Vision


class VideoFileVision(Vision):

    @util.timeit
    def __init__(self, file_path, is_show):
        self.file_path = file_path
        self.is_show = is_show
        self.play_start_time = time.time()
        self.cap = cv2.VideoCapture(file_path)
        self.FRAME_WIDTH = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.FRAME_HEIGHT = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = round(self.cap.get(cv2.CAP_PROP_FPS))
        self.source_frame = None
        # sct = mss.mss()
        # monitor = sct.monitors[1]
        # self.monitor_width = monitor['width']
        super(VideoFileVision, self).__init__()

    @util.timeit
    def receive(self):
        return

    @util.timeit
    def process(self):
        return
        # frame = status.video_frame
        # status.video_frame = frame + 1
        # ret, self.source_frame = self.cap.read()
        # if self.source_frame is None:
        #     self.cap = cv2.VideoCapture(self.file_path)
        #     ret, self.source_frame = self.cap.read()
        #     status.video_frame = 1
        #
        # focus = super(VideoFileVision, self).process(status, key)
        # if self.is_show is 'n':
        #     return focus
        #
        # display_frame = self.source_frame.copy()
        # cv2.rectangle(display_frame, (self.current_block.x, self.current_block.y),
        #               (self.current_block.x + self.current_block.w,
        #                self.current_block.y + self.current_block.h), (0, 255, 0), 1)
        #
        # if self.monitor_width == self.FRAME_WIDTH:
        #     cv2.namedWindow("frame", cv2.WND_PROP_FULLSCREEN)
        #     cv2.setWindowProperty("frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        # else:
        #     cv2.namedWindow("frame", cv2.WND_PROP_AUTOSIZE)
        #     cv2.setWindowProperty("frame", cv2.WND_PROP_AUTOSIZE, cv2.WND_PROP_AUTOSIZE)
        # cv2.imshow('frame', display_frame)
        # t1 = time.time()
        # cv2.waitKey(1)  # TODO why it take long time to process after running for a while?
        # t2 = time.time()
        # if t2 - t1 > 0.1:
        #     logging.info(f'VideoFileVision.process take long time "{t2 - t1}" for cv2.waitKey(1)')
        # return focus

    @util.timeit
    def grab(self, top, left, width, height):
        top = int(top)
        left = int(left)
        width = int(width)
        height = int(height)
        img = self.source_frame[top:top + height, left:left + width]
        img = img.copy(order='C')
        cv2.imwrite(f'debug/img/{hashlib.sha1(img).hexdigest()}.jpg', img)
        return img
