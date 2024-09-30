import unittest
import toml
from scruf.agent import FairnessAgent, ProportionalItemFM, AgentCollection, BinaryPreferenceFunction
from icecream import ic

# This is just the agent part
CONFIG_DOCUMENT = """
[agent]

[agent.country]
name = "Country"
metric_class = "proportional_item"
compatibility_class = "always_one"
preference_function_class = "binary_preference"

[agent.country.metric]
feature = "country"
proportion = 0.2

[agent.country.preference]
feature = "country"
delta = 0.5

[agent.sector]
name = "Sector"
metric_class = "proportional_item"
compatibility_class = "always_zero"
preference_function_class = "binary_preference"

[agent.sector.metric]
feature = "sector"
proportion = 0.5

[agent.sector.preference]
feature = "sector"
delta = 0.5
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

        self.assertEqual(len(agent_coll.agent_names()), 2)
    
    def test_agent_value_pairs(self):
        config = toml.loads(CONFIG_DOCUMENT)
        agent_coll = AgentCollection()
        agent_coll.setup(config)
        prs = agent_coll.agent_value_pairs()

        self.assertTrue(all(map(lambda x: x == 0, prs.values())))
        self.assertIn("Country", prs.keys())


if __name__ == '__main__':
    unittest.main()
