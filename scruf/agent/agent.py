from .fairness_metric import FairnessMetricFactory
from .compatibility_metric import CompatibilityMetricFactory
from scruf.util.config_util import check_keys
from scruf.util.errors import ConfigKeyMissingError, ConfigNoAgentsError
import icecream as ic

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

    def agent_names(self):
        return [agent.name for agent in self.agents]

    def agent_value_pairs(self, default=0.0):
        return {name:default for name in self.agent_names()}

    def setup(self, config, fairness_history):
        AgentCollection.check_config(config)

        self.history = fairness_history
        # ic(config['agent'])
        # TODO: Create the agents, collect them in the list
        # Relevant part of the config file: 'agent': tables within

    def compute_fairness(self, history):
        return {agent.name: agent.fairness_metric.compute_fairness(history) \
                    for agent in self.agents}

    def compute_compatibility(self, context):
        return {agent.name: agent.compatibility_metric.compute_compatibility(context) \
                    for agent in self.agents}


    # TODO: Also some function for use in the choice phase