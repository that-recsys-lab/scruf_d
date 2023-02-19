from icecream import ic
from .choice_mechanism import ChoiceMechanism, ChoiceMechanismFactory
from scruf.agent import AgentCollection
from scruf.util import ResultList

# This is a simple choice mechanism that computes a score for the item for all the agents and then computes the
# new score as a linear combination of the original score and the dot product of the agent scores and the allocation
# probabilities. I don't know if we would ever really use this.
class RescoreChoiceMechanism(ChoiceMechanism):

    _PROPERTY_NAMES = ['recommender_weight']

    def __init__(self):
        super().__init__()

    def __str__(self):
        return f"ReScoreChoiceMechanism: rec_weight = {self.get_property('recommender_weight')}"

    def compute_choice(self, agents: AgentCollection, allocation_probabilities, recommended_items: ResultList, list_size):
        results_dict = {}
        for agent in agents.agents:
            scorer = agent.choice_scorer
            weight = allocation_probabilities[agent.name]
            # If weight is zero could skip these steps.
            agent_results = scorer.score_choices(recommended_items, list_size, inplace=False)
            agent_results.rescore(lambda entry: entry.score * weight)
            results_dict[agent.name] = agent_results

        rec_weight = float(self.get_property('recommender_weight'))
        recommended_items.rescore(lambda entry: entry.score * rec_weight)
        results_dict['original'] = recommended_items

        new_scores = ResultList.combine_results_dict(results_dict)
        new_scores.trim(list_size)
        results_dict['output'] = new_scores
        return results_dict


mechanism_specs = [("weighted_rescore", RescoreChoiceMechanism)]

ChoiceMechanismFactory.register_choice_mechanisms(mechanism_specs)