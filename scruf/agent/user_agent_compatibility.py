from . import CompatibilityMetric, CompatibilityMetricFactory

#need explanation of what this does?
class UserAgentCompatibilityMetric(CompatibilityMetric):
    """
    A UserAgentCompatibilityMetric is a metric where users are associated with the compatibility between a user and
    a fairness agent.
    """

    def __init__(self):
        super().__init__()

    def __str__(self):
        return "UserAgentCompatibilityMetric"

    def compute_fairness(self, history):
        # Calculate the compatibility between the user and the fairness agent
        compatibility = self._calculate_compatibility(history)

        # Return the compatibility as the fairness metric
        return compatibility

    def _calculate_compatibility(self, history):
        """
        Calculates the compatibility between the user and the fairness agent. This can be done using
        any desired method, such as by analyzing the user's preferences or interactions with the
        fairness agent.
        """
        # Example implementation: return a random value between 0 and 1
        import random
        return random.uniform(0, 1)
