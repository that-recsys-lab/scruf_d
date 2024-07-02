from abc import ABC, abstractmethod
from scruf.util import InvalidFairnessMetricError, UnregisteredFairnessMetricError, PropertyMixin


class FairnessMetric (PropertyMixin,ABC):
    """
    A FairnessMetric uses a system History to computes a score in the range [0..1] reflecting the
    fairness relative to some particular concern of the outcomes over that history. All metrics are
    initialized with a dictionary of property name, value pairs. Each subclass has to specify the
    property names that it expects.
    """
    def setup(self, input_props, names=None):
        super().setup(input_props, names=names)

    def set_agent(self, agent):
        self.agent = agent

    @abstractmethod
    def compute_fairness(self, history):
        pass
   # @abstractmethod
   # def compute_test_fairness(self, history, test_data):
    #    pass

class AlwaysOneFairnessMetric(FairnessMetric):

    def compute_fairness(self, history):
        return 1.0


class AlwaysZeroFairnessMetric(FairnessMetric):

    def compute_fairness(self, history):
        return 0.0


class FairnessMetricFactory:
    """
    The FairnessMetricFactory associates names with class objects so these can be instantiated
    based on configuration information. A metric must registered in the factory before it can be
    created. Note these are all class methods, so an instance of this object never needs to be created.
    """

    _fairness_metrics = {}

    @classmethod
    def register_fairness_metric(cls, metric_type, metric_class):
        if not issubclass(metric_class, FairnessMetric):
            raise InvalidFairnessMetricError(metric_class)
        cls._fairness_metrics[metric_type] = metric_class

    @classmethod
    def register_fairness_metrics(cls, metric_specs):
        for metric_type, metric_class in metric_specs:
            cls.register_fairness_metric(metric_type, metric_class)

    @classmethod
    def create_fairness_metric(cls, metric_type):
        metric_class = cls._fairness_metrics.get(metric_type)
        if metric_class is None:
            raise UnregisteredFairnessMetricError(metric_type)
        return metric_class()

# Register the metrics created above
metric_specs = [("always_one", AlwaysOneFairnessMetric),
                ("always_zero", AlwaysZeroFairnessMetric)]

FairnessMetricFactory.register_fairness_metrics(metric_specs)
