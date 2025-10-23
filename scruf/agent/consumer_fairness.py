from . import FairnessMetric, FairnessMetricFactory, ItemFeatureFairnessMetric
from abc import abstractmethod, ABC
import numpy as np
from statistics import mean
import scruf
from joblib import Parallel, delayed


class ConsumerFairnessMetric(FairnessMetric):

    _PROPERTY_NAMES = []

    def __init__(self):
        super().__init__()

    def setup(self, input_props, names=None):
        super().setup(input_props, names=self.configure_names(ConsumerFairnessMetric._PROPERTY_NAMES, names))

    @abstractmethod
    def compute_fairness(self, history):
        pass

    @abstractmethod
    def compute_test_fairness(self, history):
        pass

class ConsumerFM(ConsumerFairnessMetric):
    """
    Returns 1 if consumer is not in protected group and 0 if consumer is in protected group.
    """
    def compute_fairness(self, history):
        user_id = history.get_current_user()
        context = scruf.Scruf.state.context.get_context(user_id)
        feature = self.get_property('feature')
        compat = context[feature]

        if compat == 1.0:
            fairness_score = 0.0
        else:
            fairness_score = 1.0

        return fairness_score

    def compute_test_fairness(self, history):
        return 1.0





# Register the metrics created above
metric_specs = [("consumer", ConsumerFM)]

FairnessMetricFactory.register_fairness_metrics(metric_specs)