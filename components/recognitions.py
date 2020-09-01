import cv2
import numpy as np
from scipy.spatial.distance import euclidean
from skimage.metrics import structural_similarity as ssim

from components import util
from components.hsv_color_shapes import ColorShape

IMG_SIZE = 14
CV_THRESHOLD = 64


def resize_img(img):
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    return img


def prepare_img(img):
    ret, img = cv2.threshold(img, CV_THRESHOLD, 255, cv2.THRESH_BINARY)
    if util.img_has_content(img):
        img = util.np_2d_array_nonzero_box(img)
        img = resize_img(img)
        return img


class ImgRgbHistogram:
    # Use 6 instead of 8 to make it faster
    bins = [6, 6, 6]
    similar_threshold = 1

    def __init__(self, img=None, feature=None):
        if feature is not None:
            self.feature = feature
        else:
            self.feature = self.describe(img)

    def describe(self, img):
        img = resize_img(img)
        # compute a 3D histogram in the RGB color space,
        # then normalize the histogram so that images
        # with the same content, but either scaled larger
        # or smaller will have (roughly) the same histogram
        hist = cv2.calcHist([img], [0, 1, 2],
                            None, self.bins, [0, 256, 0, 256, 0, 256])
        # normalize
        hist = cv2.normalize(hist, hist)
        # return out 3D histogram as a flattened array
        return hist.flatten()

    def compare(self, img2):
        feature2 = self.describe(img2)
        return util.chi2_distance(self.feature, feature2)

    def is_similar(self, img2):
        distance = self.compare(img2)
        if distance < self.similar_threshold:
            return True
        else:
            return False


class ImgShapes:
    similar_threshold = 0.4  # 0.6 for threshold 64, 0.8 for threshold 127
    top_colors_hsv = {}

    def __init__(self, img=None, feature=None):
        if feature is not None:
            self.features = [feature]
        else:
            self.features = self.describe(img)

    def describe(self, img):
        if len(img.shape) == 2:
            return self.describe_grey(img)
        else:
            return self.describe_color(img)

    def describe_grey(self, img):
        features = []
        img = prepare_img(img)
        if img is not None:
            features.append(img)
        return features

    def describe_color(self, img):
        img = resize_img(img)
        features = []
        cs = ColorShape(img)
        self.top_colors_hsv = cs.top_colors_hsv
        for k in cs.top_colors_hsv:
            img = cs.get_grey_shape(k)
            img = prepare_img(img)
            if img is not None:
                features.append(img)
        return features

    def compare(self, img2):
        distance = 1000  # max distance
        features2 = self.describe(img2)
        for f1 in self.features:
            for f2 in features2:
                d1 = 1 - ssim(f1, f2)
                if d1 < distance:
                    distance = d1
        return distance

    def is_similar(self, img2):
        distance = self.compare(img2)
        if distance < self.similar_threshold:
            return True
        else:
            return False


def get_euclidean_distance(block1, block2):
    distance = euclidean(block1[0], block2[0]) + euclidean(block1[1], block2[1])
    return distance


class VoiceMfccFrame:
    BLOCK_WIDTH = 2
    BLOCK_HEIGHT = 2
    MIN_ENERGY_UNIT = 10
    MIN_DISTANCE_UNIT = 0.1

    def __init__(self, mfcc=None, feature=None):
        if feature is not None:
            self.features = [feature]
        else:
            self.features = self.describe(mfcc)

    def has_similar_dtw(self, block1, blocks):
        for block2 in blocks:
            distance = get_euclidean_distance(block1, block2)
            if distance < self.MIN_DISTANCE_UNIT * self.BLOCK_WIDTH * self.BLOCK_HEIGHT:
                return True
        return False

    def describe(self, mfcc_frames):
        mfcc_frames = mfcc_frames[:, 1:]
        features = []
        h, w = mfcc_frames.shape
        for i in range(w - self.BLOCK_WIDTH + 1):
            block = mfcc_frames[:, i:i + self.BLOCK_WIDTH]
            block_abs = np.abs(block)
            if np.sum(block_abs) > self.MIN_ENERGY_UNIT * h * w:
                norm_block = block / block_abs.max()
                if not self.has_similar_dtw(norm_block, features):
                    features.append(norm_block)
        return features

    def compare(self, mfcc_block2):
        distance = 10000
        if len(self.features) == 0:
            return distance
        feature2 = self.describe(mfcc_block2)
        if len(feature2) == 0:
            return distance
        for f1 in self.features:
            for f2 in feature2:
                d1 = get_euclidean_distance(f1, f2)
                if d1 < distance:
                    distance = d1
        return distance

    def is_similar(self, mfcc_block2):
        distance = self.compare(mfcc_block2)
        if distance < self.MIN_DISTANCE_UNIT * self.BLOCK_WIDTH * self.BLOCK_HEIGHT:
            return True
        else:
            return False
