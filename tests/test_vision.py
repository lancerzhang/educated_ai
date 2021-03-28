import cv2
import math
import time
import unittest
from multiprocessing import Pool

import numpy as np

from src import vision, constants
from src.brain import Brain
from src.featurepack import FeaturePack
from src.vision import Block
from src.vision import Vision


def filter_feature(kernel, data, contrast=None, channel='g'):
    data_map = {channel: data}
    fp = FeaturePack(kernel=kernel, data=data_map, contrast=contrast, channel=channel)
    return vision.filter_feature(fp)


def np_histogram(img):
    # hist_np, bins = np.histogram(img.ravel(), 27, range=[0, 256])
    hist_np = np.bincount(img.ravel())
    return hist_np


class TestVision(unittest.TestCase):

    def setUp(self):
        brain1 = Brain()
        vision1 = Vision(brain1)
        vision1.FRAME_WIDTH = 1920
        vision1.FRAME_HEIGHT = 1080
        vision1.init_current_block()
        self.vision1 = vision1

    def test_filter_feature1(self):
        data = np.array([[10, 20, 30, 40, 50, 60],
                         [0, 0, 0, 0, 0, 0],
                         [50, 60, 70, 80, 0, 0],
                         [0, 0, 0, 0, 0, 0],
                         [50, 60, 70, 80, 0, 0],
                         [0, 0, 0, 0, 0, 0]], dtype='uint8')
        kernel1 = '0,0,0,0,1,0,0,0,0'
        feature_data1 = filter_feature(kernel=kernel1, data=data)
        self.assertIsNotNone(feature_data1)

    def test_filter_feature(self):
        img1_1 = cv2.imread('p1-1.jpg', 0)
        img1_2 = cv2.imread('p1-2.jpg', 0)
        img2_1 = cv2.imread('p2-1.jpg', 0)
        img2_2 = cv2.imread('p2-2.jpg', 0)
        img3_1 = cv2.imread('p3-1.jpg', 0)
        img3_2 = cv2.imread('p3-2.jpg', 0)
        img4_1 = cv2.imread('p4-1.jpg', 0)
        img4_2 = cv2.imread('p4-2.jpg', 0)
        kernel3 = '-1,-1,1,-1,-1,0,1,0,1'
        fp1_1 = filter_feature(kernel=kernel3, data=img1_1)
        fp1_2 = filter_feature(kernel=kernel3, data=img1_2, contrast=fp1_1.pack)
        self.assertTrue(fp1_2.similar)
        fp2_1 = filter_feature(kernel=kernel3, data=img2_1, contrast=fp1_1.pack)
        # self.assertFalse(fp2_1.similar)
        # TODO
        feature_data2_2 = filter_feature(kernel=kernel3, data=img2_2, contrast=fp2_1.pack)
        feature_data3_1 = filter_feature(kernel=kernel3, data=img3_1)
        feature_data3_2 = filter_feature(kernel=kernel3, data=img3_2, contrast=feature_data3_1.pack)
        self.assertTrue(feature_data3_2.similar)
        feature_data4_1 = filter_feature(kernel=kernel3, data=img4_1)
        feature_data4_2 = filter_feature(kernel=kernel3, data=img4_2, contrast=feature_data4_1.pack)
        self.assertTrue(feature_data4_2.similar)

    def test_get_rank(self):
        kernel = self.vision1.get_kernel()
        self.assertIsNotNone(kernel)
        channel = self.vision1.get_channel()
        self.assertIsNotNone(channel)
        degrees = self.vision1.get_degrees()
        self.assertIsNotNone(degrees)
        speed = self.vision1.get_speed()
        self.assertIsNotNone(speed)
        duration = self.vision1.get_duration()
        self.assertIsNotNone(duration)

    def test_get_channel_region(self):
        bgr = cv2.imread('p1-1.jpg', 1)
        channel_img = vision.get_channel_img(bgr, 'y')
        self.assertIsNotNone(channel_img)

    def test_calculate_degrees(self):
        self.vision1.current_block = Block(100, 100)
        new_block1 = Block(110, 110)
        degrees1 = self.vision1.calculate_degrees(new_block1)
        self.assertEqual(4, degrees1)
        new_block2 = Block(117.32, 110)
        degrees2 = self.vision1.calculate_degrees(new_block2)
        self.assertEqual(3, int(degrees2))
        new_block3 = Block(110, 90)
        degrees3 = self.vision1.calculate_degrees(new_block3)
        self.assertEqual(-4, degrees3)
        new_block4 = Block(90, 110)
        degrees4 = self.vision1.calculate_degrees(new_block4)
        self.assertEqual(14, degrees4)
        new_block5 = Block(100, 110)
        degrees5 = self.vision1.calculate_degrees(new_block5)
        self.assertEqual(9, degrees5)
        new_block6 = Block(90, 100)
        degrees6 = self.vision1.calculate_degrees(new_block6)
        self.assertEqual(18, degrees6)

    def test_calculate_action(self):
        action = self.vision1.current_action.copy()
        action[self.vision1.LAST_MOVE_TIME] = time.time() - 0.2
        action[constants.DEGREES] = 3
        action[constants.SPEED] = 2
        action[constants.MOVE_DURATION] = 2
        self.vision1.current_block = Block(100, 100, w=50, h=50)
        self.vision1.calculate_move_action(action)
        self.assertEqual(110, self.vision1.current_block.y)
        self.assertEqual(117, int(self.vision1.current_block.x))
        self.vision1.current_block = Block(1900, 1000, w=100, h=100)
        action[self.vision1.LAST_MOVE_TIME] = time.time() - 5
        self.vision1.calculate_move_action(action)
        self.assertEqual(1000, self.vision1.current_block.y)
        self.assertEqual(1900, int(self.vision1.current_block.x))
        self.assertEqual(self.vision1.COMPLETED, action[self.vision1.STATUS])

    def test_calculate_action_degrees(self):
        current_x = 100
        current_y = 100
        self.vision1.current_block = Block(current_x, current_y, w=50, h=50)
        step_x = 17
        step_y = 10
        new_x = current_x + step_x
        new_y = current_y + step_y
        new_block1 = Block(new_x, new_y)
        degrees1 = self.vision1.calculate_degrees(new_block1)
        self.assertEqual(3, degrees1)
        action = self.vision1.current_action.copy()
        duration = 1
        action[self.vision1.LAST_MOVE_TIME] = time.time() - duration
        action[constants.DEGREES] = degrees1
        action[constants.SPEED] = math.sqrt(step_x * step_x + step_y * step_y) / vision.ACTUAL_SPEED_TIMES
        action[constants.MOVE_DURATION] = duration
        self.vision1.calculate_move_action(action)
        self.assertEqual(new_x, self.vision1.current_block.x)
        self.assertEqual(new_y, self.vision1.current_block.y)

    def test_set_movement_absolute(self):
        self.vision1.current_block = Block(100, 100)
        new_block1 = Block(130, 140)
        self.vision1.set_movement_absolute(new_block1, 1)
        self.assertEqual(1, self.vision1.current_action[constants.SPEED])

    def test_calculate_block_histogram(self):
        img0 = cv2.imread('1920a.jpg', 0)
        height, width = img0.shape
        self.vision1.FRAME_WIDTH = width
        self.vision1.FRAME_HEIGHT = height
        img1 = cv2.imread('1920a.jpg', 1)
        hist1 = self.vision1.calculate_blocks_histogram(img1, 2, 2, width // 2, height // 2)
        self.assertEqual(4, len(hist1))

    def test_np_histogram(self):
        img0 = cv2.imread('1920a.jpg', 0)
        pool = Pool()
        time1 = time.time()
        inputs = []
        for _ in range(0, 4):
            # np_histogram(img0)
            inputs.append(img0)
        it = pool.imap_unordered(np_histogram, inputs)
        rs = list(it)
        time2 = time.time()
        print(f'used {(time2 - time1) * 1000} ms')
        # print(rs)

    def test_find_most_variable_block_division(self):
        img0 = cv2.imread('1920a.jpg', 0)
        height, width = img0.shape
        self.vision1.FRAME_WIDTH = width
        self.vision1.FRAME_HEIGHT = height
        img1 = cv2.imread('1920a.jpg', 1)
        img2 = cv2.imread('1920b.jpg', 1)
        self.vision1.previous_full_image = img1
        focus_width = 12
        self.vision1.previous_histogram1 = self.vision1.calculate_blocks_histogram(img1, 12, 12, width // 2,
                                                                                   height // 2)
        self.vision1.current_block = Block(0, 0, w=focus_width, h=focus_width)
        start = time.time()
        block = self.vision1.find_most_variable_block_division(img2, 0, 0, width, height, focus_width, focus_width)
        print('test_find_most_variable_block_division used time:{0}'.format(time.time() - start))
        self.assertEqual(423, block.x)
        self.assertEqual(212, block.y)

    def test_sum_block_histogram(self):
        cells_histogram = np.array([[1], [2], [3], [4], [1], [2], [3], [4], [1], [2], [3], [4], [1], [2], [3], [4]])
        self.vision1.ROI_ARR[0] = 1
        self.vision1.FRAME_WIDTH = 4
        self.vision1.FRAME_HEIGHT = 4
        self.vision1.current_block = Block(0, 0, w=2, h=2)
        blocks_histogram = self.vision1.sum_blocks_histogram(cells_histogram)
        self.assertEqual(6, blocks_histogram[0])
        self.assertEqual(14, blocks_histogram[1])
        self.assertEqual(6, blocks_histogram[2])
        self.assertEqual(14, blocks_histogram[3])

    def test_try_zoom_in(self):
        new_block = self.vision1.try_zoom_in(Vision.ZOOM_LEFT_TOP)
        self.assertEqual(self.vision1.current_block.ri - 1, new_block.ri)
        self.vision1.current_block.ri = 0
        new_block = self.vision1.try_zoom_in(Vision.ZOOM_LEFT_TOP)
        self.assertIsNone(new_block)

    def test_try_zoom_out(self):
        self.vision1.FRAME_WIDTH = 200
        self.vision1.FRAME_HEIGHT = 200
        self.vision1.current_block = Block(100, 100, w=50, h=50)
        self.vision1.current_block.ri = 0
        new_block = self.vision1.try_zoom_out(Vision.ZOOM_RIGHT_BOTTOM)
        self.assertEqual(1, new_block.ri)
        max_index = len(self.vision1.ROI_ARR) - 1
        self.vision1.current_block.ri = max_index
        new_block = self.vision1.try_zoom_out(Vision.ZOOM_RIGHT_BOTTOM)
        self.assertIsNone(new_block)
        self.vision1.current_block.ri = 2
        new_block = self.vision1.try_zoom_out(Vision.ZOOM_RIGHT_BOTTOM)
        self.assertIsNone(new_block)

    def test_get_duration(self):
        result = self.vision1.get_duration()
        self.assertGreater(result, 0)
        self.assertLess(result, 0.6)

    def test_calculate_feature_process_status(self):
        self.vision1.last_focus_state_time = time.time() - self.vision1.PROCESS_STABLE_DURATION + 0.1
        self.vision1.calculate_vision_focus_state()
        self.assertEqual(self.vision1.PROCESS_STATUS_NORMAL, self.vision1.focus_status)
        self.vision1.last_focus_state_time = time.time() - self.vision1.PROCESS_STABLE_DURATION - 0.1
        self.vision1.calculate_vision_focus_state()
        self.assertEqual(self.vision1.PROCESS_STATUS_DIGGING, self.vision1.focus_status)
        self.vision1.last_focus_state_time = time.time() - self.vision1.PROCESS_STABLE_DURATION * 2 - 0.1
        self.vision1.calculate_vision_focus_state()
        self.assertEqual(self.vision1.PROCESS_STATUS_EXPLORING, self.vision1.focus_status)


if __name__ == "__main__":
    unittest.main()
