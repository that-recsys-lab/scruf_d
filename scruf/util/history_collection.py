import itertools
from collections import deque, namedtuple, Counter

TimedEntry = namedtuple('TimedEntry', ['time', 'item'])

class HistoryCollection:

    def __init__(self, window_size=None):
        self.collection = deque(maxlen=window_size)
        self.time = 0

    def __str__(self):
        return f"<HistoryCollection: window: {self.collection._maxlen} current time: {self.time}>"

    def add_item(self, item):
        self.collection.appendleft(TimedEntry(self.time, item))
        self.time += 1

    def add_items(self, items):
        for item in items:
            self.add_item(item)

    # -1 means return everything
    def get_recent(self, k):
        if k == -1:
            entries = self.collection
        else:
            entries = itertools.islice(self.collection, 0, k)
        # entries = self.collection[range(0, k)]
        return [entry.item for entry in entries]

    def get_from_time(self, t):
        current_time = self.collection[0].time
        if t > current_time:
            return None
        else:
            entry = self.collection[current_time - t]
            return entry.item




