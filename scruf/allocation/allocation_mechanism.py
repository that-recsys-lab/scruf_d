from abc import ABC, abstractmethod
from scruf.util import PropertyCollection, InvalidAllocationMechanismError, UnregisteredAllocationMechanismError
from scruf.agent import AgentCollection
import random

class AllocationMechanism(ABC):
    """
    An AllocationMechanism computes allocation probabilities for a
    collection of FairnessAgents based on their fairness and compatibility scores. All mechanisms are
    initialized with a dictionary of property name, value pairs. Each subclass has to specify the
    property names that it expects.
    """

    def __init__(self):
        self.prop_coll = PropertyCollection()

    def setup(self, input_properties: dict, names=None):
        if names is None:
            names = []
        self.prop_coll.setup(input_properties, names)

    def get_property_names(self):
        return self.prop_coll.get_property_names()

    def get_properties(self):
        return self.prop_coll.get_properties()

    def get_property(self, property_name):
        return self.prop_coll.get_property(property_name)

    @abstractmethod
    def compute_allocation_probabilities(self, agents, history, context):
        pass


class RandomAllocationMechanism(AllocationMechanism):

    def compute_allocation_propabilities(self, agents, history, context):
        if agents:
            allocation_probabilities = [0] * len(agents)
            selected = random.randint(0, len(agents))
            allocation_probabilities[selected] = 1


class ProductAllocationMechanism(AllocationMechanism):
    
    def compute_allocation_probabilities(self, agents, history, context):
        """
        Computes the allocation probabilities for a collection of FairnessAgents based on their fairness
        and compatibility scores, and normalizes the values to ensure that they sum to 1.
        :param agents: a list of FairnessAgent objects
        :param history: a system History object
        :param context: a Context objedct
        :return: a dictionary mapping agent names to allocation probabilities
        """
        # Compute the fairness and compatibility scores for each agent
        scores = {}
        for agent in agents:
            fairness_score = agent.compute_fairness(history)
            compatibility_score = agent.compute_compatibility(context)
            scores[agent.name] = (1 - fairness_score) * compatibility_score

        # Normalize the scores to sum to 1
        total_score = sum(scores.values())
        normalized_scores = {k: v / total_score for k, v in scores.items()}
        return normalized_scores

class LeastFair(AllocationMechanism):
    """
    The LeastFair allocation mechanism allocates to the agent with the lowest fairness score.
    """

    def compute_allocation_probabilities(self, agents, history, context):
        if agents:  # If there are agents
            # Compute the fairness scores for each agent
            scores = [agent.compute_fairness(history) for agent in agents]

            allocation_probabilities = [0] * len(agents)  # Initialize probabilities to 0 for all agents

            min_index = scores.index(min(scores))
            allocation_probabilities[min_index] = 1  # Allocate 1 to the agent with the lowest fairness score
            return allocation_probabilities
        else:
            return None

class MostCompatible(AllocationMechanism):
    """
    The MostCompatible allocation mechanism allocates to the agent with the highest compatibility score.
    """

    def compute_allocation_probabilities(self, agents, history, context):
        """
        Computes the allocation probabilities for the agents based on their compatibility scores.
        
        Parameters:
        - agents: A list of Agent objects.
        - history: A list of past allocations.
        
        Returns:
        A list of allocation probabilities for the agents.
        """
        if agents:  # If there are agents
            allocation_probabilities = [0] * len(agents)  # Initialize probabilities to 0 for all agents
            # Compute the compatibility scores for each agent
            scores = [agent.compute_compatibility(context) for agent in agents]
            # Find the index of the agent with the highest compatibility score
            max_index = scores.index(scores.max())
            allocation_probabilities[max_index] = 1  # Allocate 1 to the agent with the highest compatibility score
            return allocation_probabilities
        else:
            return None

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
mechanism_specs = [("random_allocation", ProductAllocationMechanism),
                ("least_fair", LeastFair),
                ("most_compatible", MostCompatible)]

AllocationMechanismFactory.register_allocation_mechanism(mechanism_specs)

