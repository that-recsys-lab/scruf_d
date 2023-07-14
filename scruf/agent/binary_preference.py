from .preference_function import PreferenceFunctionFactory, PreferenceFunction
import scruf
import copy
import random
from scruf.util import ResultList


# Requires knowing protected items
class BinaryPreferenceFunction(PreferenceFunction):

    # Need to get the value as a property
    # Need to get protected feature as a property
    _PROPERTY_NAMES = ['feature', 'delta']

    def __init__(self):
        super().__init__()

    def setup(self, input_props, names=None):
        super().setup(input_props, names=self.configure_names(BinaryPreferenceFunction._PROPERTY_NAMES, names))


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
        feature = self.get_property('feature')
        delta = self.get_property('delta')
        rec_list.rescore(lambda entry: delta if if_data.is_protected(feature, entry.item) else 0.0)
        return rec_list


# Adds a random value to the binary rescoring effectively making it a total order instead of a partial order.
class PerturbedBinaryPreferenceFunction(BinaryPreferenceFunction):
    def __init__(self):
        super().__init__()

    def __str__ (self):
        prot_feature = self.get_property('protected_feature')
        delta = self.get_property('delta')
        return f"PerturbedPreferenceFunction: protected feature = {prot_feature}, delta = {delta}"

    def compute_preferences(self, recommendations: ResultList) -> ResultList:
        rand: random.Random = scruf.Scruf.state.rand
        delta = float(self.get_property('delta'))
        rec_list = super().compute_preferences(recommendations)
        rec_list.rescore(lambda entry: entry.score + delta * rand.gauss(0, 0.1))
        return rec_list

# Register the mechanisms created above
pfunc_specs = [("binary_preference", BinaryPreferenceFunction),
               ("perturbed_binary", PerturbedBinaryPreferenceFunction)]

PreferenceFunctionFactory.register_preference_functions(pfunc_specs)
