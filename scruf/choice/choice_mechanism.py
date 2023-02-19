import copy
from abc import ABC, abstractmethod

from scruf.agent import AgentCollection
from scruf.util import PropertyMismatchError, InvalidChoiceMechanismError, UnregisteredChoiceMechanismError, \
    ResultList, PropertyMixin
import scruf

class ChoiceMechanism(PropertyMixin,ABC):
    """
    A ChoiceMechanism takes in a list of allocation probabilities for all agents per user, a list of recommended items for each user, and
    a list of agents, and selects an agent for each user based on the allocation probabilities. After this the agent's preferred item is given 
    a boost in the ranking of the recommended items. Finally, a new recommended list is generated for each user based on the boosted ranking.
    """

    def do_choice(self, allocation_probabilities, recommendations):
        agents = scruf.Scruf.state.agents
        list_size = scruf.Scruf.state.output_list_size
        results = self.compute_choice(agents, allocation_probabilities, recommendations, list_size)
        scruf.Scruf.state.history.choice_history.add_item(results)
        return results

    @abstractmethod
    def compute_choice(self, agents: AgentCollection, allocation_probabilities, recommended_items: ResultList, list_size):
        pass

class NullChoiceMechanism(ChoiceMechanism):
    """
    The agents have no influence on the recommendations
    """

    def __init__(self):
        super().__init__()
        
    def compute_choice(self, agents, allocation_probabilities, recommended_items: ResultList, list_size):
        """
        Returns the recommendation list without any .
        :return: selected agent for each user
        """
        output = copy.deepcopy(recommended_items)
        output.trim(list_size)
        return {'original': recommended_items,
                'output': output}

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
mechanism_specs = [("null_choice", NullChoiceMechanism)]

ChoiceMechanismFactory.register_choice_mechanisms(mechanism_specs)





