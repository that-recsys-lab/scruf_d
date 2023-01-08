from .fairness_metric import FairnessMetricFactory
from .compatibility_metric import CompatibilityMetricFactory
from scruf.util.config_util import check_keys
from scruf.util.errors import ConfigKeyMissingError, ConfigNoAgentsError

class FairnessAgent:

    def __init__(self, name):
        self.name = name
        self.fairness_metric = None
        self.compatibility_metric = None

    def setup(self, properties):
        # Set up fairness metric
        fairness_metric_name = properties['metric_class']
        self.fairness_metric = FairnessMetricFactory.create_fairness_metric(fairness_metric_name)

        if 'metric' in properties:
            self.fairness_metric.setup(properties['metric'])
        else:
            self.fairness_metric.setup(dict())

        # Set up compatibility metric
        compatibility_metric_name = properties['compatibility_class']
        self.compatibility_metric = CompatibilityMetricFactory.create_compatibility_metric(compatibility_metric_name)

        if 'compatibility' in properties: #If the metric key is present in the properties dictionary, the setup() method of the fairness metric object is called with the value of the metric key as the parameter. Does the metric key have multiple values?
            self.compatibility_metric.setup(properties['compatibility'])
        else:
            self.compatibility_metric.setup(dict())

class AgentCollection:

    @classmethod
    def check_config(cls, config):
        if not check_keys(config, [['agent']]):
            raise ConfigKeyMissingError('agent')
        if len(config['agent']) == 0:
            raise ConfigNoAgentsError()

    def __init__(self):
        self.agents = []
        self.history = None

    def setup(self, config, fairness_history):
        AgentCollection.check_config(config)

        self.history = fairness_history
        # TODO: Create the agents, collect them in the list
        # Relevant part of the config file: 'agent': tables within

    def compute_fairness(self):
        # TODO: Go through the agent list and compute their fairness values and return vector
        # Or maybe it should be a dictionary keyed by agent name?
        pass

    # TODO: Also some function for use in the choice phase