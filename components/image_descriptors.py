import cv2
import numpy as np


class RgbHistogram:
    similar_threshold = 1

    def __init__(self):
        # Use 6 instead of 8 to make it faster
        self.bins = [6, 6, 6]

    def chi2_distance(histA, histB, eps=1e-10):
        # compute the chi-squared distance
        d = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps)
                          for (a, b) in zip(histA, histB)])
        # return the chi-squared distance
        return d

    def describe(self, image):
        # compute a 3D histogram in the RGB colorspace,
        # then normalize the histogram so that images
        # with the same content, but either scaled larger
        # or smaller will have (roughly) the same histogram
        hist = cv2.calcHist([image], [0, 1, 2],
                            None, self.bins, [0, 256, 0, 256, 0, 256])
        # normalize
        hist = cv2.normalize(hist, hist)
        # return out 3D histogram as a flattened array
        return hist.flatten()

    def compare(self, img1, img2):
        feature1 = self.describe(img1)
        feature2 = self.describe(img2)
        return self.chi2_distance(feature1, feature2)

    def is_similar(self, img1, img2):
        distance = self.compare(img1, img2)
        if distance < self.similar_threshold:
            return True
        else:
            return False


class MajorColor:
    similar_threshold = 1

    def __init__(self):
        pass

    def describe(self, image):
        return 0

    def compare(self, img1, img2):
        feature1 = self.describe(img1)
        feature2 = self.describe(img2)
        return 0

    def is_similar(self, img1, img2):
        distance = self.compare(img1, img2)
        if distance < self.similar_threshold:
            return True
        else:
            return False


class MajorColorShape:
    similar_threshold = 1

    def __init__(self):
        pass

    def describe(self, image):
        return 0

    def compare(self, img1, img2):
        feature1 = self.describe(img1)
        feature2 = self.describe(img2)
        return 0

    def is_similar(self, img1, img2):
        distance = self.compare(img1, img2)
        if distance < self.similar_threshold:
            return True
        else:
            return False


class ThresholdShape:
    similar_threshold = 1

    def __init__(self):
        pass

    def describe(self, image):
        return 0

    def compare(self, img1, img2):
        feature1 = self.describe(img1)
        feature2 = self.describe(img2)
        return 0

    def is_similar(self, img1, img2):
        distance = self.compare(img1, img2)
        if distance < self.similar_threshold:
            return True
        else:
            return False


class Vgg16FilterShape:
    similar_threshold = 1

    def __init__(self):
        pass

    def describe(self, image):
        return 0

    def compare(self, img1, img2):
        feature1 = self.describe(img1)
        feature2 = self.describe(img2)
        return 0

    def is_similar(self, img1, img2):
        distance = self.compare(img1, img2)
        if distance < self.similar_threshold:
            return True
        else:
            return False
