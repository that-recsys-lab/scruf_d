import unittest
import toml
from scruf.agent import FairnessAgent, ProportionalItemFM, AgentCollection, FixedValueChoiceScorer

# This is just the agent part
CONFIG_DOCUMENT = """
[agent]

[agent.country]
name = "Country"
metric_class = "proportional_item"
compatibility_class = "always_one"
choice_scorer_class = "fixed_value"

[agent.country.metric]
feature = "country"
proportion = 0.2

[agent.country.scorer]
protected_feature = "country"
protected_score_value = 0.5

[agent.sector]
name = "Sector"
metric_class = "proportional_item"
compatibility_class = "always_zero"
choice_scorer_class = "fixed_value"

[agent.sector.metric]
feature = "sector"
proportion = 0.5

[agent.sector.scorer]
protected_feature = "sector"
protected_score_value = 0.5
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

    def test_multi_agent_creation(self):
        config = toml.loads(CONFIG_DOCUMENT)
        agent_coll = AgentCollection()
        agent_coll.setup(config)


if __name__ == '__main__':
    unittest.main()
