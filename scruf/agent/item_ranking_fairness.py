from . import FairnessMetric, FairnessMetricFactory, ItemFeatureFairnessMetric
from abc import abstractmethod
import scruf

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
        mrr_total = 0
        protected_feature = self.get_property('feature')
        item_data = scruf.Scruf.state.item_features
        num_queries = 0

        for result in history.choice_output_history.get_recent(-1):
            for idx, recommendation in enumerate(result.get_results(), start=1):
                if item_data.is_protected(protected_feature, recommendation.item):
                    mrr_total += 1 / idx
                    break
            num_queries += 1

        # Avoid division by zero if there are no queries
        if num_queries == 0:
            return 1.0

        mrr_score = mrr_total / num_queries
        return mrr_score

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

        for result in history.choice_output_history.get_recent(-1):
            for recommendation in result.get_results():
                if item_data.is_protected(protected_feature, recommendation.item):
                    exposure_protected += 1
                else:
                    exposure_non_protected += 1

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
