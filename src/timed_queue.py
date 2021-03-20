import time
from collections import deque


class TimedItem:
    def __init__(self, item):
        self.item = item
        self.time = time.time()


class TimedQueue:

    def __init__(self, total_duration, pop_duration, pop_count):
        if total_duration <= pop_duration:
            raise RuntimeError("total_duration should larger than pop_duration!")
        self.data = deque()
        self.total_duration = total_duration
        self.pop_duration = pop_duration
        self.pop_count = pop_count

    def __len__(self):
        return len(self.data)

    def __getitem__(self, x):
        return self.data[x].item

    def append(self, item):
        self.data.append(TimedItem(item))

    def extend(self, items):
        self.data.extend(items)

    # left pop certain items from the queue
    def pop_left(self):
        # print('pop_left')
        if len(self.data) == 0:
            return
        # only read when time elapse certain duration
        # because data is collected continuously, should collect data for enough time
        read_end_time = self.data[0].time + self.pop_duration
        if read_end_time > time.time():
            return
        result = []
        # print(f'read_end_time:{read_end_time}')
        while self.data:
            # print(self.data[0].time)
            if self.data[0].time < read_end_time and len(result) < self.pop_count:
                result.append(self.data.popleft().item)
            else:
                return result
        return result
