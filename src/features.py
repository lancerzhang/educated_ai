from src import constants


class Feature(object):
    type = 'feature'


class VoiceFeature(Feature):

    def __init__(self, frequency, energy, shape=None):
        self.type = constants.speech
        self.frequency = frequency
        self.energy = energy
        self.shape = shape


class ImageFeature(Feature):

    def __init__(self, hist=None, color=None, shape=None):
        self.type = constants.image
        self.hist = hist
        self.color = color
        self.shape = shape
