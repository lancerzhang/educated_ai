from components import util


class Storage:
    def __init__(self):
        self.vuk = SortedStack()
        self.suk = SortedStack()
        self.speed = SortedStack()
        self.degrees = SortedStack()
        self.channel = SortedStack()

    @util.timeit
    def get_top(self, category, offset=0):
        sorted_stack = getattr(self, category)
        return sorted_stack.get_top(offset)

    @util.timeit
    def put_item(self, category, key):
        sorted_stack = getattr(self, category)
        sorted_stack.put_item(key)


class SortedStack:
    def __init__(self):
        self.items = []

    @util.timeit
    def get_top(self, offset=0):
        return self.items[offset]

    @util.timeit
    def get_item(self, key):
        for item in self.items:
            if key == item.key:
                return item

    @util.timeit
    def put_item(self, key):
        item = self.get_item(key)
        if item:
            item.count += 1
            self.items = sorted(self.items, key=lambda x: x.count, reverse=True)
        else:
            item = Item(key)
            self.items.append(item)


class Item:

    def __init__(self, key):
        self.key = key
        self.count = 1
