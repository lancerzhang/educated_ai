import cv2
import imagehash
import librosa
import numpy as np
from PIL import Image
from scipy.spatial.distance import euclidean
from skimage.metrics import structural_similarity as ssim

from components import util
from components.features import VoiceFeature
from components.hsv_color_shapes import ColorShape

CV_THRESHOLD = 64


class ImgHistRecognizer:
    # Use 6 instead of 8 to make it faster
    bins = [6, 6, 6]
    similar_threshold = 1
    img_size = 100

    def __init__(self, img=None, feature=None):
        if feature is not None:
            self.feature = feature
        else:
            self.feature = self.describe(img)

    def describe(self, img):
        img = cv2.resize(img, (self.img_size, self.img_size))
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


class ImageRecognizer:
    hash_threshold = 21
    ssim_threshold = 0.4
    top_colors_hsv = {}
    matched = []
    img_size = 100
    ssim_img_size = 14

    def __init__(self, img=None, feature=None, mode='ssim'):
        self.mode = mode  # ssim or hash, ssim is better for small img (less than32x32)
        if feature is not None:
            self.features = [feature]
        else:
            self.features = self.describe(img)

    def describe(self, img):
        if len(img.shape) == 2:
            feature = self.describe_grey(img)
            if feature is not None:
                return [feature]
            else:
                return []
        else:
            return self.describe_color(img)

    def describe_grey(self, img):
        ret, img = cv2.threshold(img, CV_THRESHOLD, 255, cv2.THRESH_BINARY)
        if util.img_has_content(img):
            img = util.np_2d_array_nonzero_box(img)
            # self.matched.append(img)
            if self.mode == 'ssim':
                img = cv2.resize(img, (self.ssim_img_size, self.ssim_img_size))
                return img
            elif self.mode == 'hash':
                img = Image.fromarray(img)
                # img will be resize to 32x32 in phash
                feature = imagehash.phash(img)
                return feature

    def describe_color(self, img):
        img = cv2.resize(img, (self.img_size, self.img_size))
        features = []
        cs = ColorShape(img)
        self.top_colors_hsv = cs.top_colors_hsv
        for k in cs.top_colors_hsv:
            img = cs.get_grey_shape(k)
            feature = self.describe_grey(img)
            if feature is not None:
                features.append(feature)
        return features

    def compare_feature(self, img2):
        distance = 1000  # max distance
        features2 = self.describe(img2)
        for f1 in self.features:
            for f2 in features2:
                if self.mode == 'ssim':
                    d = 1 - ssim(f1, f2)
                else:
                    d = f1 - f2
                if d < distance:
                    distance = d
        return distance

    def is_similar(self, img2):
        distance = self.compare_feature(img2)
        similar_threshold = self.hash_threshold
        if self.mode == 'ssim':
            similar_threshold = self.ssim_threshold
        if distance < similar_threshold:
            return True
        else:
            return False


def get_euclidean_distance(block1, block2):
    distance = euclidean(block1[0], block2[0]) + euclidean(block1[1], block2[1])
    return distance


class VoiceRecognizer:
    BLOCK_WIDTH = 2
    BLOCK_HEIGHT = 2
    MIN_ENERGY_UNIT = 25
    MIN_DISTANCE_UNIT = 0.1

    def __init__(self, y, sr):
        self.features = self.recognize(y, sr)

    def has_similar_dtw(self, block1, blocks):
        for block2 in blocks:
            distance = get_euclidean_distance(block1, block2)
            if distance < self.MIN_DISTANCE_UNIT * self.BLOCK_WIDTH * self.BLOCK_HEIGHT:
                return True
        return False

    def recognize(self, y, sr):
        mfcc_frames = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13).T
        features = []
        h, w = mfcc_frames.shape
        for j in range(h - self.BLOCK_WIDTH + 1):
            feature = []
            # find shape start from 2nd mfcc value
            for i in range(1, w - self.BLOCK_WIDTH + 1):
                block = mfcc_frames[j:j + self.BLOCK_HEIGHT, i:i + self.BLOCK_WIDTH]
                if np.sum(np.abs(block)) > self.MIN_ENERGY_UNIT * self.BLOCK_WIDTH * self.BLOCK_HEIGHT:
                    norm_block = block / np.max(np.abs(block))
                    max_energy = np.max(block)
                    feature.append(VoiceFeature(i, max_energy, norm_block))
            if len(feature) > 0:
                # first mfcc value is total energy
                total_energy = mfcc_frames[j:j + self.BLOCK_HEIGHT, 0:1]
                max_energy = np.max(total_energy)
                feature.insert(0, VoiceFeature(0, max_energy))
                features.append(feature)
        return features

    def compare_feature(self, mfcc_block2):
        distance = 10000
        if len(self.features) == 0:
            return distance
        feature2 = self.recognize(mfcc_block2)
        if len(feature2) == 0:
            return distance
        for f1 in self.features:
            for f2 in feature2:
                d1 = get_euclidean_distance(f1, f2)
                if d1 < distance:
                    distance = d1
        return distance

    def is_similar(self, mfcc_block2):
        distance = self.compare_feature(mfcc_block2)
        if distance < self.MIN_DISTANCE_UNIT * self.BLOCK_WIDTH * self.BLOCK_HEIGHT:
            return True
        else:
            return False
