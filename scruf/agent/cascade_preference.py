from .preference_function import PreferenceFunctionFactory, PreferenceFunction
from .binary_preference import BinaryPreferenceFunction
import scruf
import copy
import random
from scruf.util import ResultList


# This preference function is not recommended for choice mechanisms that rely on
# adding scores between agent preferences and the recommendations.
class CascadePreferenceFunction(BinaryPreferenceFunction):

    # maybe this should be a parameter, but I can't think of a good reason why you'd want to change it.
    CASCADE_FACTOR = 0.5

    def __init__(self):
        super().__init__()

    def __str__ (self):
        prot_feature = self.get_property('protected_feature')
        return f"CascadePreferenceFunction: protected feature = {prot_feature}"

    # Formula for the cascaded preference is
    # ((original_score - min_score) / max_score) * 1/2 * delta +
    #    0 if not protected
    #    delta if protected
    # The new range of the data will be delta * 1.5 to zero and all the scores >= delta will be protected
    # All the scores < delta will be unprotected.
    def compute_preferences(self, recommendations: ResultList) -> ResultList:
        rec_list = copy.deepcopy(recommendations)
        max_score, min_score = recommendations.score_range()

        if_data = scruf.Scruf.state.item_features
        feature = self.get_property('feature')
        delta = self.get_property('delta')

        # Didn't want to cram this whole thing into the rescore call.
        def cascade_score(entry):
            normalized = (entry.score - min_score) / (max_score - min_score)
            scaled = normalized * CascadePreferenceFunction.CASCADE_FACTOR * delta
            if if_data.is_protected(feature, entry.item):
                return scaled + delta
            else:
                return scaled

        rec_list.rescore(cascade_score)
        return rec_list


# Register the mechanisms created above
pfunc_specs = [("cascade_preference", CascadePreferenceFunction)]

PreferenceFunctionFactory.register_preference_functions(pfunc_specs)