from abc import ABC, abstractmethod
from scruf.util import PropertyMismatchError, InvalidChoiceMechanismError, UnregisteredChoiceMechanismError

class ChoiceMechanism:
    """
    A ChoiceMechanism takes in a list of allocation probabilities for all agents per user, a list of recommended items for each user, and
    a list of agents, and selects an agent for each user based on the allocation probabilities. After this the agent's preferred item is given 
    a boost in the ranking of the recommended items. Finally, a new recommended list is generated for each user based on the boosted ranking.
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
    def compute_choice(self, agents, allocation_probabilities, recommended_items):
        pass

class RandomChoice(ChoiceMechanism):
    """
    A RandomChoice mechanism selects an agent for each user based on the allocation probabilities.
    """

    def __init__(self):
        super().__init__()
        
    def compute_choice(self, agents, allocation_probabilities, recommended_items):
        """
        Selects the agent with the highest allocation probability for each user.
        :return: selected agent for each user
        """
        selected_agents = []
        for i, agent in enumerate(agents):
            max_prob = max(allocation_probabilities)
            if allocation_probabilities[i] == max_prob:
                selected_agents.append(agent)
            else:
                selected_agents.append(None)
        return selected_agents

class ChoiceMechanismFactory:
    """
    A factory class for creating ChoiceMechanism objects.
    """

    _choice_mechanisms = {}

    @classmethod
    def register_choice_mechanism(cls, mechanism_type, mechanism_class):
        if not issubclass(mechanism_class, ChoiceMechanism):
            raise InvalidChoiceMechanismError(mechanism_class)
        cls._choice_mechanisms[mechanism_type] = mechanism_class

    @classmethod
    def register_choice_mechanisms(cls, mechanism_specs):
        for mechanism_type, mechanism_class in mechanism_specs:
            cls.register_choice_mechanism(mechanism_type, mechanism_class)

    @classmethod
    def create_choice_mechanism(cls, mechanism_type):
        mechanism_class = cls._choice_mechanisms.get(mechanism_type)
        if mechanism_class is None:
            raise UnregisteredChoiceMechanismError(mechanism_type)
        return mechanism_class()

# Register the mechanisms created above
mechanism_specs = [("random_choice", RandomChoice)]

ChoiceMechanismFactory.register_choice_mechanism(mechanism_specs)





