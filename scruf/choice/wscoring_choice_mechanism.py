from icecream import ic
from .choice_mechanism import ChoiceMechanism, ChoiceMechanismFactory
from scruf.agent import AgentCollection
from scruf.util import ResultList, BallotCollection

# This is a simple choice mechanism that combines the weights and scores that come from the allocation mechanism
# with the scores from the recommender system, weighted by the configured weight.
class WScoringChoiceMechanism(ChoiceMechanism):

    _PROPERTY_NAMES = ['recommender_weight']

    def __init__(self):
        super().__init__()

    def __str__(self):
        return f"WScoringChoiceMechanism: rec_weight = {self.get_property('recommender_weight')}"

    def compute_choice(self, agents: AgentCollection, bcoll: BallotCollection, recommended_items: ResultList, list_size):
        rec_weight = float(self.get_property('recommender_weight'))
        bcoll.set_ballot('__rec', recommended_items, rec_weight)
        output = self.weighted_combine(bcoll)
        output.trim()
        return bcoll, output

    def compute_choice(self, agents: AgentCollection, allocation_probabilities, recommended_items: ResultList, list_size):
        results_dict = {}

        # For agent in agents:
        #   Collect prefs
        # Weight by weight from dictionary
        # Combine results
        # Trim
        # Return
        # TODO: write a version of combine results that allows weights




        recommended_items.rescore(lambda entry: entry.score * rec_weight)
        results_dict['original'] = recommended_items

        new_scores = ResultList.combine_results_dict(results_dict)
        new_scores.trim(list_size)
        results_dict['output'] = new_scores
        return results_dict


mechanism_specs = [("weighted_scoring", WScoringChoiceMechanism)]

ChoiceMechanismFactory.register_choice_mechanisms(mechanism_specs)