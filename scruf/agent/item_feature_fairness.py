from . import FairnessMetric, FairnessMetricFactory
from abc import abstractmethod
import scruf
from icecream import ic
import numpy as np

class ItemFeatureFairnessMetric(FairnessMetric):
    """
    An ItemFeatureFairnessMetric is one where recommended items are associated with a protected
    feature defined in the feature section.
    """
    _PROPERTY_NAMES = ['feature']

    def __init__(self):
        super().__init__()

    def setup(self, input_props, names=None):
        super().setup(input_props, names=self.configure_names(ItemFeatureFairnessMetric._PROPERTY_NAMES, names))

    def __str__(self):
        return f"ItemFeatureFairnessMetric: feature = {self.get_property('feature')}"

    @abstractmethod
    def compute_fairness(self, history):
        pass

    @abstractmethod
    def compute_test_fairness(self, history):
        pass


class ProportionalItemFM(ItemFeatureFairnessMetric):
    """
    A ProportionalItemFM (fairness metric) is an item feature metric where fairness is a function of
    a specific proportion of the recommended items in the history that are protected. If the proportion
    is >= the given value, the fairness is 1.0. It linearly interpolates to zero.
    """

    _PROPERTY_NAMES = ['proportion']

    def __init__(self):
        super().__init__()

    def setup(self, input_props, names=None):
        super().setup(input_props, \
                      names=self.configure_names(ProportionalItemFM._PROPERTY_NAMES, names))

    def __str__(self):
        return f"ProportionalItemFM: feature = {self.get_property('feature')}"

    # No data means assume fairness
    # Might want this to be configurable.
    def compute_fairness(self, history):
        if history.choice_output_history.is_empty():
            return 1.0
        else:
            prior_results = history.choice_output_history.get_recent(-1)
            target_proportion = float(self.get_property('proportion'))
            protected, total_items = self.count_protected(prior_results)
            protected_ratio = float(protected) / total_items
            # If protected ratio is at or above
            if protected_ratio > target_proportion:
                protected_ratio = target_proportion
            # 1.0 is ratio = target
            fairness_value = protected_ratio / target_proportion
            return fairness_value

    def compute_test_fairness(self, history):

        target_proportion = float(self.get_property('proportion'))
        protected, total_items = self.count_test_protected(history)
        protected_ratio = float(protected) / total_items
        # If protected ratio is at or above
        if protected_ratio > target_proportion:
            protected_ratio = target_proportion
            # 1.0 is ratio = target
        fairness_value = protected_ratio / target_proportion
        return fairness_value


    def count_protected(self, history_entries):
        feature = self.get_property('feature')
        item_data = scruf.Scruf.state.item_features
        protected_count = 0
        total_count = 0
        for result in history_entries:
            #result = history_entry['output']
            protected_vector = [1 if item_data.is_protected(feature, result_entry.item) else 0 \
                                    for result_entry in result.get_results()]
            protected_count += sum(protected_vector)
            total_count += len(result.get_results())

        return protected_count, total_count

    def count_test_protected(self, history_entries):
        feature = self.get_property('feature')
        item_data = scruf.Scruf.state.item_features
        protected_count = 0
        results = [item for sublist in history_entries for item in sublist]
        for result in results:
            #result = history_entry['output']
            protected_vector = [1 if item_data.is_protected(feature, result) else 0]
            protected_count += sum(protected_vector)
        total_count = len(results)

        return protected_count, total_count



# Register the metrics created above
metric_specs = [("proportional_item", ProportionalItemFM)]

FairnessMetricFactory.register_fairness_metrics(metric_specs)