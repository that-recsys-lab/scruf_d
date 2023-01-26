import copy
from abc import ABC, abstractmethod
from scruf.util import InvalidChoiceScorerError, UnregisteredChoiceScorerError, PropertyCollection, ResultList

class ChoiceScorer(ABC):

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
    def score_choices(self, rec_list: ResultList, list_size, inplace=False) -> ResultList:
        pass

class ChoiceScorerFactory:
    """
    The ChoiceScorerFactory associates names with class objects so these can be instantiated
    based on configuration information. A scorer must registered in the factory before it can be
    created. Note these are all class methods, so an instance of this object never needs to be created.
    """

    _choice_scorers = {}

    @classmethod
    def register_choice_scorer(cls, metric_type, metric_class):
        if not issubclass(metric_class, ChoiceScorer):
            raise InvalidChoiceScorerError(metric_class)
        cls._choice_scorers[metric_type] = metric_class

    @classmethod
    def register_choice_scorers(cls, metric_specs):
        for metric_type, metric_class in metric_specs:
            cls.register_choice_scorer(metric_type, metric_class)

    @classmethod
    def create_choice_scorer(cls, metric_type):
        metric_class = cls._choice_scorers.get(metric_type)
        if metric_class is None:
            raise UnregisteredChoiceScorerError(metric_type)
        return metric_class()


