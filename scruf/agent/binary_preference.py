from .preference_function import PreferenceFunctionFactory, PreferenceFunction
import scruf
import copy
from scruf.util import ResultList


# Requires knowing protected items
class BinaryPreferenceFunction(PreferenceFunction):

    # Need to get the value as a property
    # Need to get protected feature as a property
    _PROPERTY_NAMES = ['feature', 'delta']

    def __init__(self):
        super().__init__()

    def __str__(self):
        prot_feature = self.get_property('protected_feature')
        delta = self.get_property('delta')
        return f"BinaryPreferenceFunction: protected feature = {prot_feature}, delta = {delta}"

    # For every item in the list
    #   check if it is in the protected feature set
    #   if so, replace the score with the score + value
    #  return the list.
    # List size is ignored.
    def compute_preferences(self, recommendations: ResultList) -> ResultList:
        rec_list = copy.deepcopy(recommendations)

        if_data = scruf.Scruf.state.item_features
        feature = self.get_property('protected_feature')
        delta = self.get_property('delta')
        rec_list.rescore(lambda entry: delta if if_data.is_protected(feature, entry.item) else 0.0)
        return rec_list


# Register the mechanisms created above
pfunc_specs = [("binary_preference", BinaryPreferenceFunction)]

PreferenceFunctionFactory.register_preference_functions(pfunc_specs)
