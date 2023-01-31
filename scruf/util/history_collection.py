import itertools
from collections import deque, namedtuple
from scruf.util.errors import HistoryEmptyError

TimedEntry = namedtuple('TimedEntry', ['time', 'item'])

class HistoryCollection:

    def __init__(self, window_size=None):
        self.window_size = window_size
        self.collection = deque(maxlen=window_size)
        self.time = 0

    def __repr__(self):
        return f"<HistoryCollection: window: {self.collection._maxlen} current time: {self.time}>"

    def add_item(self, item):
        self.collection.appendleft(TimedEntry(self.time, item))
        self.time += 1

    def add_items(self, items):
        for item in items:
            self.add_item(item)

    def get_most_recent(self):
        if len(self.collection) > 0:
            return self.collection[0].item
        else:
            raise HistoryEmptyError()

    # -1 means return everything
    def get_recent(self, k):
        if len(self.collection) == 0:
            raise HistoryEmptyError()

        if k == -1:
            entries = self.collection
        else:
            entries = itertools.islice(self.collection, 0, k)
        # entries = self.collection[range(0, k)]
        return [entry.item for entry in entries]

    def get_from_time(self, t):
        if len(self.collection) == 0:
            raise HistoryEmptyError()

        current_time = self.collection[0].time
        if t > current_time:
            return None
        else:
            entry = self.collection[current_time - t]
            return entry.item

    def is_empty(self):
        return len(self.collection) == 0


