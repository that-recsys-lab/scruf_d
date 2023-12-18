from . import FairnessMetric, FairnessMetricFactory, ItemFeatureFairnessMetric
from abc import abstractmethod
import scruf

class MeanReciprocalRankFM(ItemFeatureFairnessMetric):

    def compute_fairness(self, history):
        pass

class DisparateExposureFM(ItemFeatureFairnessMetric):

    def compute_fairness(self, history):
        pass

# Register the metrics created above
metric_specs = [("mrr", MeanReciprocalRankFM), ('disparate_exposure', DisparateExposureFM)]

FairnessMetricFactory.register_fairness_metrics(metric_specs)