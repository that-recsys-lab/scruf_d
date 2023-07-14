from .allocation_mechanism import AllocationMechanism, AllocationMechanismFactory
from scruf.agent import AgentCollection
from scruf.util import normalize_score_dict
from abc import abstractmethod
from icecream import ic
import scruf

# Similar to a scored allocation but the weights are treated like lottery and
# only a single agent is chosen
class LotteryAllocationMechanism(AllocationMechanism):

    def score_dict_lottery(self, score_dict: dict, agents):
        lottery = normalize_score_dict(score_dict)
        winner = scruf.Scruf.state.rand.choices(lottery.keys(), lottery.values())
        result = scruf.Scruf.state.agents.agent_value_pairs(default=0.0)
        result[winner] = 1.0
        return result

    def __init__(self):
        super().__init__()

    @abstractmethod
    def score(self, agent_name, fairness_values, compatibility_values):
        pass

    def compute_allocation_probabilities(self, agents: AgentCollection, history, context):
        """
        Computes the allocation probabilities for a collection of FairnessAgents based on the product of
        their fairness and compatibility scores, and conducts a lottery using the values.
        :param agents: a list of FairnessAgent objects
        :param history: a system History object
        :param context: a Context objedct
        :return: a dictionary mapping agent names to allocation probabilities
        """
        # Compute the fairness and compatibility scores for each agent
        fairness_values = agents.compute_fairnesses(history)
        compat_values = agents.compute_compatibilities(context)
        scores = {agent_name: self.score(agent_name, fairness_values, compat_values) \
                    for agent_name in agents.agent_names()}

        # Normalize the scores to sum to 1
        scores = self.score_dict_lottery(scores, agents)
        return {'fairness scores': fairness_values,
                'compatibility scores': compat_values,
                'output': scores}

class ProductAllocationLottery(LotteryAllocationMechanism):

    def __init__(self):
        super().__init__()

    def score(self, agent_name, fairness_values, compatibility_values):
        return (1.0 - fairness_values[agent_name]) * compatibility_values[agent_name]


class WeightedProductAllocationLottery(LotteryAllocationMechanism):

    _PROPERTY_NAMES = ['fairness_exponent', 'compatibility_exponent']

    def __init__(self):
        super().__init__()

    def setup(self, input_props, names=None):
        super().setup(input_props,
                      names=self.configure_names(WeightedProductAllocationLottery._PROPERTY_NAMES, names))


    def __str__(self):
        return f"WeightedProductAllocation: fairness = {self.get_propery('fairness_exponent')}, compatibility = {self.get_propery('compatibility_exponent')}"

    def score(self, agent_name, fairness_values, compatibility_values):
        fairness_exp = self.get_property('fairness_exponent')
        compat_exp = self.get_property('compatibility_exponent')
        fairness_term = (1.0 - fairness_values[agent_name]) ** fairness_exp
        compat_term =  compatibility_values[agent_name] ** compat_exp
        return fairness_term * compat_term

class FairnessAllocationLottery(LotteryAllocationMechanism):

    def __init__(self):
        super().__init__()

    def score(self, agent_name, fairness_values, compatibility_values):
        return 1.0 - fairness_values[agent_name]

class StaticAllocationLottery(LotteryAllocationMechanism):

    # Weights are specified in the config file as a list of pairs:
    # [ ["Agent 1", 0.5], ["Agent 2", 0.2] ]
    # If the total is less than 1, then a dummy agent is added. If the
    # dummy is selected by the lottery, then no agents are allocated.
    _PROPERTY_NAMES = ['weights']
    _DUMMY_AGENT = "__dummy__"

    def __init__(self):
        super().__init__()
        self.lottery = None

    def setup(self, input_properties: dict, names=None):
        super().setup(input_properties,
                      names=self.configure_names(StaticAllocationLottery._PROPERTY_NAMES, names))
        weights = self.get_property('weights')
        weights_sum = sum([float(wt) for agent, wt in weights])
        if weights_sum < 1.0:
            weights.append([self._DUMMY_AGENT, 1 - weights_sum])
        self.lottery = normalize_score_dict({agent: float(wt) for agent, wt in weights})

    def score_dict_lottery(self, _, agents):
        # ic(list(self.lottery.keys()), list(self.lottery.values()))
        winner = scruf.Scruf.state.rand.choices(list(self.lottery.keys()), list(self.lottery.values()))[0]
        #ic(winner)
        result = scruf.Scruf.state.agents.agent_value_pairs(default=0.0)
        if winner != self._DUMMY_AGENT:
            result[winner] = 1.0
        return result

    def score(self, agent_name, fairness_values, compatibility_values):
        return float("nan")

mechanism_specs = [("product_lottery", ProductAllocationLottery),
                   ("weighted_product_lottery", WeightedProductAllocationLottery),
                   ("fairness_lottery", FairnessAllocationLottery),
                   ("static_lottery", StaticAllocationLottery)]

AllocationMechanismFactory.register_allocation_mechanisms(mechanism_specs)
