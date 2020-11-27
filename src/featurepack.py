class FeaturePack(object):

    def __init__(self, mid=None, data=None, channel=None, kernel=None, feature=None, contrast=None):
        self.mid = mid
        self.data = data
        self.channel = channel
        self.kernel = kernel
        self.feature = feature
        self.contrast = contrast
        self.similar = False
