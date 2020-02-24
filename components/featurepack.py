class FeaturePack(object):

    def __init__(self, mid=None, data=None, type=None, channel=None, kernel=None, feature=None):
        self.mid = mid
        self.data = data
        self.type = type
        self.channel = channel
        self.kernel = kernel
        self.feature = feature
        self.similar = False
