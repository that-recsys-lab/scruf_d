from abc import ABC, abstractmethod
from scruf.util import PropertyMismatchError, InvalidCompatibilityMetricError, UnregisteredCompatibilityMetricError

class CompatibilityMetric (ABC):
    """
    A CompatibilityMetric uses a system History & * to computes a score in the range [0..1] reflecting the
    compatibility of the users over the Recommended Items with some particular concern. All metrics are
    initialized with a dictionary of property name, value pairs. Each subclass has to specify the
    property names that it expects.
    """

    def __init__(self):
        self.property_names = []
        self.properties = {}

    @abstractmethod
    # Only in this method are the property names set. The property name list is built up
    # through calls to super().
    def setup_property_names(self, names):
        self.property_names = names

    def get_property_names(self):
        return self.property_names

    def get_properties(self):
        return self.properties

    def get_property(self, property_name):
        return self.properties[property_name]

    def setup(self, input_properties: dict):
        """
        Checks the properties provided with those expected by the object
        :param input_properties:
        :return:
        """
        self.setup_property_names()

        self.properties = {}
        input_property_names = input_properties.keys()

        self._check_properties(self.property_names, input_property_names)

        for key in input_property_names:
            self.properties[key] = input_properties[key]

    def _check_properties(self, my_properties, input_properties):
        set_my_properties = set(my_properties)
        set_input_properties = set(input_properties)

        diff_left = set_my_properties - set_input_properties
        diff_right = set_input_properties - set_my_properties

        if len(diff_left) == 0 and len(diff_right) == 0:
            return
        else:
            raise PropertyMismatchError(self, list(diff_left), list(diff_right))

    @abstractmethod
    def compute_compatibility(self, history):
        pass

class AlwaysOneCompatibilityMetric(CompatibilityMetric):

    def compute_compatibility(self, history):
        return 1.0


class AlwaysZeroCompatibilityMetric(CompatibilityMetric):

    def compute_compatibility(self, history):
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
        metric_class = cls._fairness_metrics.get(metric_type)
        if metric_class is None:
            raise UnregisteredCompatibilityMetricError(metric_type)
        return metric_class()

# Register the metrics created above
metric_specs = [("always_one", AlwaysOneCompatibilityMetric),
                ("always_zero", AlwaysZeroCompatibilityMetric)]

CompatibilityMetricFactory.register_compatibility_metrics(metric_specs)

