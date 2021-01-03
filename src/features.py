from src import constants


class Feature(object):
    type = 'feature'


class SpeechFeature(Feature):

    def __init__(self, frequency, energy, shape=None):
        self.type = constants.speech
        self.frequency = frequency
        self.energy = energy
        self.shape = shape


class VisionFeature(Feature):

    def __init__(self, hist=None, color=None, shape=None):
        self.type = constants.vision
        self.hist = hist
        self.color = color
        self.shape = shape
