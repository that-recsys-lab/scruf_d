from collections import defaultdict


class ResultEntry:

    def __init__(self, user=None, item=None, score=float('nan'),
                 rank=-1):
        self.user = user
        self.item = item
        self.score = score
        self.rank = rank

    def __repr__(self):
        return f'ResultEntry: U:{self.user}, I:{self.item}, S:{self.score}, R{self.rank}'

# TODO: Probably should have some kind of 'dirty' flag, so that when the list is changed but not
# sorted, some functions can either fail or force sort.
class ResultList:

    def __repr__(self):
        return f'Result: {self.results}'

    def __init__(self):
        self.results = []

    def __copy__(self):
        result_list = ResultList()
        result_list.results = self.results.copy()
        return result_list

    def __deepcopy__(self, memodict={}):
        result_list = ResultList()
        for entry in self.results:
            result = ResultEntry(user=entry.user, item=entry.item, score=entry.rating, rank=entry.rank)
            result_list.results.append(result)
        return result_list

    def setup(self, triples, presorted=False, trim=0):
        self.results = []
        # Test for length of triples. If > 3, signal file format error
        for user, item, rating in triples:
            result = ResultEntry(user=user, item=item, score=float(rating), rank=-1)
            self.results.append(result)

        if not presorted:
            self.sort()

        if trim > 0:
            self.trim(trim)

    # Assumes all results are for the same user
    def get_user(self):
        if len(self.results) > 0:
            return self.results[0].user
        else:
            return None

    def get_results(self):
        return self.results

    def result_item_iter(self):
        for entry in self.results:
            yield entry.item

    def get_length(self):
        return len(self.results)

    def remove_result(self, item):
        self.results = keyed_delete(self.results, item, key=lambda entry: entry.item)

    # Assumes sorted
    def remove_top(self):
        self.results = self.results[1:]

    # Assumes the list is sorted
    def score_range(self):
        first_entry = self.results[0]
        last_entry = self.results[-1]
        return (first_entry.score, last_entry.score)

    def add_result(self, user, item, score, sort=False):
        new_entry = ResultEntry(user=user, item=item, score=score, rank=-1)
        self.results.append(new_entry)
        if sort:
            self.sort()

    def add_result_entry(self, entry: ResultEntry, sort=False):
        self.results.append(entry)
        if sort:
            self.sort()

    # In addition to sorting, also sets the rank value
    def sort(self):
        sorted_results = sorted(self.results, key=lambda result: result.score, reverse=True)
        for i in range(0, len(sorted_results)):
            sorted_results[i].rank= i

        self.results = sorted_results

    # Assumes the list is sorted.
    def trim(self, new_length):
        if len(self.results) > new_length:
            self.results = self.results[0:new_length]

    def rescore(self, score_fn):
        self.rescore_no_sort(score_fn)
        self.sort()

    def rescore_no_sort(self, score_fn):
        for result in self.results:
            new_score = score_fn(result)
            result.score = new_score

    def filter_results(self, filter_fn):
        output = ResultList()
        output.results = list(filter(filter_fn, self.results))
        return output

    @staticmethod
    # Assumes all the same user. Maybe should check for this
    # Does not require the result lists be in the same order
    def combine_results(result_lists):
        if len(result_lists) == 0:
            return []
        user_id = result_lists[0].results[0].user
        score_table = defaultdict(list)
        for result_list in result_lists:
            for entry in result_list.results:
                score_table[entry.item].append(entry.score)

        output = ResultList()
        for item, value_list in score_table.items():
            output.add_result(user_id, item, sum(value_list), sort=False)

        output.sort()

        return output

    # As above but input is an agent -> ResultList dictionary
    @staticmethod
    def combine_results_dict(result_dict):
        if len(result_dict) == 0:
            return []
        score_table = defaultdict(list)
        for result_list in result_dict.values():
            for entry in result_list.results:
                user_id = entry.user
                score_table[entry.item].append(entry.score)

        output = ResultList()
        for item, value_list in score_table.items():
            output.add_result(user_id, item, sum(value_list), sort=False)

        output.sort()

        return output

    def intersection(self, other_results):
        this_items = {entry.item for entry in self.results}
        other_items = {entry.item for entry in other_results.results}
        return this_items.intersection(other_items)


# Non-destructive
def keyed_delete(lst, item, key=None):
    if key is None:
        new_lst = lst.copy()
        new_lst.remove(item)
        return new_lst
    else:
        return [entry for entry in lst if not key(entry)==item]
