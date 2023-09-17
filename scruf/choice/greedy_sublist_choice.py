from icecream import ic
from .choice_mechanism import ChoiceMechanism, ChoiceMechanismFactory
from scruf.agent import AgentCollection
from scruf.util import ResultList, BallotCollection, MultipleBallotsGreedyError
from collections import defaultdict
from copy import copy
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
# there no benefit otherwise we give a bonus to the items. We will use delta for this. Could
# extend to multiple ballots
class xQuadChoiceMechanism(GreedySublistChoiceMechanism):

    def sublist_scorer(self, list_so_far: ResultList, candidates: ResultList, ballots: BallotCollection):
        if ballots.get_count() > 2:
            raise MultipleBallotsGreedyError()
        else:
            # Get the protected ballot
            key = [key for key in ballots.get_names() if key != BallotCollection.REC_NAME][0]
            prot_ballot = ballots.subset([key])
            # Get the recommender weight
            rec_weight = ballots.get_ballot(BallotCollection.REC_NAME).weight
            # If no items in the ballot are on the list so far
            protected_items = prot_ballot.get_ballot(key).prefs.filter_results(lambda entry: entry.score > 0)
            if len(protected_items.intersection(list_so_far)) == 0:
                # Kind of abusing the REC_NAME but that's what merge() uses
                ballots.set_ballot(BallotCollection.REC_NAME, candidates, rec_weight)
                merged = ballots.merge(candidates.get_user())
                return merged
            else:
                return candidates


# Register the mechanisms created above
mechanism_specs = [("xquad", xQuadChoiceMechanism)]

ChoiceMechanismFactory.register_choice_mechanisms(mechanism_specs)



