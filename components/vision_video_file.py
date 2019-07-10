from .vision import Vision
from . import util
import mss
import cv2


class VideoFileVision(Vision):

    @util.timeit
    def __init__(self, bm, file_path, status_controller):
        self.file_path = file_path
        self.cap = cv2.VideoCapture(file_path)
        self.FRAME_WIDTH = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.FRAME_HEIGHT = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        status_controller.video_fps = fps
        self.source_frame = None
        sct = mss.mss()
        monitor = sct.monitors[1]
        self.monitor_width = monitor['width']
        super(VideoFileVision, self).__init__(bm)

    @util.timeit
    def process(self, status_controller, key):
        frame = status_controller.video_frame
        status_controller.video_frame = frame + 1
        ret, self.source_frame = self.cap.read()
        if self.source_frame is None:
            self.cap = cv2.VideoCapture(self.file_path)
            ret, self.source_frame = self.cap.read()
            status_controller.video_frame = 1

        focus = super(VideoFileVision, self).process(status_controller, key)
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
        cv2.waitKey(1)
        return focus

    @util.timeit
    def grab(self, top, left, width, height):
        top = int(top)
        left = int(left)
        width = int(width)
        height = int(height)
        return self.source_frame[top:top + height, left:left + width]
