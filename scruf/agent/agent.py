from .fairness_metric import FairnessMetricFactory
from .compatibility_metric import CompatibilityMetricFactory
from .choice_scorer import ChoiceScorerFactory
from scruf.util import get_value_from_keys
from scruf.util.errors import ConfigKeyMissingError, ConfigNoAgentsError
from scruf.util import ResultList
import scruf
from icecream import ic

class FairnessAgent:

    def __init__(self, name):
        self.name = name
        self.fairness_metric = None
        self.compatibility_metric = None
        self.choice_scorer = None

    def setup(self, properties):
        # Set up fairness metric
        fairness_metric_name = properties['metric_class']
        self.fairness_metric = FairnessMetricFactory.create_fairness_metric(fairness_metric_name)

        if 'metric' in properties:
            self.fairness_metric.setup(properties['metric'])
        else:
            self.fairness_metric.setup(dict())
        self.fairness_metric.set_agent(self)

        # Set up compatibility metric
        compatibility_metric_name = properties['compatibility_class']
        self.compatibility_metric = CompatibilityMetricFactory.create_compatibility_metric(compatibility_metric_name)

        if 'compatibility' in properties: #If the metric key is present in the properties dictionary, the setup() method of the fairness metric object is called with the value of the metric key as the parameter. Does the metric key have multiple values?
            self.compatibility_metric.setup(properties['compatibility'])
        else:
            self.compatibility_metric.setup(dict())
        self.compatibility_metric.set_agent(self)

        # Set up choice scorer
        choice_scorer_name = properties['choice_scorer_class']
        self.choice_scorer = ChoiceScorerFactory.create_choice_scorer(choice_scorer_name)

        if 'scorer' in properties:
            self.choice_scorer.setup(properties['scorer'])
        else:
            self.choice_scorer.setup(dict())

class AgentCollection:

    @classmethod
    def check_config(cls, config=None):
        if config is None:
            agents = scruf.Scruf.get_value_from_keys(['agent'])
        else:
            agents = get_value_from_keys(['agent'], config)
        if len(agents) == 0:
            raise ConfigNoAgentsError()

    def __init__(self):
        self.agents = []
        self.history = None

    def agent_names(self):
        return [agent.name for agent in self.agents]

    def agent_value_pairs(self, default=0.0):
        return {name:default for name in self.agent_names()}

    # Note: Overwrites the agent list
    def setup(self, config=None):

        AgentCollection.check_config(config)

        agent_coll_config = config['agent']

        agent_list = []

        for agent_key in agent_coll_config.keys():
            agent_config = agent_coll_config[agent_key]
            agent = FairnessAgent(agent_config['name'])
            agent.setup(agent_config)
            agent_list.append(agent)

        self.agents = agent_list

    def compute_fairness(self, history):
        return {agent.name: agent.fairness_metric.compute_fairness(history) \
                    for agent in self.agents}

    def compute_compatibility(self, context):
        return {agent.name: agent.compatibility_metric.compute_compatibility(context) \
                    for agent in self.agents}

    def score_items(self, rec_list: ResultList, list_size):
        pass

    # TODO: Also some function for use in the choice phase