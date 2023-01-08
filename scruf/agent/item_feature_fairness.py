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
        return f"ItemFeatureFairnessMetric: feature = {self.get_property('protected_feature')}"

    def setup(self, input_properties: dict, names=None):
        if names is None:
            names = ItemFeatureFairnessMetric._PROPERTY_NAMES
        else:
            names = ItemFeatureFairnessMetric._PROPERTY_NAMES + names
        super().setup(input_properties, names)

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
        return f"ProportionalItemFM: feature = {self.get_propery('protected_feature')}"

    def setup(self, input_properties: dict, names=None):
        if names is None:
            names = ProportionalItemFM._PROPERTY_NAMES
        else:
            names = ProportionalItemFM._PROPERTY_NAMES + names
        super().setup(input_properties, names)

    def compute_fairness(self, history):
        return float('nan')


# Register the metrics created above
metric_specs = [("proportional_item", ProportionalItemFM),
                ("item_feature", ItemFeatureFairnessMetric)]

FairnessMetricFactory.register_fairness_metrics(metric_specs)