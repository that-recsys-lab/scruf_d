from . import FairnessMetric, FairnessMetricFactory

class ItemFeatureFairnessMetric(FairnessMetric):
    """
    An ItemFeatureFairnessMetric is one where recommended items are associated with a single protected
    feature and a set of protected values.
    """
    _PROPERTY_NAMES = ['protected_feature', 'protected_values']

    def __init__(self):
        super().__init__()

    def __str__(self):
        return f"ItemFeatureFairnessMetric: feature = {self.properties['protected_feature']}"

    def setup_property_names(self, names=None):
        if names is None:
            names = []

        super().setup_property_names(names + ItemFeatureFairnessMetric._PROPERTY_NAMES)

    def compute_fairness(self, history):
        return float('nan')


class ProportionalItemFM(ItemFeatureFairnessMetric):
    """
    A ProportionalItemFM (fairness metric) is an item feature metric where fairness is a function of
    a specific proportion of the recommended items in the history that are protected. If the proportion
    is >= the given value, the fairness is 1.0. It linearly interpolates to zero.
    """

    _PROPERTY_NAMES = ['proportion']

    def __init__(self):
        super().__init__()

    def __str__(self):
        return f"ProporationalItemFM: feature = {self.properties['protected_feature']}"

    def setup_property_names(self, names=None):
        if names is None:
            names = []

        super().setup_property_names(names + ProportionalItemFM._PROPERTY_NAMES)

    def compute_fairness(self, history):
        return float('nan')

# Register the metrics created above
metric_specs = [("proportional_item", ProportionalItemFM),
                ("item_feature", ItemFeatureFairnessMetric)]

FairnessMetricFactory.register_fairness_metrics(metric_specs)