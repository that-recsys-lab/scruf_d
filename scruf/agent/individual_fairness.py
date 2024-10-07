from . import FairnessMetric, FairnessMetricFactory, ItemFeatureFairnessMetric
from abc import abstractmethod, ABC
import numpy as np
from statistics import mean
import scruf


class IndividualFairnessMetric(FairnessMetric):
    """
    An IndividualFairnessMetric is one where recommended items are ...
    """
    _PROPERTY_NAMES = []

    def __init__(self):
        super().__init__()

    def setup(self, input_props, names=None):
        super().setup(input_props, names=self.configure_names(IndividualFairnessMetric._PROPERTY_NAMES, names))

    @abstractmethod
    def compute_fairness(self, history):
        pass

    @abstractmethod
    def compute_test_fairness(self, history):
        pass


class GiniIndexFM(IndividualFairnessMetric):
    """
    The gini index computes the fairness in terms of .
    """
    _PROPERTY_NAMES = []

    def __init__(self):
        super().__init__()

    def setup(self, input_props, names=None):
        super().setup(input_props,
                      names=self.configure_names(GiniIndexFM._PROPERTY_NAMES, names))

    def compute_fairness(self, history):
        """
        Computes the
        """
        if history.choice_output_history.is_empty():
            return 1.0
        n = scruf.Scruf.state.item_features.item_feature_index.__len__()
        counts_dict = {}
        for result in history.choice_output_history.get_recent(-1):
            for recommendation in result.get_results():
                if recommendation.item in counts_dict:
                    counts_dict[recommendation.item] += 1
                else:
                    counts_dict[recommendation.item] = 1
        item_recs = list(counts_dict.values())
        zeros_to_add = n - len(item_recs)
        for i in range(zeros_to_add):
            item_recs.append(0)
        item_recs.sort()
        position_sum = 0
        for i, value in enumerate(item_recs, 1):
            position_sum += i * value
        value_sum = sum(item_recs)
        half_relative_mean = (2*position_sum) / (n*value_sum)
        fairness_score = half_relative_mean - ((n + 1) / n)

        return fairness_score

    def compute_test_fairness(self, history):
        fairness_score = 1.0
        return fairness_score
        """  protected_feature = self.get_property('feature')
        item_data = scruf.Scruf.state.item_features
        target_mrr = float(self.get_property('target'))
        mrr = []

        for result in history:
            mrr_for_query = 0.0
            for idx, recommendation in enumerate(result, start=1):
                if item_data.is_protected(protected_feature, recommendation):
                    mrr_for_query = max(mrr_for_query, 1.0 / idx)
                    mrr.append(mrr_for_query)
                    break
                if idx == 10:
                    mrr.append(0)
        avg_mrr = mean(mrr)
        fair_mrr = avg_mrr / target_mrr"""




# Register the metrics created above
metric_specs = [("gini", GiniIndexFM)]

FairnessMetricFactory.register_fairness_metrics(metric_specs)
