from . import FairnessMetric, FairnessMetricFactory, ItemFeatureFairnessMetric
from abc import abstractmethod
import scruf

# Calculation is average of (for each list, 1/rank of highest ranked protected item)
class MeanReciprocalRankFM(ItemFeatureFairnessMetric):

    def compute_fairness(self, history):
        pass

# Calculate sum of utility for protected group items, compare to unprotected items.
# protected group utility / unprotected utility.
# 1 / log_2(rank + 1) (if zero-based, rank + 2)
class DisparateExposureFM(ItemFeatureFairnessMetric):

    def compute_fairness(self, history):
        pass

# Register the metrics created above
metric_specs = [("mrr", MeanReciprocalRankFM), ('disparate_exposure', DisparateExposureFM)]

FairnessMetricFactory.register_fairness_metrics(metric_specs)