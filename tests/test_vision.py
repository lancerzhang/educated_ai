import unittest, vision, memory, cv2, constants, time, math
import numpy as np
from data_adaptor import DataAdaptor
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from db_tinydb import DB_TinyDB
from vision import Vision


class TestVision(unittest.TestCase):
    data = None
    database = None

    def setUp(self):
        database = DB_TinyDB(TinyDB(storage=MemoryStorage))
        self.data = DataAdaptor(database)
        memory.forget_memory = False
        memory.data_adaptor = self.data
        self.vision = Vision(self.data)

    def test_filter_feature1(self):
        data = np.array([[10, 20, 30, 40, 50, 60],
                         [0, 0, 0, 0, 0, 0],
                         [50, 60, 70, 80, 0, 0],
                         [0, 0, 0, 0, 0, 0],
                         [50, 60, 70, 80, 0, 0],
                         [0, 0, 0, 0, 0, 0]], dtype='uint8')
        kernel1 = '0,0,0,0,1,0,0,0,0'
        feature_data1 = self.vision.filter_feature(data, kernel1)
        self.assertIsNotNone(feature_data1)
        self.assertEquals(3, len(feature_data1))

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
        feature_data1_1 = self.vision.filter_feature(img1_1, kernel3)
        feature_data1_2 = self.vision.filter_feature(img1_2, kernel3, feature_data1_1[constants.FEATURE])
        feature_data1_1 = self.vision.filter_feature(img1_1, kernel3)
        feature_data2_1 = self.vision.filter_feature(img2_1, kernel3, feature_data1_1[constants.FEATURE])
        self.assertTrue(feature_data1_2[constants.SIMILAR])
        self.assertFalse(feature_data2_1[constants.SIMILAR])
        # TODO
        feature_data2_2 = self.vision.filter_feature(img2_2, kernel3, feature_data2_1[constants.FEATURE])
        feature_data3_1 = self.vision.filter_feature(img3_1, kernel3)
        feature_data3_2 = self.vision.filter_feature(img3_2, kernel3, feature_data3_1[constants.FEATURE])
        self.assertTrue(feature_data3_2[constants.SIMILAR])
        feature_data4_1 = self.vision.filter_feature(img4_1, kernel3)
        feature_data4_2 = self.vision.filter_feature(img4_2, kernel3, feature_data4_1[constants.FEATURE])
        self.assertTrue(feature_data4_2[constants.SIMILAR])

    def test_get_rank(self):
        kernel = self.vision.get_kernel()
        self.assertIsNotNone(kernel)
        channel = self.vision.get_channel()
        self.assertIsNotNone(channel)
        degrees = self.vision.get_degrees()
        self.assertIsNotNone(degrees)
        speed = self.vision.get_speed()
        self.assertIsNotNone(speed)
        duration = self.vision.get_duration()
        self.assertIsNotNone(duration)

    def test_get_channel_region(self):
        bgr = cv2.imread('p1-1.jpg', 1)
        channel_img = vision.get_channel_img(bgr, 'y')
        self.assertIsNotNone(channel_img)

    def test_update_memory_indexes(self):
        kernel1 = '0,0,0,0,1,0,0,0,0'
        self.vision.update_memory_indexes('y', kernel1, 'id1')
        memory_indexes = self.vision.memory_indexes
        self.assertGreater(len(memory_indexes), 0)
        kernel2 = '0,0,0,0,1,0,0,0,0'
        self.vision.update_memory_indexes('y', kernel2, 'id2')
        element = next((x for x in memory_indexes if x[constants.KERNEL] == kernel2 and x[constants.CHANNEL] == 'y'),
                       None)
        self.assertEquals(2, len(element[constants.MEMORIES]))

    def test_search_memory(self):
        img1_1 = cv2.imread('p1-1.jpg', 0)
        img1_2 = cv2.imread('p1-2.jpg', 0)
        kernel = '-1,-1,1,-1,-1,0,1,0,1'
        feature_data1_1 = self.vision.filter_feature(img1_1, kernel)
        feature_data1_2 = self.vision.filter_feature(img1_2, kernel)
        channel = 'y'
        mem = memory.add_vision_feature_memory(constants.VISION_FEATURE, channel, kernel,
                                               feature_data1_1[constants.FEATURE])
        self.vision.update_memory_indexes(channel, kernel, mem[constants.MID])
        self.vision.update_memory_indexes(channel, kernel, '123')
        new_mem = self.vision.search_feature_memory(channel, kernel, feature_data1_2[constants.FEATURE])
        self.assertIsNotNone(new_mem)

    def test_calculate_degrees(self):
        self.vision.current_block = {self.vision.START_X: 100, self.vision.START_Y: 100}
        new_block1 = {self.vision.START_X: 110, self.vision.START_Y: 110}
        degrees1 = self.vision.calculate_degrees(new_block1)
        self.assertEqual(5, degrees1)
        new_block2 = {self.vision.START_X: 117.32, self.vision.START_Y: 110}
        degrees2 = self.vision.calculate_degrees(new_block2)
        self.assertEqual(3, int(degrees2))
        new_block3 = {self.vision.START_X: 110, self.vision.START_Y: 90}
        degrees3 = self.vision.calculate_degrees(new_block3)
        self.assertEqual(-5, degrees3)
        new_block4 = {self.vision.START_X: 90, self.vision.START_Y: 110}
        degrees4 = self.vision.calculate_degrees(new_block4)
        self.assertEqual(14, degrees4)
        new_block5 = {self.vision.START_X: 100, self.vision.START_Y: 110}
        degrees5 = self.vision.calculate_degrees(new_block5)
        self.assertEqual(9, degrees5)
        new_block6 = {self.vision.START_X: 90, self.vision.START_Y: 100}
        degrees6 = self.vision.calculate_degrees(new_block6)
        self.assertEqual(18, degrees6)

    def test_calculate_action(self):
        self.vision.SCREEN_WIDTH = 1920
        self.vision.SCREEN_HEIGHT = 1080
        action = self.vision.current_action.copy()
        action[self.vision.CREATE_TIME] = time.time() - 0.2
        action[constants.DEGREES] = 3
        action[constants.SPEED] = 2
        action[constants.DURATION] = 2
        self.vision.current_block = {self.vision.START_X: 100, self.vision.START_Y: 100, self.vision.WIDTH: 50,
                                     self.vision.HEIGHT: 50}
        self.vision.calculate_action(action)
        self.assertEqual(110, self.vision.current_block[self.vision.START_Y])
        self.assertEqual(117, int(self.vision.current_block[self.vision.START_X]))
        self.vision.current_block = {self.vision.START_X: 1900, self.vision.START_Y: 1000, self.vision.WIDTH: 100,
                                     self.vision.HEIGHT: 100}
        action[self.vision.CREATE_TIME] = time.time() - 5
        self.vision.calculate_action(action)
        self.assertEqual(980, self.vision.current_block[self.vision.START_Y])
        self.assertEqual(1820, int(self.vision.current_block[self.vision.START_X]))
        self.assertEqual(self.vision.COMPLETED, action[self.vision.STATUS])

    def test_calculate_action_degrees(self):
        self.vision.SCREEN_WIDTH = 1920
        self.vision.SCREEN_HEIGHT = 1080
        cx = 100
        cy = 100
        self.vision.current_block = {self.vision.START_X: cx, self.vision.START_Y: cy, self.vision.WIDTH: 50,
                                     self.vision.HEIGHT: 50}
        sx = 17
        sy = 10
        nx = cx + sx
        ny = cy + sy
        new_block1 = {self.vision.START_X: nx, self.vision.START_Y: ny}
        degrees1 = self.vision.calculate_degrees(new_block1)
        self.assertEqual(3, degrees1)
        action = self.vision.current_action.copy()
        duration = 1
        action[self.vision.CREATE_TIME] = time.time() - duration
        action[constants.DEGREES] = degrees1
        action[constants.SPEED] = math.sqrt(sx * sx + sy * sy) / constants.ACTUAL_SPEED_TIMES
        action[constants.DURATION] = duration
        self.vision.calculate_action(action)
        self.assertEqual(nx, self.vision.current_block[self.vision.START_X])
        self.assertEqual(ny, self.vision.current_block[self.vision.START_Y])

    def test_set_movement_absolute(self):
        self.vision.current_block = {self.vision.START_X: 100, self.vision.START_Y: 100}
        new_block1 = {self.vision.START_X: 130, self.vision.START_Y: 140}
        self.vision.set_movement_absolute(new_block1, 1)
        self.assertEqual(1, self.vision.current_action[constants.SPEED])

    def test_calculate_block_histogram(self):
        img1 = cv2.imread('rgb1.jpg', 0)
        height, width = img1.shape
        self.vision.SCREEN_WIDTH = width
        self.vision.SCREEN_HEIGHT = height
        self.vision.NUMBER_SUB_REGION = 2
        hist1 = self.vision.calculate_block_histogram(img1)
        self.assertEqual(4, len(hist1))

    def test_find_most_variable_region(self):
        img1 = cv2.imread('rgb1.jpg', 0)
        height, width = img1.shape
        self.vision.SCREEN_WIDTH = width
        self.vision.SCREEN_HEIGHT = height
        self.vision.NUMBER_SUB_REGION = 2
        hist1 = self.vision.calculate_block_histogram(img1)
        self.vision.previous_block_histogram = hist1
        self.vision.current_block = {self.vision.START_X: 0, self.vision.START_Y: 0, self.vision.WIDTH: 8,
                                     self.vision.HEIGHT: 8}
        img2 = cv2.imread('rgb2.jpg', 1)
        block = self.vision.find_most_variable_region(img2)
        self.assertEqual(width / 2, block[self.vision.START_X])
        self.assertEqual(height / 2, block[self.vision.START_Y])

    def test_zoom_in(self):
        self.vision.roi_index = 1
        self.vision.zoom_in()
        self.assertEqual(0, self.vision.roi_index)
        self.vision.roi_index = 0
        self.vision.zoom_in()
        self.assertEqual(0, self.vision.roi_index)

    def test_zoom_out(self):
        self.vision.SCREEN_WIDTH = 200
        self.vision.SCREEN_HEIGHT = 200
        self.vision.current_block = {self.vision.START_X: 100, self.vision.START_Y: 100, self.vision.WIDTH: 50,
                                     self.vision.HEIGHT: 50}
        self.vision.roi_index = 0
        self.vision.zoom_out()
        self.assertEqual(1, self.vision.roi_index)
        max_index = len(self.vision.ROI_ARR) - 1
        self.vision.roi_index = max_index
        self.vision.zoom_out()
        self.assertEqual(max_index, self.vision.roi_index)
        self.vision.roi_index = 2
        self.vision.zoom_out()
        self.assertEqual(2, self.vision.roi_index)

    def test_get_duration(self):
        result = self.vision.get_duration()
        self.assertGreater(result, 0)
        self.assertLess(result, 0.6)


if __name__ == "__main__":
    unittest.main()
