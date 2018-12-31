from vision import Vision
import cv2


class VideoFileVision(Vision):

    def __init__(self, ds, file_path):
        self.file_path = file_path
        self.cap = cv2.VideoCapture(file_path)
        self.SCREEN_WIDTH = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.SCREEN_HEIGHT = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame = None
        super(VideoFileVision, self).__init__(ds)

    def process(self, working_memories, sequential_time_memories, work_status, key):
        # print self.current_block
        ret, self.frame = self.cap.read()
        if self.frame is None:
            self.cap = cv2.VideoCapture(self.file_path)
            ret, self.frame = self.cap.read()

        super(VideoFileVision, self).process(working_memories, sequential_time_memories, work_status, key)
        cv2.rectangle(self.frame, (self.current_block[self.START_X], self.current_block[self.START_Y]),
                      (self.current_block[self.START_X] + self.current_block[self.WIDTH],
                       self.current_block[self.START_Y] + self.current_block[self.HEIGHT]), (0, 255, 0), 1)
        cv2.namedWindow("frame", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow('frame', self.frame)
        cv2.waitKey(1)

    def grab(self, top, left, width, height):
        return self.frame[top:top + height, left:left + width]
