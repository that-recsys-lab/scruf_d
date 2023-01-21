import unittest
import toml
from icecream import ic

from scruf.agent import AgentCollection
from scruf.allocation import AllocationMechanismFactory, WeightedProductAllocationMechanism, \
    MostCompatibleAllocationMechanism, LeastFairAllocationMechanism

SAMPLE_PROPERTIES = '''
[allocation]
algorithm = "weighted_product_allocation"
[allocation.properties]
fairness_exponent = 1.0
compatibility_exponent = 0.7
'''

SAMPLE_AGENTS = '''
[agent]

[agent.low_compat]
name = "Low Compatibility"
metric_class = "always_zero"
compatibility_class = "always_zero"

[agent.high_compat]
name = "High Compatibility"
metric_class = "always_one"
compatibility_class = "always_one"
'''


class AllocationMechanismTestCase(unittest.TestCase):

    def test_mechanism_creation(self):
        config = toml.loads(SAMPLE_PROPERTIES)
        alg_name = config['allocation']['algorithm']
        alloc = AllocationMechanismFactory.create_allocation_mechanism(alg_name)
        alloc.setup(config['allocation']['properties'])

        self.assertEqual(alloc.__class__, WeightedProductAllocationMechanism)
        self.assertAlmostEqual(alloc.get_property('compatibility_exponent'), 0.7)

    def test_mechanism_scoring(self):
        config = toml.loads(SAMPLE_AGENTS)
        agents = AgentCollection()
        agents.setup(config, None)

        alloc1 = MostCompatibleAllocationMechanism()
        alloc1.setup({})

        probs1 = alloc1.compute_allocation_probabilities(agents, None, None)

        self.assertEqual(probs1['Low Compatibility'], 0.0)
        self.assertEqual(probs1['High Compatibility'], 1.0)

        alloc2 = LeastFairAllocationMechanism()
        alloc2.setup({})

        probs2 = alloc2.compute_allocation_probabilities(agents, None, None)

        self.assertEqual(probs2['Low Compatibility'], 1.0)
        self.assertEqual(probs2['High Compatibility'], 0.0)

