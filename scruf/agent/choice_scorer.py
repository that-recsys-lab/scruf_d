from abc import ABC, abstractmethod
from scruf.util import InvalidChoiceScorerError, UnregisteredChoiceScorerError, PropertyCollection, ResultList

class ChoiceScorerMetric (ABC):

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
    def score_choices(self, rec_list: ResultList, list_size) -> ResultList:
        pass


# Requires knowing protected items
#class FixedIncrementChoiceScorer(ChoiceScorerMetric):