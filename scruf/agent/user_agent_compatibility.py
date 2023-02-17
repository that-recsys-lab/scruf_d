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

    def compute_compatibility(self, context):
        # Calculate the compatibility between the user and the fairness agent
        compatibility = self.calculate_compatibility(context)

        # Return the compatibility as the fairness metric
        return compatibility

    def calculate_compatibility(self, context):
        """
        Calculates the compatibility between the user and the fairness agent. This can be done using
        any desired method, such as by analyzing the user's preferences or interactions with the
        fairness agent.
        """
        # Example implementation: return a random value between 0 and 1
        import random
        return random.uniform(0, 1)


class ContextCompatibilityMetric(UserAgentCompatibilityMetric):

    def compute_compatibility(self, context):
        return context[self.agent.name]

# Register the metrics created above
metric_specs = [("context_compatibility", ContextCompatibilityMetric)]

CompatibilityMetricFactory.register_compatibility_metrics(metric_specs)


