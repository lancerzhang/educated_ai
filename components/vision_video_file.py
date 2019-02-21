from vision import Vision
import constants
import cv2
import logging


class VideoFileVision(Vision):

    def __init__(self, bm, file_path, video_file_info):
        logging.info('start to load video file')
        self.file_path = file_path
        self.cap = cv2.VideoCapture(file_path)
        self.SCREEN_WIDTH = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.SCREEN_HEIGHT = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_file_info.update({constants.total_frames: frames})
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        video_file_info.update({constants.fps: fps})
        self.video_info = video_file_info
        self.source_frame = None
        super(VideoFileVision, self).__init__(bm)

    def process(self, work_status, key):
        frame = self.video_info[constants.current_frame]
        self.video_info.update({constants.current_frame: frame + 1})
        ret, self.source_frame = self.cap.read()
        if self.source_frame is None:
            self.cap = cv2.VideoCapture(self.file_path)
            ret, self.source_frame = self.cap.read()
            self.video_info.update({constants.current_frame: 1})

        super(VideoFileVision, self).process(work_status, key)
        display_frame = self.source_frame.copy()
        cv2.rectangle(display_frame, (self.current_block[self.START_X], self.current_block[self.START_Y]),
                      (self.current_block[self.START_X] + self.current_block[self.WIDTH],
                       self.current_block[self.START_Y] + self.current_block[self.HEIGHT]), (0, 255, 0), 1)
        cv2.namedWindow("frame", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow('frame', display_frame)
        cv2.waitKey(1)

    def grab(self, top, left, width, height):
        top = int(top)
        left = int(left)
        width = int(width)
        height = int(height)
        return self.source_frame[top:top + height, left:left + width]
