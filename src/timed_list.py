import time


class TimedItem:
    def __init__(self, content):
        self.content = content
        self.created_time = time.time()


class TimedList:

    def __init__(self, working_duration):
        self.data = []
        self.working_duration = working_duration
        self.total_duration = working_duration * 2
        self.processing = []
        self.processed = []
        self.expired = []

    def __len__(self):
        return len(self.data)

    def __getitem__(self, x):
        return self.data[x].content

    def append(self, item):
        self.data.append(TimedItem(item))

    def extend(self, items):
        self.data.extend(items)

    def slice(self):
        processing = []
        processed = []
        expired = []
        now_time = time.time()
        for item in self.data:
            elapsed = now_time - item.created_time
            if elapsed > self.total_duration:
                expired.append(item)
            elif elapsed > self.working_duration:
                processed.append(item)
            else:
                processing.append(item)

    def rebuild(self, new_processing):
        self.data = self.processed + new_processing
