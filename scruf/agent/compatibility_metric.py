from abc import ABC, abstractmethod
from scruf.util import InvalidCompatibilityMetricError, UnregisteredCompatibilityMetricError, PropertyCollection

class CompatibilityMetric (ABC):
    """
    A CompatibilityMetric uses a system History & * to computes a score in the range [0..1] reflecting the
    compatibility of the users over the Recommended Items with some particular concern. All metrics are
    initialized with a dictionary of property name, value pairs. Each subclass has to specify the
    property names that it expects.
    """

    def __init__(self):
        self.prop_coll = PropertyCollection()

    def setup(self, input_properties: dict, names=None):
        if names is None:
            names = []
        self.prop_coll.setup(input_properties, names)

    def get_property_names(self):
        return self.prop_coll.get_property_names()

    def get_properties(self):
        return self.prop_coll.get_properties()

    def get_property(self, property_name):
        return self.prop_coll.get_property(property_name)

    @abstractmethod
    def compute_compatibility(self, history):
        pass

class AlwaysOneCompatibilityMetric(CompatibilityMetric):

    def compute_compatibility(self, context):
        return 1.0


class AlwaysZeroCompatibilityMetric(CompatibilityMetric):

    def compute_compatibility(self, context):
        return 0.0


class CompatibilityMetricFactory:
    """
    The CompatibilityMetricFactory associates names with class objects so these can be instantiated
    based on configuration information. A metric must registered in the factory before it can be
    created. Note these are all class methods, so an instance of this object never needs to be created.
    """

    _compatibility_metrics = {}

    @classmethod
    def register_compatibility_metric(cls, metric_type, metric_class):
        if not issubclass(metric_class, CompatibilityMetric):
            raise InvalidCompatibilityMetricError(metric_class)
        cls._compatibility_metrics[metric_type] = metric_class

    @classmethod
    def register_compatibility_metrics(cls, metric_specs):
        for metric_type, metric_class in metric_specs:
            cls.register_compatibility_metric(metric_type, metric_class)

    @classmethod
    def create_compatibility_metric(cls, metric_type):
        metric_class = cls._compatibility_metrics.get(metric_type)
        if metric_class is None:
            raise UnregisteredCompatibilityMetricError(metric_type)
        return metric_class()

# Register the metrics created above
metric_specs = [("always_one", AlwaysOneCompatibilityMetric),
                ("always_zero", AlwaysZeroCompatibilityMetric)]

CompatibilityMetricFactory.register_compatibility_metrics(metric_specs)

