from abc import ABC, abstractmethod

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

