from abc import ABC, abstractmethod
from scruf.util import PropertyMismatchError, InvalidChoiceMechanismError, UnregisteredChoiceMechanismError

class ChoiceMechanism:
    """
    A ChoiceMechanism takes in a list of allocation probabilities for all agents per user, a list of recommended items for each user, and
    a list of agents, and selects an agent for each user based on the allocation probabilities. After this the agent's preferred item is given 
    a boost in the ranking of the recommended items. Finally, a new recommended list is generated for each user based on the boosted ranking.
    """

    def __init__(self):
        self.property_names = []
        self.properties = {}
        self.allocation_probabilities = []
        self.recommended_items = []
        self.agents = []

    @abstractmethod
    # Only in this method are the property names set. The property name list is built up
    # through calls to super().
    def setup_property_names(self, names):
        self.property_names = names

    def get_property_names(self):
        return self.property_names

    def get_properties(self):
        return self.properties

    def get_property(self, property_name):
        return self.properties[property_name]

    def setup(self, input_properties: dict, allocation_probabilities, recommended_items, agents):
        """
        Checks the properties provided with those expected by the object, sets up the allocation probabilities, 
        recommended items, and agents for the ChoiceMechanism.
        :param input_properties:
        :param allocation_probabilities: a list of allocation probabilities for the agents
        :param recommended_items: a list of recommended items for each agent
        :param agents: a list of Agent objects
        :return:
        """
        self.setup_property_names()

        self.properties = {}
        input_property_names = input_properties.keys()

        self._check_properties(self.property_names, input_property_names)

        for key in input_property_names:
            self.properties[key] = input_properties[key]

        self.allocation_probabilities = allocation_probabilities
        self.recommended_items = recommended_items
        self.agents = agents

    def _check_properties(self, my_properties, input_properties):
        set_my_properties = set(my_properties)
        set_input_properties = set(input_properties)

        diff_left = set_my_properties - set_input_properties
        diff_right = set_input_properties - set_my_properties

        if len(diff_left) == 0 and len(diff_right) == 0:
            return
        else:
            raise PropertyMismatchError(self, list(diff_left), list(diff_right))

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





