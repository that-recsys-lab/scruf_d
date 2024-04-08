from . import FairnessMetric, FairnessMetricFactory, ItemFeatureFairnessMetric
from abc import abstractmethod
import numpy as np
import scruf

# Calculation is average of (for each list, 1/rank of highest ranked protected item)
class MeanReciprocalRankFM(ItemFeatureFairnessMetric):
    """
    MeanReciprocalRankFM computes the fairness in terms of Mean Reciprocal Rank (MRR) of protected items.
    MRR is a statistic measure for evaluating any process that produces a list of possible responses to a sample of queries,
    ordered by probability of correctness.
    """
    _PROPERTY_NAMES = ['target']

    def __init__(self):
        super().__init__()

    def setup(self, input_props, names=None):
        super().setup(input_props, \
                      names=self.configure_names(MeanReciprocalRankFM._PROPERTY_NAMES, names))

    def __str__(self):
        return f"MeanReciprocalRankFM: feature = {self.get_property('feature')}"

    def compute_fairness(self, history):
        """
        Computes the MRR fairness for the protected feature within the provided history.
        The fairness is computed as the average of reciprocal ranks of the first relevant (protected) item
        encountered in the list of recommendations.
        """
        if history.choice_output_history.is_empty():
            return 1.0

        max_mrr = 0  # To track the maximum MRR across all queries
        protected_feature = self.get_property('feature')
        item_data = scruf.Scruf.state.item_features
        target_mrr = float(self.get_property('target'))

        for result in history.choice_output_history.get_recent(-1):
            mrr_for_query = 0  # MRR for the current query
            for idx, recommendation in enumerate(result.get_results(), start=1):
                if item_data.is_protected(protected_feature, recommendation.item):
                    mrr_for_query = max(mrr_for_query, 1 / idx)
            max_mrr = max(max_mrr, mrr_for_query)


        return max_mrr/target_mrr
class DisparateExposureFM(ItemFeatureFairnessMetric):
    """
    DisparateExposureFM computes fairness by ensuring that protected and non-protected groups receive
    proportional visibility/exposure in the recommendation lists, relative to their representation.
    """
    _PROPERTY_NAMES = ['n_protected', 'target']

    def __init__(self):
        super().__init__()

    def setup(self, input_props, names=None):
        super().setup(input_props, \
                      names=self.configure_names(DisparateExposureFM._PROPERTY_NAMES, names))

    def __str__(self):
        return f"DisparateExposureFM: feature = {self.get_property('feature')}"
    def compute_fairness(self, history):
        """
        Computes the fairness based on the concept of disparate exposure for protected and non-protected
        groups within the provided history. Fairness in this context aims to equalize the exposure of
        protected and non-protected items.
        """
        if history.choice_output_history.is_empty():
            return 1.0

        utility_protected = 0
        utility_non_protected = 0
        protected_feature = self.get_property('feature')
        n_prot = self.get_property('n_protected')
        n_unprot= 1-self.get_property('n_protected')
        target = self.get_property('target')
        item_data = scruf.Scruf.state.item_features

        for result in history.choice_output_history.get_recent(-1):
            rank = 0
            for recommendation in result.get_results():
                rank +=1
                if item_data.is_protected(protected_feature, recommendation.item):
                    utility_protected += 1 / np.log2(rank + 1)
                else:
                    utility_non_protected += 1 / np.log2(rank + 1)

        # Avoid division by zero
        # total_exposure = utility_protected + utility_non_protected
        #if total_exposure == 0:
        #    return 1.0

        # the proportion of exposure between protected and non-protected items has been considered.
        # Adjust this formula based on fairness definition.
        fairness_score = ((utility_protected/n_prot) / (utility_non_protected/n_unprot))/target

        return fairness_score

# Register the metrics created above
metric_specs = [("mrr", MeanReciprocalRankFM), ('disparate_exposure', DisparateExposureFM)]

FairnessMetricFactory.register_fairness_metrics(metric_specs)