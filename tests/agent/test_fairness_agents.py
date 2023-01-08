import unittest
import toml
from scruf.agent import FairnessAgent, ProportionalItemFM

# This is just the agent part
CONFIG_DOCUMENT = """
[agent]
[agent.country]
name = "Country"
metric_class = "proportional_item"
compatibility_class = "always_one"
[agent.country.metric]
protected_feature = "country"
protected_values = ["ug", "th", "ke", "ha"]
proportion = 0.2

[agent.sector]
name = "Sector"
metric_class = "list_exposure"
compatibility_class = "always_zero"

[agent.sector.metric]
protected_feature = "sector"
protected_values = [7, 18, 35]
"""

class AgentTestCase(unittest.TestCase):
    def test_agent_creation(self):
        config = toml.loads(CONFIG_DOCUMENT)
        config_agent = config['agent']['country']

        agent = FairnessAgent(config_agent['name'])
        agent.setup(config_agent)
        metric = agent.fairness_metric

        self.assertEqual(metric.__class__, ProportionalItemFM)
        self.assertAlmostEqual(metric.get_property('proportion'), 0.2)


if __name__ == '__main__':
    unittest.main()
