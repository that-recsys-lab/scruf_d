import copy
from abc import ABC, abstractmethod
from scruf.util import InvalidChoiceScorerError, UnregisteredChoiceScorerError, PropertyMixin, ResultList

class ChoiceScorer(PropertyMixin,ABC):

    @abstractmethod
    def score_choices(self, rec_list: ResultList, list_size, inplace=False) -> ResultList:
        pass


class ZeroScorer(ChoiceScorer):
    def score_choices(self, rec_list: ResultList, list_size, inplace=False) -> ResultList:
        if inplace is False:
            rec_list = copy.deepcopy(rec_list)
        rec_list.rescore_no_sort(lambda entry: 0.0)
        return rec_list

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

scorer_specs = [("zero_scorer", ZeroScorer)]

ChoiceScorerFactory.register_choice_scorers(scorer_specs)

