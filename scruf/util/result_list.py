from collections import namedtuple

ResultEntry = namedtuple('ResultEntry', ['user', 'item', 'score', 'rank',
                                         'old_scores', 'old_ranks'],
                         defaults=[None, None, float('nan'), -1, [], []])

class ResultList:

    def __init__(self):
        self.results = None

    def setup(self, triples, presorted=False, trim=0):
        self.results = []
        for user, item, rating in triples:
            result = ResultEntry(user=user, item=item, score=float(rating))
            self.results.append(result)

        if not presorted:
            self.sort()

        if trim > 0:
            self.trim(trim)

    def get_results(self):
        return self.results

    # In addition to sorting, also sets the rank value
    def sort(self):
        sorted_results = sorted(self.results, key=lambda result: result.score, reverse=True)
        for i in range(0, len(sorted_results)):
            sorted_results[i]._replace(rank=i)

        self.results = sorted_results

    # Assumes the list is sorted.
    def trim(self, new_length):
        self.results = self.results[0:new_length]

    def rescore(self, score_fn):
        for result in self.results:
            new_score = score_fn(result)
            result.old_scores.append(result['score'])
            result.old_ranks.append(result['rank'])

            result.score = new_score

        self.sort()

    def filter_results(self, filter_fn):
        return filter(filter_fn, self.results)

