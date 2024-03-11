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

    def compute_fairness(self, history):
        """
        Computes the MRR fairness for the protected feature within the provided history.
        The fairness is computed as the average of reciprocal ranks of the first relevant (protected) item
        encountered in the list of recommendations.
        """

        max_mrr = 0  # To track the maximum MRR across all queries
        protected_feature = self.get_property('feature')
        item_data = scruf.Scruf.state.item_features

        for result in history.choice_output_history.get_recent(-1):
            mrr_for_query = 0  # MRR for the current query
            for idx, recommendation in enumerate(result.get_results(), start=1):
                if item_data.is_protected(protected_feature, recommendation.item):
                    mrr_for_query = max(mrr_for_query, 1 / idx)
            max_mrr = max(max_mrr, mrr_for_query)

        # If there are no queries or no protected items were found, max_mrr remains 0, indicating no fairness issue.
        return max_mrr if max_mrr > 0 else 1.0


# Calculate sum of utility for protected group items, compare to unprotected items.
# protected group utility / unprotected utility.
# 1 / log_2(rank + 1) (if zero-based, rank + 2)
class DisparateExposureFM(ItemFeatureFairnessMetric):
    """
    DisparateExposureFM computes fairness by ensuring that protected and non-protected groups receive
    proportional visibility/exposure in the recommendation lists, relative to their representation.
    """

    def compute_fairness(self, history):
        """
        Computes the fairness based on the concept of disparate exposure for protected and non-protected
        groups within the provided history. Fairness in this context aims to equalize the exposure of
        protected and non-protected items.
        """
        exposure_protected = 0
        exposure_non_protected = 0
        protected_feature = self.get_property('feature')
        item_data = scruf.Scruf.state.item_features

        for i, result in history.choice_output_history.get_recent(-1):
            rank = 0
            for recommendation in result.get_results():
                rank +=1
                if item_data.is_protected(protected_feature, recommendation.item):
                    exposure_protected += 1 / np.log2(rank + 1)
                else:
                    exposure_non_protected += 1 / np.log2(rank + 1)

        # Avoid division by zero
        total_exposure = exposure_protected + exposure_non_protected
        if total_exposure == 0:
            return 1.0

        # the proportion of exposure between protected and non-protected items has been considered.
        # Adjust this formula based on fairness definition.
        fairness_score = exposure_protected / total_exposure

        return fairness_score

# Register the metrics created above
metric_specs = [("mrr", MeanReciprocalRankFM), ('disparate_exposure', DisparateExposureFM)]

FairnessMetricFactory.register_fairness_metrics(metric_specs)