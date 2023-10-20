from .result_list import ResultList
from collections import defaultdict
from icecream import ic

class BallotCollection:
    REC_NAME = '__rec'

    def __init__(self):
        self.ballots = {}

    def get_count(self):
        return len(self.ballots)

    def get_names(self):
        return list(self.ballots.keys())

    def get_weights(self):
        return {bal.name: bal.weight for bal in self.ballots.values()}

    def get_ballot(self, name):
        return self.ballots[name]

    def get_ballots(self):
        return self.ballots.values()

    def set_ballot(self, name, prefs, weight=1.0):
        bal = Ballot(name, prefs, weight)
        self.ballots[name] = bal

    def subset(self, names, copy=False, inverse=False):
        new_bcoll = BallotCollection()
        if inverse:
            names = set(self.get_names()).difference(names)
        for name in names:
            if copy:
                ballot = self.ballots[name]
                new_bcoll.set_ballot(ballot.name, ballot.prefs, ballot.weight)
            else:
                new_bcoll.ballots[name] = self.ballots[name]
        return new_bcoll

    def merge(self, user, ignore_weight=False):
        output = ResultList()
        score_table = defaultdict(float)
        ballot_name = BallotCollection.REC_NAME
        for ballot in self.get_ballots():
            ballot_name = ballot.name
            for entry in ballot.prefs.get_results():
                if ignore_weight:
                    score_table[entry.item] += entry.score
                else:
                    score_table[entry.item] += entry.score * ballot.weight

        item_set = {entry.item for entry in self.get_ballot(ballot_name).entry_iterator()}
        triples_list = [(user, item, score_table[item]) for item in item_set]
        output.setup(triples_list, presorted=False)
        return output


class Ballot:
    def __init__(self, name, prefs: ResultList, weight=1.0):
        self.name: str = name
        self.weight: float = weight
        self.prefs: ResultList = prefs

    def __repr__(self):
        return f'Ballot {self.name} ({self.weight}): {self.prefs}'

    def intersect_results(self, results: ResultList):
        return self.prefs.intersection(results)

    def rescore(self, scoring_fn):
        self.prefs.rescore(scoring_fn)

    def entry_iterator(self):
        for entry in self.prefs.get_results():
            yield entry

    def is_recommender(self):
        return self.name == BallotCollection.REC_NAME
