from collections import Counter
from scruf.util import HistoryCollection


class ResultsHistory(HistoryCollection):

    def get_recent_results(self, k):
        rlists = self.get_recent(k)

        full_list = []
        for rlist in rlists:
            full_list += rlist.get_results()

        return full_list

    def get_item_counts(self, k):
        results = self.get_recent_results(k)
        items = [result.item for result in results]
        return Counter(items)
