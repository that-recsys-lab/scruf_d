import unittest
import toml
import random
import scruf
from icecream import ic

from scruf.agent import AgentCollection, BinaryPreferenceFunction
from scruf.allocation import AllocationMechanismFactory, WeightedProductAllocationMechanism, \
    MostCompatibleAllocationMechanism, LeastFairAllocationMechanism, StaticAllocationLottery

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
preference_function_class = "binary_preference"

[agent.low_compat.preference]
feature = "foo"
delta = 0.5

[agent.high_compat]
name = "High Compatibility"
metric_class = "always_one"
compatibility_class = "always_one"
preference_function_class = "binary_preference"

[agent.high_compat.preference]
feature = "bar"
delta = 0.5
'''

SAMPLE_LOTTERY_PROPERTIES = '''
[allocation]
algorithm = "static_lottery"
[allocation.properties]
weights = [["Agent 1", "0.5"], ["Agent 2", "0.2"]]
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
        agents.setup(config)

        scruf.Scruf.state = scruf.Scruf.ScrufState(None)
        scruf.Scruf.state.rand = random.Random(20220223)

        alloc1 = MostCompatibleAllocationMechanism()
        alloc1.setup({})

        alloc_result = alloc1.compute_allocation_probabilities(agents, None, None)
        probs1 = alloc_result['output']

        self.assertEqual(probs1['Low Compatibility'], 0.0)
        self.assertEqual(probs1['High Compatibility'], 1.0)

        alloc2 = LeastFairAllocationMechanism()
        alloc2.setup({})

        alloc_result = alloc2.compute_allocation_probabilities(agents, None, None)
        probs2 = alloc_result['output']

        self.assertEqual(probs2['Low Compatibility'], 1.0)
        self.assertEqual(probs2['High Compatibility'], 0.0)

    def test_static_lottery(self):
        config = toml.loads(SAMPLE_LOTTERY_PROPERTIES)
        alg_name = config['allocation']['algorithm']
        alloc = AllocationMechanismFactory.create_allocation_mechanism(alg_name)
        alloc.setup(config['allocation']['properties'])
        lottery = alloc.lottery
        self.assertEqual(lottery['Agent 1'], 0.5)
        self.assertEqual(lottery['Agent 2'], 0.2)
        self.assertAlmostEqual(lottery['__dummy__'], 0.3)

