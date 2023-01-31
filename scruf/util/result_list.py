from collections import defaultdict


class ResultEntry:

    def __init__(self, user=None, item=None, score=float('nan'),
                 rank=-1):
        self.user = user
        self.item = item
        self.score = score
        self.rank = rank
        self.old_scores = []
        self.old_ranks = []

    def __repr__(self):
        return f'ResultEntry: U:{self.user}, I:{self.item}, S:{self.score}, R{self.rank}, OS:{self.old_scores}, OR:{self.old_ranks}'

    def update_score(self, new_score):
        self.old_scores.append(self.score)
        self.score = new_score

    def update_rank(self, new_rank):
        if not self.rank == -1:
            self.old_ranks.append(self.rank)
        self.rank = new_rank


class ResultList:

    def __init__(self):
        self.results = []

    def setup(self, triples, presorted=False, trim=0):
        self.results = []
        for user, item, rating in triples:
            result = ResultEntry(user=user, item=item, score=float(rating), rank=-1)
            self.results.append(result)

        if not presorted:
            self.sort()

        if trim > 0:
            self.trim(trim)

    def get_results(self):
        return self.results

    def add_result(self, user, item, score, sort=False):
        new_entry = ResultEntry(user=user, item=item, score=score, rank=-1)
        self.results.append(new_entry)
        if sort:
            self.sort()

    # In addition to sorting, also sets the rank value
    def sort(self):
        sorted_results = sorted(self.results, key=lambda result: result.score, reverse=True)
        for i in range(0, len(sorted_results)):
            sorted_results[i].update_rank(i)

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
            result.update_score(new_score)

    def filter_results(self, filter_fn):
        return filter(filter_fn, self.results)

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




