from abc import ABC, abstractmethod
from scruf.util import PropertyMismatchError

class AllocationMechanism(ABC):
    """
    An AllocationMechanism computes allocation probabilities for a
    collection of FairnessAgents based on their fairness and compatibility scores. All mechanisms are
    initialized with a dictionary of property name, value pairs. Each subclass has to specify the
    property names that it expects.
    """

    def __init__(self):
        self.property_names = []
        self.properties = {}
        self.fairness_metric = None
        self.compatibility_metric = None

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

    def setup(self, input_properties: dict, fairness_metric, compatibility_metric):
        """
        Checks the properties provided with those expected by the object, sets up the fairness
        and compatibility metrics, and stores them as instance variables.
        :param input_properties:
        :param fairness_metric: an instance of a FairnessMetric
        :param compatibility_metric: an instance of a CompatibilityMetric
        :return:
        """
        self.setup_property_names()

        self.properties = {}
        input_property_names = input_properties.keys()

        self._check_properties(self.property_names, input_property_names)

        for key in input_property_names:
            self.properties[key] = input_properties[key]

        self.fairness_metric = fairness_metric
        self.compatibility_metric = compatibility_metric

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
    def compute_allocation_probabilities(self, agents, history):
        pass
    
    class RandomAllocationMechanism(AllocationMechanism):
        
        def compute_allocation_probabilities(self, agents, history):
            """
            Computes the allocation probabilities for a collection of FairnessAgents based on their fairness
            and compatibility scores, and normalizes the values to ensure that they sum to 1.
            :param agents: a list of FairnessAgent objects
            :param history: a system History object
            :return: a dictionary mapping agent names to allocation probabilities
            """
            # Compute the fairness and compatibility scores for each agent
            scores = {}
            for agent in agents:
                fairness_score = self.fairness_metric.compute_fairness(history)
                compatibility_score = self.compatibility_metric.compute_compatibility(history)
                scores[agent.name] = 1 - (fairness_score * compatibility_score)

            # Normalize the scores to sum to 1
            total_score = sum(scores.values())
            normalized_scores = {k: v / total_score for k, v in scores.items()}
            return normalized_scores

    class LeastFair(AllocationMechanism):
        """
        The LeastFair allocation mechanism allocates to the agent with the lowest fairness score.
        """

        def compute_allocation_probabilities(self, agents, history):
            # Compute the fairness scores for each agent
            for agent in agents:
                fairness_score = self.fairness_metric.compute_fairness(history)
                agent.fairness_score = fairness_score
            allocation_probabilities = [0] * len(agents)  # Initialize probabilities to 0 for all agents
            if agents:  # If there are agents
                # Find the index of the agent with the lowest fairness score
                min_index = min(range(len(agents)), key=lambda i: agents[i].fairness_score)
                allocation_probabilities[min_index] = 1  # Allocate 1 to the agent with the lowest fairness score
            return allocation_probabilities

class MostCompatible(AllocationMechanism):
    """
    The MostCompatible allocation mechanism allocates to the agent with the highest compatibility score.
    """

    def __init__(self, compatibility_metric):
        """
        Initializes the MostCompatible allocation mechanism with a compatibility metric.
        
        Parameters:
        - compatibility_metric: An instance of a CompatibilityMetric class that is used to compute the compatibility scores of the agents.
        """
        self.compatibility_metric = compatibility_metric

    def compute_allocation_probabilities(self, agents, history):
        """
        Computes the allocation probabilities for the agents based on their compatibility scores.
        
        Parameters:
        - agents: A list of Agent objects.
        - history: A list of past allocations.
        
        Returns:
        A list of allocation probabilities for the agents.
        """
        allocation_probabilities = [0] * len(agents)  # Initialize probabilities to 0 for all agents
        if agents:  # If there are agents
            # Compute the compatibility scores for each agent
            for agent in agents:
                compatibility_score = self.compatibility_metric.compute_compatibility(history)
                agent.compatibility_score = compatibility_score  # Update the compatibility score of the agent
            # Find the index of the agent with the highest compatibility score
            max_index = max(range(len(agents)), key=lambda i: agents[i].compatibility_score)
            allocation_probabilities[max_index] = 1  # Allocate 1 to the agent with the highest compatibility score
        return allocation_probabilities

    class AllocationMechanismFactory:
        """
        A factory class for creating AllocationMechanism objects.
        """

        _allocation_mechanism = {}

        @classmethod
        def register_allocation_mechanism(cls, mechanism_type, mechanism_class):
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


            

