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

    def compute_fairness(self, context):
        # Calculate the compatibility between the user and the fairness agent
        compatibility = self._calculate_compatibility(context)

        # Return the compatibility as the fairness metric
        return compatibility

    def _calculate_compatibility(self, context):
        """
        Calculates the compatibility between the user and the fairness agent. This can be done using
        any desired method, such as by analyzing the user's preferences or interactions with the
        fairness agent.
        """
        # Example implementation: return a random value between 0 and 1
        import random
        return random.uniform(0, 1)

# TODO: PrecomputedCompatibiltyMetric
# The configuration would specify a file and then the compatibility information would be loaded
# from the file. _calculate_compatibility would just do a lookup.
# Configuration would be something like:
# [agent.sector]
# name = "Sector"
# metric_class = "list_exposure"
# compatibility_class = "always_zero"
#
# [agent.sector.metric]
# protected_feature = "sector"
# protected_values = [7, 18, 35]
# [agent.sector.compatibility]
# file = "sector_compatibility.csv"
