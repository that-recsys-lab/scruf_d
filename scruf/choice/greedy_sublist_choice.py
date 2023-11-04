from icecream import ic
from .choice_mechanism import ChoiceMechanism, ChoiceMechanismFactory
from scruf.agent import AgentCollection
from scruf.util import ResultList, BallotCollection, MultipleBallotsGreedyError
from collections import defaultdict
from copy import copy
from numpy import array
from abc import abstractmethod

# This is a sublist optimization choice mechanism. The subclasses define a list scoring metric
# using the ballots and then the mechanism augments sublists by adding the item that maximizes
# the score.
class GreedySublistChoiceMechanism(ChoiceMechanism):

    _PROPERTY_NAMES = ['recommender_weight']

    def __init__(self):
        super().__init__()

    def setup(self, input_props, names=None):
        super().setup(input_props,
                      names=self.configure_names(GreedySublistChoiceMechanism._PROPERTY_NAMES, names))


    def __str__(self):
        return f"GreedySublistMechanism: rec_weight = {self.get_property('recommender_weight')}"

    def compute_choice(self, agents: AgentCollection, bcoll: BallotCollection, recommendations: ResultList,
                       list_size):
        rec_weight = float(self.get_property('recommender_weight'))
        bcoll.set_ballot('__rec', recommendations, rec_weight)

        output = ResultList()
        candidates = copy(recommendations)
        score = list_size
        while len(output.get_results()) < list_size or candidates.get_length() == 0:
            # If output has nothing, you can't score, just add top current candidate
            if output.get_length() > 0:
                # score recommendation list
                candidates = self.sublist_scorer(output, candidates, bcoll)
            # remove top item and add to output
            top_item = candidates.get_results()[0]
            candidates.remove_top()
            # Note that we can't use the score that comes out of the sublist_score because that is
            # relative to each iteration, so we just use ordinals here.
            top_item.score = score
            score -= 1
            output.add_result_entry(top_item, sort=False)

        return output

    @abstractmethod
    def sublist_scorer(self, list_so_far: ResultList, candidates: ResultList, ballots: BallotCollection):
        pass

# xQuad says that if there is already one item in the list that is in the protected class then
# there no benefit otherwise we give a bonus to the items.
# Original definition of xQUAD
# xQuAD(u,v, R, S) △= arg max_{v ∈R\S} [λ(rec(v,u) + (1 − λ) max_{v′∈S} I_{x_v∩x_v′=∅}]
# where I is the indicator function.
# So, we add the v (not already in the output list) that maximizes the sum. The first term of the
# sum is λ rec(v,u) and the second term is (1 − λ) and identifies an item whose features represented by
# x do not overlap with existing items.
# In our implementation, rec_weight serves as lambda. Multiple ballots correspond to multiple
# protected features. Is this what Nasim did in the OFaiR experiments?

class xQuadChoiceMechanism(GreedySublistChoiceMechanism):

    def sublist_scorer(self, list_so_far: ResultList, candidates: ResultList, ballots: BallotCollection):
        # Drop the recommender from the agents
        drop_rec = ballots.subset([BallotCollection.REC_NAME], copy=True, inverse=True)
        # Merge the ballots. Scores don't matter; only > 0
        # TODO: get_user as an argument is bogus
        merged = drop_rec.merge(candidates.get_user(), ignore_weight=True)
        # Grab the weight
        rec_weight = ballots.get_ballot(BallotCollection.REC_NAME).weight
        # Filter for the the non-zero items
        protected_items = merged.filter_results(lambda entry: entry.score > 0)
        # If there were non-zero items
        if len(protected_items.intersection(list_so_far)) == 0:
            # Score them all with 1 - re
            merged.rescore(lambda entry: 1 - rec_weight)
            # Add the recommender back in
            ballots.set_ballot(BallotCollection.REC_NAME, candidates, rec_weight)
            final_scoring = ballots.merge(candidates.get_user())
            return final_scoring
        else:
            return candidates

# TODO: Add the non-binary version of xQuad. In this version, the indicator function is replaced
# with a measure of unfairness, which maxes out at 1. This information isn't in the ballot.

# In the PFAR paper, we use this definition of MMR
# MMR(u,v, R, S) △= arg max_{v∈R\S} [λ(rec(v,u) − (1 − λ) Sum_{v′∈S} sim(v,v′)]
# We sum the similarities and find the item which has a large similarity in aggregate. Maybe
# this should be the mean?
#
# But the original definition of MMR from Carbonell and Goldstein, 1998 is this:
# MMR(u,v, R, S) △= arg max_{v∈R\S} [λ(rec(v,u) − (1 − λ) max_{v′∈S} sim(v,v′)]
# So, we find the single item where we have the biggest difference and use that as the
# discount.
# TODO: Maybe this should draw from the item data rather than the agents / ballots?

class MMRAbstractChoiceMechanism(GreedySublistChoiceMechanism):

    def create_feature_dict(self, ballots: BallotCollection):
        self.feature_dict = {}
        for ballot in ballots.get_ballots():
            feature_entries = set()
            non_feature_entries = set()
            for entry in ballot.entry_iterator():
                if entry.score > 0:
                    feature_entries.add(entry.item)
                else:
                    non_feature_entries.add(entry.item)
            self.feature_dict[ballot.name] = feature_entries
            self.feature_dict['~'+ballot.name] = non_feature_entries

    def create_item_dict(self):
        # Create a dictionary of feature sets
        self.candidate_features = defaultdict(set)
        for feature, item_set in self.feature_dict.items():
            for item in item_set:
                self.candidate_features[item].add(feature)

    def ballot_jaccard(self, item1, item2):
        features1 = self.candidate_features[item1]
        features2 = self.candidate_features[item2]
        inter = features1.intersection(features2)
        uni = features1.union(features2)
        return float(len(inter)) / len(uni)

    @abstractmethod
    def candidates_vs_list_score(self, candidates, list_so_far):
        pass

    def sublist_scorer(self, list_so_far: ResultList, candidates: ResultList, ballots: BallotCollection):
         # Drop the recommender from the agents
        drop_rec = ballots.subset([BallotCollection.REC_NAME], copy=True, inverse=True)
        # Create a dictionary mapping features/ballots -> {items} with that feature
        # Use ~feature to represent the absence
        self.create_feature_dict(drop_rec)
        # Create a dictionary mapping items -> {features}
        self.create_item_dict()
        # Grab the weight
        rec_weight = ballots.get_ballot(BallotCollection.REC_NAME).weight

        scored = self.candidates_vs_list_score(candidates, list_so_far)
        rescored_ballots = BallotCollection()
        rescored_ballots.set_ballot('mmr', scored, -(1 - rec_weight))

        # Add the recommender back in
        rescored_ballots.set_ballot(BallotCollection.REC_NAME, candidates, rec_weight)
        final_scoring = rescored_ballots.merge(candidates.get_user(), ignore_weight=False)
        return final_scoring

class MMRSumChoiceMechanism(MMRAbstractChoiceMechanism):

    def sum_similarity(self, item, list_so_far: ResultList):
        similarity = 0
        for output_item in list_so_far.result_item_iter():
            similarity += self.ballot_jaccard(item, output_item)
        return similarity

    def candidates_vs_list_score(self, candidates, list_so_far):
        # For each candidate, score it based on sum of similarities with output items so far
        scored = copy(candidates)
        scored.rescore(lambda entry: self.sum_similarity(entry.item, list_so_far))

        return scored


class MMRClassicChoiceMechanism(MMRAbstractChoiceMechanism):

    def max_similarity(self, item, list_so_far: ResultList):
        return max([self.ballot_jaccard(item, output_item)
                    for output_item in list_so_far.result_item_iter()])

    def candidates_vs_list_score(self, candidates, list_so_far):
        scored = copy(candidates)
        scored.rescore(lambda entry: self.max_similarity(entry.item, list_so_far))

        return scored

# TODO: New algorithm idea. We have the allocation scores. We could use this as input to a weighted similarity.

# Register the mechanisms created above
mechanism_specs = [("xquad", xQuadChoiceMechanism),
                   ("mmr_sum", MMRSumChoiceMechanism),
                   ("mmr_max", MMRClassicChoiceMechanism)]

ChoiceMechanismFactory.register_choice_mechanisms(mechanism_specs)

