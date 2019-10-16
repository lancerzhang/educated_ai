from components import util


class Storage:
    def __init__(self):
        self.vuk = SortedList()
        self.suk = SortedList()
        self.speed = SortedList()
        self.degrees = SortedList()
        self.channel = SortedList()

    @util.timeit
    def top(self, category, index=0):
        sorted_list = getattr(self, category)
        return sorted_list.top(index)

    @util.timeit
    def update(self, category, key):
        sorted_list = getattr(self, category)
        sorted_list.update(key)


class SortedList:
    def __init__(self):
        self.items = []

    @util.timeit
    def top(self, index=0):
        return self.items[index]

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
