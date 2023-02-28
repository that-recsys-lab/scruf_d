from abc import ABC, abstractmethod
from scruf.util import PropertyMixin, InvalidAllocationMechanismError, UnregisteredAllocationMechanismError, \
    normalize_score_dict, collapse_score_dict, ContextNotFoundError
from scruf.agent import AgentCollection
import scruf
import random

class AllocationMechanism(PropertyMixin,ABC):
    """
    An AllocationMechanism computes allocation probabilities for a
    collection of FairnessAgents based on their fairness and compatibility scores. All mechanisms are
    initialized with a dictionary of property name, value pairs. Each subclass has to specify the
    property names that it expects.
    """

    def do_allocation(self, user_info):
        user_id = user_info.get_user()
        agents = scruf.Scruf.state.agents
        history = scruf.Scruf.state.history
        context = scruf.Scruf.state.context.get_context(user_id)
        if len(context) == 0:
            raise ContextNotFoundError(user_id)
        allocation_result = self.compute_allocation_probabilities(agents, history, context)
        history.allocation_history.add_item(allocation_result)
        return allocation_result['output']

    @abstractmethod
    def compute_allocation_probabilities(self, agents, history, context):
        pass


class RandomAllocationMechanism(AllocationMechanism):

    def __init__(self):
        super().__init__()

    def compute_allocation_propabilities(self, agents, history, context):
        # ignored
        del history, context
        allocation_probabilities = agents.agent_value_pairs()
        selected = random.choice(agents.agent_names())
        allocation_probabilities[selected] = 1
        nan_scores = agents.agent_value_pairs(default=float('NaN'))
        return {'fairness scores': nan_scores,
                'compatibility scores': nan_scores,
                'output': allocation_probabilities}

class ScoredAllocationMechanism(AllocationMechanism):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def score(self, agent_name, fairness_values, compatibility_values):
        pass

    def compute_allocation_probabilities(self, agents: AgentCollection, history, context):
        """
        Computes the allocation probabilities for a collection of FairnessAgents based on the product of
        their fairness and compatibility scores, and normalizes the values to ensure that they sum to 1.
        :param agents: a list of FairnessAgent objects
        :param history: a system History object
        :param context: a Context objedct
        :return: a dictionary mapping agent names to allocation probabilities
        """
        # Compute the fairness and compatibility scores for each agent
        fairness_values = agents.compute_fairness(history)
        compat_values = agents.compute_compatibility(context)
        scores = {agent_name: self.score(agent_name, fairness_values, compat_values) \
                    for agent_name in agents.agent_names()}

        # Normalize the scores to sum to 1
        scores = normalize_score_dict(scores, inplace=True)
        return {'fairness scores': fairness_values,
                'compatibility scores': compat_values,
                'output': scores}


class ProductAllocationMechanism(ScoredAllocationMechanism):

    def __init__(self):
        super().__init__()

    def score(self, agent_name, fairness_values, compatibility_values):
        return (1.0 - fairness_values[agent_name]) * compatibility_values[agent_name]


class WeightedProductAllocationMechanism(ScoredAllocationMechanism):

    _PROPERTY_NAMES = ['fairness_exponent', 'compatibility_exponent']

    def __init__(self):
        super().__init__()

    def __str__(self):
        return f"WeightedProductAllocation: fairness = {self.get_propery('fairness_exponent')}, compatibility = {self.get_propery('compatibility_exponent')}"

    def score(self, agent_name, fairness_values, compatibility_values):
        fairness_exp = self.get_property('fairness_exponent')
        compat_exp = self.get_property('compatibility_exponent')
        fairness_term = (1.0 - fairness_values[agent_name]) ^ fairness_exp
        compat_term =  compatibility_values[agent_name] ^ compat_exp
        return fairness_term * compat_term

class LeastFairAllocationMechanism(AllocationMechanism):
    """
    The LeastFair allocation mechanism allocates to the agent with the lowest fairness score.
    """

    def __init__(self):
        super().__init__()

    def compute_allocation_probabilities(self, agents, history, context):
        # Compute the fairness scores for each agent
        scores = agents.compute_fairness(history)
        # Find lowest fairness
        lowest_agent = collapse_score_dict(scores, type='min', handle_multiple='random',
                                           rand=scruf.Scruf.state.rand)
        # To get prior behavior, change to
        #lowest_agent = collapse_score_dict(scores, type='min', handle_multiple='first',
        #                                   rand=scruf.Scruf.state.rand)
        # Create empty probability vector
        probs = agents.agent_value_pairs(default=0.0)

        if lowest_agent is not None:
            probs[lowest_agent] = 1.0
        nan_scores = agents.agent_value_pairs(default=float('NaN'))
        return {'fairness scores': scores,
                'compatibility scores': nan_scores,
                'output': probs}

class MostCompatibleAllocationMechanism(AllocationMechanism):
    """
    The MostCompatible allocation mechanism allocates to the agent with the highest compatibility score.
    """

    def __init__(self):
        super().__init__()

    def compute_allocation_probabilities(self, agents, history, context):
        """
        Computes the allocation probabilities for the agents based on their compatibility scores.
        
        Parameters:
        - agents: A list of Agent objects.
        - history: A list of past allocations.
        
        Returns:
        A list of allocation probabilities for the agents.
        """
        # Compute the fairness scores for each agent
        scores = agents.compute_compatibility(context)
        # Find highest compatibility
        highest_agent = collapse_score_dict(scores, type='max', handle_multiple='random',
                                           rand=scruf.Scruf.state.rand)
        # Create empty probability vector
        probs = agents.agent_value_pairs(default=0.0)

        if highest_agent is not None:
            probs[highest_agent] = 1.0
        fairness_values = agents.compute_fairness(history)
        return {'fairness scores': fairness_values,
                'compatibility scores': scores,
                'output': probs}

class AllocationMechanismFactory:
    """
    A factory class for creating AllocationMechanism objects.
    """

    _allocation_mechanism = {}

    @classmethod
    def register_allocation_mechanism(cls, mechanism_type, mechanism_class):
        if not issubclass(mechanism_class, AllocationMechanism):
            raise InvalidAllocationMechanismError(mechanism_class)
        cls._allocation_mechanism[mechanism_type] = mechanism_class

    @classmethod
    def register_allocation_mechanisms(cls, mechanism_specs):
        for mechanism_type, mechanism_class in mechanism_specs:
            cls.register_allocation_mechanism(mechanism_type, mechanism_class)

    @classmethod
    def create_allocation_mechanism(cls, mechanism_type):
        mechanism_class = cls._allocation_mechanism.get(mechanism_type)
        if mechanism_class is None:
            raise UnregisteredAllocationMechanismError(mechanism_type)
        return mechanism_class()


# Register the mechanisms created above
mechanism_specs = [("random_allocation", RandomAllocationMechanism),
                   ("product_allocation", ProductAllocationMechanism),
                   ("weighted_product_allocation", WeightedProductAllocationMechanism),
                   ("least_fair", LeastFairAllocationMechanism),
                   ("most_compatible", MostCompatibleAllocationMechanism)]

AllocationMechanismFactory.register_allocation_mechanisms(mechanism_specs)

