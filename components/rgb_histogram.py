import cv2
import imutils

SIZE = 100


class RGBHistogram:
    def __init__(self, bins):
        # store the number of bins the histogram will use
        self.bins = bins

    def describe(self, image):
        h, w = image.shape
        if h < SIZE or w < SIZE:
            image = cv2.resize(image, (SIZE, SIZE))
        # compute a 3D histogram in the RGB colorspace,
        # then normalize the histogram so that images
        # with the same content, but either scaled larger
        # or smaller will have (roughly) the same histogram
        hist = cv2.calcHist([image], [0, 1, 2], None, self.bins, [0, 256, 0, 256, 0, 256])
        # normalize with OpenCV 2.4
        if imutils.is_cv2():
            hist = cv2.normalize(hist)
        # otherwise normalize with OpenCV 3+
        else:
            hist = cv2.normalize(hist, hist)
        # return out 3D histogram as a flattened array
        return hist.flatten()
