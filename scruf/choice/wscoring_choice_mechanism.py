from icecream import ic
from .choice_mechanism import ChoiceMechanism, ChoiceMechanismFactory
from scruf.agent import AgentCollection
from scruf.util import ResultList, BallotCollection, ScrufError
from collections import defaultdict

# This is a simple choice mechanism that combines the weights and scores that come from the allocation mechanism
# with the scores from the recommender system, weighted by the configured weight.
class WScoringChoiceMechanism(ChoiceMechanism):

    _PROPERTY_NAMES = ['recommender_weight']

    def __init__(self):
        super().__init__()

    def setup(self, input_props, names=None):
        super().setup(input_props, names=self.configure_names(WScoringChoiceMechanism._PROPERTY_NAMES, names))


    def __str__(self):
        return f"WScoringChoiceMechanism: rec_weight = {self.get_property('recommender_weight')}"

    # This function computes its ballot output by combining the weighted scores of items. If there is no score
    # for an item for one agent, then a default score is applied. If there is no score table, then all
    # ballots must contain the same set of items. default score not implemented yet.
    def weighted_combine(self, user, bcoll, default_score_table: None):
        if len(bcoll.get_ballots()) == 0:
            return ResultList()

        if default_score_table is not None:
            raise ScrufError('Default scoring not implemented yet.')

        item_set = {entry.item for entry in bcoll.get_ballot('__rec').prefs.get_results()}
        for ballot in bcoll.get_ballots():
            ballot_items = {entry.item for entry in ballot.prefs.get_results()}
            if len(item_set.symmetric_difference(ballot_items)) != 0:
                raise ScrufError('Ballots must contain identical items if no default score table provided.')

        return bcoll.merge(user)

    def compute_choice(self, agents: AgentCollection, bcoll: BallotCollection, recommended_items: ResultList, list_size):
        rec_weight = float(self.get_property('recommender_weight'))
        bcoll.set_ballot('__rec', recommended_items, rec_weight)
        user = recommended_items.get_user()
        output = self.weighted_combine(user, bcoll, default_score_table=None)
        output.trim(list_size)
        return bcoll, output


mechanism_specs = [("weighted_scoring", WScoringChoiceMechanism)]

ChoiceMechanismFactory.register_choice_mechanisms(mechanism_specs)