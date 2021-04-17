import time
from collections import deque


class TimedItem:
    def __init__(self, content):
        self.content = content
        self.created_time = time.time()


class TimedQueue:

    def __init__(self, total_duration, pop_duration, pop_count=9999, break_time=9999, consecutive_duplicates=True):
        if total_duration <= pop_duration:
            raise RuntimeError("Total_duration should larger than pop_duration!")
        self.data = deque()
        self.total_duration = total_duration
        self.pop_duration = pop_duration
        self.pop_count = pop_count
        self.break_time = break_time
        self.consecutive_duplicates = consecutive_duplicates  # Allow consecutive duplicates?

    def __len__(self):
        return len(self.data)

    def __getitem__(self, x):
        return self.data[x].content

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
        read_end_time = self.data[0].created_time + self.pop_duration
        # print(f'pop_left: read_end_time:{read_end_time}')
        # print(f'pop_left: now {time.time()}')
        if read_end_time > time.time():
            # print('pop_left: not enough duration to read')
            return
        result = []
        last_time = self.data[0].created_time
        while self.data:
            # print(self.data[0].created_time)
            if self.data[0].created_time < read_end_time \
                    and self.data[0].created_time - last_time < self.break_time \
                    and len(result) < self.pop_count:
                last_time = self.data[0].created_time
                new_item = self.data.popleft()
                # if len(result) > 0:
                #     print(f'result[-1] {result[-1]}')
                # print(f'new_item.content {new_item.content}')
                # print(f'break')
                if self.consecutive_duplicates or len(result) == 0 or result[-1] != new_item.content:
                    result.append(new_item.content)
            else:
                return result
        return result

    def delete_expired(self):
        new_queue = deque()
        end_time = time.time() - self.total_duration
        for item in self.data:
            if item.created_time > end_time:
                new_queue.append(item)
        self.data = new_queue
