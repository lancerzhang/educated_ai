from components import util
import numpy as np


class Favor:
    def __init__(self):
        self.vuk = Rank()
        self.suk = Rank()
        self.speed = Rank()
        self.degrees = Rank()
        self.channel = Rank()

    @util.timeit
    def top(self, category, index=0):
        rank = getattr(self, category)
        return rank.top(index)

    @util.timeit
    def update(self, category, key):
        rank = getattr(self, category)
        rank.update(key)

    @util.timeit
    def save(self):
        self.vuk.items = self.vuk.items[:50]
        self.suk.items = self.suk.items[:50]
        favors = [self.vuk, self.suk, self.speed, self.degrees, self.channel]
        np.save('favor', list(favors))

    @util.timeit
    def load(self):
        try:
            all = np.load('favor.npy', allow_pickle=True)
            self.vuk = all[0]
            self.suk = all[1]
            self.speed = all[2]
            self.degrees = all[3]
            self.channel = all[4]
        except:
            pass


class Rank:
    def __init__(self):
        self.items = []

    @util.timeit
    def top(self, index=0):
        if index < len(self.items):
            return self.items[index]
        return

    @util.timeit
    def get(self, key):
        for item in self.items:
            if key == item.key:
                return item

    @util.timeit
    def update(self, key):
        item = self.get(key)
        if item:
            item.count += 1
            self.items = sorted(self.items, key=lambda x: x.count, reverse=True)
        else:
            item = Count(key)
            self.items.append(item)


class Count:

    def __init__(self, key):
        self.key = key
        self.count = 1
