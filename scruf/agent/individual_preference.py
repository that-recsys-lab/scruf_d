from .preference_function import PreferenceFunctionFactory, PreferenceFunction
import scruf
import copy
import random
from scruf.util import ResultList
from abc import ABC, abstractmethod



class IndividualPreferenceFunction(PreferenceFunction):

    _PROPERTY_NAMES = ['delta']

    def __init__(self):
        super().__init__()

    def setup(self, input_props, names=None):
        super().setup(input_props, names=self.configure_names(IndividualPreferenceFunction._PROPERTY_NAMES, names))

    def __str__(self):
        delta = self.get_property('delta')
        return f"IndividualPreferenceFunction: delta = {delta}"

    @abstractmethod
    def compute_preferences(self, history):
        pass



class Individual_Norm(IndividualPreferenceFunction):

    # For every item in the list
    #   check how often item is recommended
    #   order list with the least recommended items recommended highest.
    def compute_preferences(self, recommendations: ResultList) -> ResultList:
        rec_list = copy.deepcopy(recommendations)
        counts_dict = scruf.Scruf.state.popularity.popularity_dict
        delta = self.get_property('delta')
        history = scruf.Scruf.state.history
        for result in history.choice_output_history.get_recent(-1):
            for recommendation in result.get_results():
                if recommendation.item in counts_dict:
                    counts_dict[recommendation.item] += 1
                else:
                    counts_dict[recommendation.item] = 1

        max_counts = max(counts_dict.values())
        min_counts = min(counts_dict.values())

        def individual_score(entry):
            frequency = counts_dict.get(entry.item, 0)
            if max_counts != min_counts:
                normalized = (max_counts-frequency) / (max_counts - min_counts)
            else:
                normalized = 1.0
            scaled = entry.score + (delta*normalized)
            return scaled

        rec_list.rescore(individual_score)
        return rec_list

class Individual_Exponential(IndividualPreferenceFunction):

    # For every item in the list
    #   check how often item is recommended
    #   order list with the least recommended items recommended highest.
    def compute_preferences(self, recommendations: ResultList) -> ResultList:
        rec_list = copy.deepcopy(recommendations)
        counts_dict = scruf.Scruf.state.popularity.popularity_dict
        delta = self.get_property('delta')
        history = scruf.Scruf.state.history
        for result in history.choice_output_history.get_recent(-1):
            for recommendation in result.get_results():
                if recommendation.item in counts_dict:
                    counts_dict[recommendation.item] += 1
                else:
                    counts_dict[recommendation.item] = 1

        max_counts = max(counts_dict.values())
        min_counts = min(counts_dict.values())

        def individual_score(entry):
            frequency = counts_dict.get(entry.item, 0)
            if max_counts != min_counts:
                normalized = (max_counts-frequency) / (max_counts - min_counts)
            else:
                normalized = 1.0
            scaled = entry.score + (delta*normalized)**3
            return scaled

        rec_list.rescore(individual_score)
        return rec_list

class Individual_Binary(IndividualPreferenceFunction):

    # For every item in the list
    #   check how often item is recommended
    #   order list with the least recommended items recommended highest.
    def compute_preferences(self, recommendations: ResultList) -> ResultList:
        rec_list = copy.deepcopy(recommendations)
        counts_dict = scruf.Scruf.state.popularity.popularity_dict
        delta = self.get_property('delta')
        history = scruf.Scruf.state.history
        for result in history.choice_output_history.get_recent(-1):
            for recommendation in result.get_results():
                if recommendation.item in counts_dict:
                    counts_dict[recommendation.item] += 1
                else:
                    counts_dict[recommendation.item] = 1

        max_counts = max(counts_dict.values())
        min_counts = min(counts_dict.values())

        def individual_score(entry):
            frequency = counts_dict.get(entry.item, 0)
            if max_counts != min_counts:
                normalized = (max_counts-frequency) / (max_counts - min_counts)
            else:
                normalized = 1.0
            if normalized >= 0.75:
                scaled = entry.score + delta
            else:
                scaled = entry.score
            return scaled

        rec_list.rescore(individual_score)
        return rec_list
# Register the mechanisms created above
pfunc_specs = [("individual_preference", IndividualPreferenceFunction),("ind_norm", Individual_Norm), ("ind_exponential", Individual_Exponential), ("ind_binary", Individual_Binary)]

PreferenceFunctionFactory.register_preference_functions(pfunc_specs)