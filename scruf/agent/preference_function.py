import copy
from abc import ABC, abstractmethod
from scruf.util import InvalidPreferenceFunctionError, UnregisteredPreferenceFunctionError, \
    PropertyMixin, ResultList

class PreferenceFunction(PropertyMixin,ABC):

    @abstractmethod
    def compute_preferences(self, recommendations: ResultList) -> ResultList:
        pass

class ZeroPreference(PreferenceFunction):

    # Return a new result list with all zeros.
    def compute_preferences(self, recommendations: ResultList) -> ResultList:
        rec_list = copy.deepcopy(recommendations)
        rec_list.rescore_no_sort(lambda entry: 0.0)
        return rec_list


class PreferenceFunctionFactory:
    """
    The PreferenceFunctionFactory associates names with class objects so these can be instantiated
    based on configuration information. A preference function must registered in the factory before it can be
    created. Note these are all class methods, so an instance of this object never needs to be created.
    """

    _preference_functions = {}

    @classmethod
    def register_preference_function(cls, metric_type, metric_class):
        if not issubclass(metric_class, PreferenceFunction):
            raise InvalidPreferenceFunctionError(metric_class)
        cls._preference_functions[metric_type] = metric_class

    @classmethod
    def register_preference_functions(cls, metric_specs):
        for metric_type, metric_class in metric_specs:
            cls.register_preference_function(metric_type, metric_class)

    @classmethod
    def create_preference_function(cls, metric_type):
        metric_class = cls._preference_functions.get(metric_type)
        if metric_class is None:
            raise UnregisteredPreferenceFunctionError(metric_type)
        return metric_class()


pfunc_specs = [("zero_preference", ZeroPreference)]

PreferenceFunctionFactory.register_preference_functions(pfunc_specs)
