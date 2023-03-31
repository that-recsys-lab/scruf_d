from .result_list import ResultList


class BallotCollection:
    def __init__(self):
        self.ballots = {}

    def get_weights(self):
        return {bal.name: bal.weight for bal in self.ballots.values()}

    def get_ballot(self, name):
        return self.ballots[name]

    def set_ballot(self, name, prefs, weight=1.0):
        bal = Ballot(name, prefs, weight)
        self.ballots[name] = bal


class Ballot:
    def __init__(self, name, prefs: ResultList, weight=1.0):
        self.name = name
        self.weight = weight
        self.prefs = prefs
