from .result_list import ResultList
from collections import defaultdict

class BallotCollection:
    REC_NAME = '__rec'

    def __init__(self):
        self.ballots = {}

    def get_count(self):
        return len(self.ballots)

    def get_weights(self):
        return {bal.name: bal.weight for bal in self.ballots.values()}

    def get_ballot(self, name):
        return self.ballots[name]

    def get_ballots(self):
        return self.ballots.values()

    def set_ballot(self, name, prefs, weight=1.0):
        bal = Ballot(name, prefs, weight)
        self.ballots[name] = bal

    def subset(self, names, copy=False):
        new_bcoll = BallotCollection()
        for name in names:
            if copy:
                ballot = self.ballots[name]
                new_bcoll.set_ballot(ballot.name, ballot.prefs, ballot.weight)
            else:
                new_bcoll.ballots[name] = self.ballots[name]
        return new_bcoll

    def merge(self, user):
        output = ResultList()
        score_table = defaultdict(float)
        for ballot in self.get_ballots():
            for entry in ballot.prefs.get_results():
                score_table[entry.item] += entry.score * ballot.weight

        item_set = {entry.item for entry in self.get_ballot(BallotCollection.REC_NAME).prefs.get_results()}
        triples_list = [(user, item, score_table[item]) for item in item_set]
        output.setup(triples_list, presorted=False)
        return output

class Ballot:
    def __init__(self, name, prefs: ResultList, weight=1.0):
        self.name = name
        self.weight = weight
        self.prefs = prefs

    def intersect_results(self, results: ResultList):
        return self.prefs.intersection(results)
